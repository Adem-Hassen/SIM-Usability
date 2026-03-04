
PERSONA_TEMPLATES = {
    "novice": {
        "name": "Novice User",
        "description": "First-time user with limited technical knowledge. Expects clear guidance and simple workflows.",
        "technical_level": "novice",
        "characteristics": [
            "Reads all instructions carefully",
            "Hesitates before clicking unfamiliar elements",
            "Looks for help text and tooltips",
            "Prefers obvious, clearly labeled buttons",
            "Gets confused by technical jargon",
            "May give up if task seems too complex"
        ],
        "accessibility_needs": []
    },
    
    "intermediate": {
        "name": "Intermediate User",
        "description": "Regular user comfortable with standard web interfaces. Can navigate typical patterns but may struggle with advanced features.",
        "technical_level": "intermediate",
        "characteristics": [
            "Familiar with common UI patterns",
            "Scans pages quickly for relevant elements",
            "Uses some keyboard shortcuts",
            "Expects standard controls in standard places",
            "Can recover from minor errors",
            "Appreciates efficiency but won't hunt for it"
        ],
        "accessibility_needs": []
    },
    
    "expert": {
        "name": "Expert User",
        "description": "Power user with high technical proficiency. Expects efficiency, shortcuts, and advanced features.",
        "technical_level": "expert",
        "characteristics": [
            "Uses keyboard shortcuts extensively",
            "Skips help text and instructions",
            "Expects advanced features and customization",
            "Very fast navigation and decision-making",
            "Frustrated by unnecessary steps or slowness",
            "Looks for most efficient path"
        ],
        "accessibility_needs": []
    },
    
    "mobile_user": {
        "name": "Mobile User",
        "description": "User on mobile device. Expects touch-friendly interface, responsive design, and mobile-optimized workflows.",
        "technical_level": "intermediate",
        "characteristics": [
            "Uses touch gestures (tap, swipe)",
            "Expects large, easy-to-tap targets",
            "Prefers scrolling to multiple clicks",
            "Has limited screen space",
            "May have slower/unreliable connection",
            "Often multitasking or in motion"
        ],
        "accessibility_needs": []
    },
    
    "accessibility_user": {
        "name": "Screen Reader User",
        "description": "User relying on assistive technology. Needs proper ARIA labels, semantic HTML, and keyboard navigation.",
        "technical_level": "intermediate",
        "characteristics": [
            "Navigates by headings and landmarks",
            "Needs descriptive labels for all controls",
            "Relies on alt text for images",
            "Uses tab key for navigation",
            "Expects proper ARIA attributes",
            "Cannot see visual-only cues"
        ],
        "accessibility_needs": ["screen_reader", "keyboard_navigation"]
    },
    
    "senior": {
        "name": "Senior User",
        "description": "Older adult who may need larger text and clearer contrast. Prefers simple, predictable interfaces.",
        "technical_level": "novice",
        "characteristics": [
            "Prefers larger text and UI elements",
            "Needs high contrast for readability",
            "Slower, more deliberate mouse movements",
            "May have vision or motor challenges",
            "Values simplicity and clarity",
            "Uncomfortable with rapid changes or complex flows"
        ],
        "accessibility_needs": []
    },
    
    "impatient": {
        "name": "Impatient User",
        "description": "User in a hurry who wants to complete tasks quickly with minimum steps. Values efficiency above all.",
        "technical_level": "intermediate",
        "characteristics": [
            "Skips instructions and help text",
            "Clicks rapidly, often before reading fully",
            "Expects immediate feedback and response",
            "Frustrated by delays or extra steps",
            "May make mistakes due to rushing",
            "Abandons tasks that seem too slow"
        ],
        "accessibility_needs": []
    },
    
    "international": {
        "name": "International User",
        "description": "User with different language or cultural background. May misunderstand idioms or culture-specific references.",
        "technical_level": "intermediate",
        "characteristics": [
            "May misunderstand local idioms or slang",
            "Expects clear internationalization",
            "Prefers universal icons over text",
            "Uses different date/number formats",
            "May use translation tools",
            "Sensitive to cultural assumptions"
        ],
        "accessibility_needs": []
    }
}


def get_persona_template(persona_type: str) -> dict:
    
    return PERSONA_TEMPLATES.get(persona_type, PERSONA_TEMPLATES["intermediate"])


def list_available_persona_types() -> list:
   
    return list(PERSONA_TEMPLATES.keys())


def get_persona_description_summary() -> str:
  
    summary_lines = []
    for i, (ptype, template) in enumerate(PERSONA_TEMPLATES.items(), 1):
        summary_lines.append(
            f"{i}. {ptype} - {template['description']}"
        )
    return "\n".join(summary_lines)