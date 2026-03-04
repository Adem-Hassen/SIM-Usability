from utils.models import UiPage
from typing import List,Dict, Annotated
from langchain.tools import tool
from utils.helpers import calculate_accessibility_complexity,calculate_ui_source_complexity,analyze_screenshot_complexity
import asyncio

from agents.personas_generator import generate_personas_for_page

@tool
def analyze_ui_complexity(ui_pages : List[UiPage]) :
    results=[]
    for page in ui_pages :
        a11y_score=calculate_accessibility_complexity(page.accessibility_tree)
        source_code_score= calculate_ui_source_complexity(page.code)
        if page.screenshots:
         
         screenshots_score= analyze_screenshot_complexity(page.screenshots,[page.name for i in range(len(page.screenshots))])
        else :
         screenshots_score=0
        
        overall_score=(a11y_score+source_code_score+screenshots_score)/3
        results.append({"page_name":page.name, "a11y_score":a11y_score,"source_code_score":source_code_score,"screenshots_score":screenshots_score,"overall_score":overall_score})
        
    return results






@tool
async def generate_user_personas_tool(
    pages_complexity: 
        List[Dict],
    ui_context:str, 
    ) :
    
    if not pages_complexity:
        raise ValueError("pages_complexity cannot be empty")
    
    if not ui_context or not ui_context.strip():
        raise ValueError("ui_context must be provided and non-empty")
    
 
    # ========================================================================
    # LLM INITIALIZATION
    # ========================================================================
    
    # Initialize LLM for persona generation
    # Use supervisor's model (typically more capable than user agent model)
    # Temperature 0.7 allows some creativity for diverse personas and tasks
    llm = ChatOpenAI(
        model=settings.supervisor_model,  # e.g., "gpt-4o-mini"
        temperature=0.7  # Balance between creativity and consistency
    )
    
    # ========================================================================
    # PARALLEL PERSONA GENERATION
    # ========================================================================
    
    # Create async tasks for each page
    # Processing in parallel significantly speeds up multi-page generation
    # Example: 5 pages × 3 seconds each = 15s sequential vs 3s parallel
    generation_tasks = [
        generate_personas_for_page(page_data, ui_context, llm)
        for page_data in pages_complexity
    ]
    
    # Execute all tasks in parallel and wait for completion
    # If one fails, others continue (asyncio.gather doesn't fail-fast by default)
    agent_clusters = await asyncio.gather(*generation_tasks)
    
    # ========================================================================
    # AGGREGATE RESULTS
    # ========================================================================
    
    # Calculate total agents across all pages
    total_agents = sum(cluster["agent_count"] for cluster in agent_clusters)
    
    # Create human-readable summary
    # Format: "page1 (N agents), page2 (M agents), ..."
    pages_summary = ", ".join([
        f"{cluster['page_name']} ({cluster['agent_count']} agents)"
        for cluster in agent_clusters
    ])
    
    generation_summary = (
        f"Generated {total_agents} agents across {len(agent_clusters)} pages: "
        f"{pages_summary}"
    )
    
    
    # ========================================================================
    # RETURN STRUCTURED RESULT
    # ========================================================================
    
    return {
        "agent_clusters": agent_clusters,
        "total_agents": total_agents,
        "pages_processed": len(agent_clusters),
        "generation_summary": generation_summary
    }  