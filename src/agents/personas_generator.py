

import json
import re
from typing import List, Dict

from agents.personas_templates import PERSONA_TEMPLATES, list_available_persona_types
from agents.personas_prompts import (
    build_persona_selection_prompt,
    build_task_generation_prompt
)



async def generate_personas_for_page(
    page_data: Dict,
    ui_context: str,
    llm
) -> Dict:
    
    page_name = page_data["name"]
    complexity_score = page_data["overall_score"]
    
    
    available_types = list_available_persona_types()
    
    selection_prompt = build_persona_selection_prompt(
        ui_context=ui_context,
        page_name=page_name,
        complexity_score=complexity_score,
        available_types=available_types
    )
    
    try:
        selection_response = await llm.ainvoke(selection_prompt)
        
        # Clean response (remove markdown code fences if present)
        cleaned = re.sub(
            r'```(?:json)?\s*|\s*```', 
            '', 
            selection_response.content
        ).strip()
        
        # Parse JSON response
        selection_data = json.loads(cleaned)
        selected_types = selection_data["selected_personas"]
        selection_reasoning = selection_data.get("reasoning", "")
        
        
    except Exception as e:
        # If LLM call fails, use fallback selection
        selected_types = get_fallback_persona_types(recommended_agents)
        selection_reasoning = "Fallback selection due to LLM error"
    
    # ========================================================================
    # STEP 2: Generate Task for Each Persona
    # ========================================================================
    
    personas = []
    
    # Iterate through selected persona types
    # Limit to recommended_agents in case LLM selected too many
    for persona_type in selected_types[:recommended_agents]:
        
        # Get the template for this persona type
        template = PERSONA_TEMPLATES.get(persona_type)
        
        if not template:
            logger.warning(f"Unknown persona type: {persona_type}, skipping")
            continue
        
        # Build task generation prompt
        task_prompt = build_task_generation_prompt(
            ui_context=ui_context,
            page_name=page_name,
            persona_type=persona_type,
            persona_description=template["description"],
            complexity_factors=complexity_factors,
            sample_elements=elements
        )
        
        # Call LLM to generate task
        try:
            task_response = await llm.ainvoke(task_prompt)
            
            # Clean the task text (remove quotes and extra whitespace)
            task = task_response.content.strip().strip('"\'')
            
            # Validate task isn't too long (safety check)
            # Truncate if needed (LLM should follow 15-word limit but sometimes doesn't)
            if len(task.split()) > 20:
                task = " ".join(task.split()[:20]) + "..."
                
        except Exception as e:
            # If task generation fails, use generic fallback
            task = f"Complete the main task on {page_name}"
        
        # ========================================================================
        # STEP 3: Assemble Complete Persona Object
        # ========================================================================
        
        persona = {
            "name": template["name"],
            "type": persona_type,
            "description": template["description"],
            "technical_level": template["technical_level"],
            "task": task,
            "behavioral_traits": template["characteristics"],
            "accessibility_needs": template.get("accessibility_needs", []),
            "page_name": page_name
        }
        
        personas.append(persona)
        
    
    # ========================================================================
    # STEP 4: Create Final Cluster Object
    # ========================================================================
    
    cluster = {
        "page_name": page_name,
        "complexity_score": complexity_score,
        "agent_count": len(personas),
        "personas": personas,
        "selection_reasoning": selection_reasoning
    }
    

    
    return cluster


def get_fallback_persona_types(count: int) -> List[str]:
    """
    Get fallback persona types when LLM selection fails.
    
    This function provides a reasonable default ordering of persona types
    based on general testing priorities. It ensures the most important
    personas (novice, expert) are always included first.
    
    The priority order reflects:
    - Novice: Test learnability (always most important)
    - Expert: Test efficiency (second most important)
    - Intermediate: Standard users
    - Accessibility: Compliance and inclusion
    - Mobile: Device coverage
    - Senior: Age diversity
    - Impatient: Speed testing
    - International: Global users
    
    Args:
        count: How many persona types to return
    
    Returns:
        list: Persona type identifiers in priority order, limited to count
    
    Example:
        >>> types = get_fallback_persona_types(3)
        >>> print(types)
        ['novice', 'expert', 'intermediate']
    """
    
    priority_order = [
        "novice",           # Always test for beginners
        "expert",           # Always test for power users
        "intermediate",     # Standard user
        "accessibility_user",  # Compliance
        "mobile_user",      # Mobile coverage
        "senior",           # Older users
        "impatient",        # Speed-focused
        "international"     # Global users
    ]
    
    # Return only the number requested
    return priority_order[:count]