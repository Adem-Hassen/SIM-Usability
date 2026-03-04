

from typing import List, Dict
from agents.personas_templates import PERSONA_TEMPLATES


def build_persona_selection_prompt(
    ui_context: str,
    page_name: str,
    complexity_score: float,
    recommended_agents: int,
    available_types: List[str]
) -> str:
   
    types_description = "\n".join([
        f"{i+1}. {ptype} - {PERSONA_TEMPLATES[ptype]['description'][:80]}..."
        for i, ptype in enumerate(available_types)
    ])
    
    # Join complexity factors into readable list
 
    
    prompt = f"""You are a UX testing expert selecting user personas for comprehensive UI testing.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

UI CONTEXT (what this system is for):
{ui_context}

PAGE BEING TESTED:
Name: {page_name}
Complexity: {complexity_score}/5.0

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

AVAILABLE PERSONA TYPES:
{types_description}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

YOUR TASK:
Select exactly {recommended_agents} persona types that would provide the MOST VALUABLE testing coverage for this specific UI.

SELECTION CRITERIA:
1. Relevance: Who would ACTUALLY use this system? (based on UI context)
2. Coverage: Which personas would reveal the most diverse set of issues?
3. Priority: Always include at least one novice persona (test learnability)
4. Context-fit: Don't select personas that don't match the use case
   Example: Don't pick "mobile_user" for desktop-only enterprise software
   Example: Don't pick "senior" for a gaming platform targeting youth

IMPORTANT:
- Base selection heavily on the UI CONTEXT
- Consider the complexity level (higher = more diverse personas needed)
- Ensure diversity across technical levels

Respond with ONLY valid JSON (no markdown, no code fences):
{{
  "selected_personas": ["type1", "type2", "type3", ...],
  "reasoning": "Brief 1-sentence explanation of selection rationale"
}}

Your JSON response:
"""
    
    return prompt


def build_task_generation_prompt(
    ui_context: str,
    page_name: str,
    persona_type: str,
    persona_description: str,
    sample_elements: List[Dict]
) -> str:
    
    if sample_elements:
        elements_text = "\n".join([
            f"  - {el.get('role', 'element')}: \"{el.get('name', 'unnamed')}\""
            for el in sample_elements[:12]
        ])
    else:
        elements_text = "  (No element information available)"
    
    # Join complexity factors
    
    prompt = f"""Generate a realistic, goal-oriented task for UI testing.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

UI CONTEXT:
{ui_context}

PAGE: {page_name}

PERSONA TYPE: {persona_type}
Description: {persona_description}

SAMPLE ELEMENTS ON PAGE:
{elements_text}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

TASK REQUIREMENTS:

1. REALISTIC: Based on UI context, what would this user actually try to do?

2. GOAL-ORIENTED: State WHAT to accomplish, not HOW
   ✓ Good: "Find your order history"
   ✗ Bad: "Click the Orders tab, then scroll to Recent"

3. PERSONA-APPROPRIATE: Match skill level and behavior
   - novice: Simple, common first-time tasks
   - intermediate: Standard everyday tasks
   - expert: Efficient, advanced workflows
   - accessibility_user: Tasks requiring keyboard/screen reader
   - mobile_user: Tasks natural on mobile device
   - senior: Tasks testing clarity and simplicity
   - impatient: Tasks testing speed and efficiency
   - international: Tasks testing universal understanding

4. TESTABLE: Clear success criteria (either done or not done)

5. SPECIFIC: Reference actual UI purpose, not generic actions

6. BRIEF: Maximum 15 words

EXAMPLES:
- E-commerce novice: "Add a book to your cart"
- Dashboard expert: "Export this week's sales report"
- Medical portal accessibility: "Find patient allergies using only keyboard"
- Banking senior: "Check your account balance"

Generate ONLY the task text (no JSON, no quotes, no explanation):
"""
    
    return prompt

