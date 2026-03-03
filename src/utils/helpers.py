from typing import Dict
from bs4 import BeautifulSoup
import base64
import json
import re
import os
from dotenv  import load_dotenv
from google.genai import types
from google import genai
from typing import List
import math
from collections import defaultdict

load_dotenv()

api_key=os.getenv("OPENAI_API_KEY")


def calculate_accessibility_complexity(tree : Dict):
    stats = {
        "interactive_count": 0,
        "interactive_roles": defaultdict(int),
        "form_fields": 0,
        "form_buttons": 0,
        "nav_links": 0,
        "nav_depth": 0,
        "navigation_nodes": 0,
        "control_types": set()
    }

    FORM_ROLES = {"textbox", "checkbox", "radio", "combobox", "searchbox"}
    CONTROL_ROLES = {"button", "link", "textbox", "checkbox", "radio", "combobox"}
    
    def traverse(node, depth=0, inside_nav=False):
        role = node.get("role", "")
        actions = node.get("actions", [])
        focusable = node.get("focusable", False)
        children = node.get("children", [])

        # ---- Interactive Elements ----
        if focusable or actions:
            stats["interactive_count"] += 1
            stats["interactive_roles"][role] += 1

        # ---- Control Diversity ----
        if role in CONTROL_ROLES:
            stats["control_types"].add(role)

        # ---- Form Complexity ----
        if role in FORM_ROLES:
            stats["form_fields"] += 1

        if role == "button":
            stats["form_buttons"] += 1

        # ---- Navigation Complexity ----
        if role == "navigation":
            stats["navigation_nodes"] += 1
            inside_nav = True

        if inside_nav and role == "link":
            stats["nav_links"] += 1
            stats["nav_depth"] = max(stats["nav_depth"], depth)

        for child in children:
            traverse(child, depth + 1, inside_nav)

    traverse(tree)


    interactive_score = stats["interactive_count"] * 2

    total = sum(stats["interactive_roles"].values())
    entropy = 0
    if total > 0:
        for count in stats["interactive_roles"].values():
            p = count / total
            entropy -= p * math.log2(p)
    distribution_score = entropy * 5

    form_score = (stats["form_fields"] * 3) + (stats["form_buttons"] * 1.5)

    navigation_score = (
        stats["nav_links"] * 2 +
        stats["navigation_nodes"] * 3 +
        stats["nav_depth"] * 1.5
    )

    diversity_score = len(stats["control_types"]) * 4
    MAX_SCORE = 200
    raw_score = (
        interactive_score +
        distribution_score +
        form_score +
        navigation_score +
        diversity_score
    )
    normalized_score = (raw_score / MAX_SCORE) * 5
    complexity_score = round(min(5,normalized_score), 2)

    return {
        "complexity_score": complexity_score,
    }





def calculate_ui_source_complexity(html_source: str):
    soup = BeautifulSoup(html_source, "html.parser")

   
    def get_max_depth(element, depth=0):
        if not hasattr(element, "children"):
            return depth
        depths = [depth]
        for child in element.children:
            if child.name is not None:
                depths.append(get_max_depth(child, depth + 1))
        return max(depths)

    dom_depth = get_max_depth(soup)

    
    semantic_tags = ["header", "nav", "main", "section", "article", "aside", "footer"]
    semantic_count = sum(len(soup.find_all(tag)) for tag in semantic_tags)

    hidden_elements = 0
    for el in soup.find_all(True):
        if (
            el.has_attr("hidden") or
            el.get("aria-hidden") == "true" or
            "display:none" in (el.get("style") or "") or
            "hidden" in (el.get("class") or [])
        ):
            hidden_elements += 1

  
    component_keywords = ["card", "modal", "dropdown", "accordion",
                          "carousel", "sidebar", "tabs"]

    component_count = 0
    for el in soup.find_all(True):
        classes = " ".join(el.get("class", []))
        for keyword in component_keywords:
            if keyword in classes.lower():
                component_count += 1
                break


    forms = soup.find_all("form")
    form_count = len(forms)

    input_count = len(soup.find_all(["input", "textarea", "select"]))
    fieldsets = len(soup.find_all("fieldset"))
    form_buttons = len([btn for btn in soup.find_all("button") if btn.find_parent("form")])

    form_complexity = (
        form_count * 10 +
        input_count * 3 +
        fieldsets * 5 +
        form_buttons * 2
    )

    all_elements = soup.find_all(True)
    total_nodes = len(all_elements)

    text_length = len(soup.get_text(strip=True))
    content_density = text_length / (total_nodes + 1)

    raw_score = (
        dom_depth * 4 +
        semantic_count * 3 +
        hidden_elements * 2 +
        component_count * 5 +
        form_complexity +
        min(content_density, 50)  
    )

    raw_score = min(raw_score, 200)

 

    normalized_score = round((raw_score / 200) * 5, 2)

    return {
        "complexity_score": normalized_score,
    
    }








def encode_image(image_path):
    with open(image_path, "rb") as img:
        return base64.b64encode(img.read()).decode("utf-8")






def analyze_multiple_screenshots_complexity(
    screenshots: List[bytes],
    page_names: List[str] = None
) -> dict:

    # Validate inputs
    if not screenshots:
        raise ValueError("No screenshots provided")
    
    if len(screenshots) > 5:
        raise ValueError("Maximum 5 screenshots supported")
    
    # Generate default names if not provided
    if page_names is None:
        page_names = [f"page_{i+1}" for i in range(len(screenshots))]
    
    if len(page_names) != len(screenshots):
        raise ValueError("Number of page names must match number of screenshots")
    
    # Initialize client
    client = genai.Client(api_key=api_key)
    
    # Build the prompt
    prompt = build_multi_page_prompt(page_names)
    
    # Prepare content parts
    content_parts = [prompt]
    
    # Add each screenshot with a label
    for i, (screenshot_bytes, page_name) in enumerate(zip(screenshots, page_names)):
        # Add a text separator
        content_parts.append(f"\n--- Screenshot {i+1}: {page_name} ---\n")
        
        # Add the image
        content_parts.append(
            types.Part.from_bytes(
                data=screenshot_bytes,
                mime_type="image/png"
            )
        )
    
    # Call VLM
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",  
            contents=content_parts
        )
        
        # Clean response
        cleaned = re.sub(r'```(?:json)?\s*|\s*```', '', response.text)
        cleaned = cleaned.strip()
        
        # Parse JSON
        result = json.loads(cleaned)
        
        # Validate response structure
        if "pages" not in result:
            raise ValueError("VLM response missing 'pages' key")
        
        # Calculate per-page normalized scores
        per_page_scores = []
        for page_data in result["pages"]:
            total_score = page_data.get("total_score", 0)
            # Normalize: (total / 60) * 10 to get 0-10 scale
            normalized = round((total_score / 60) * 5, 2)
            page_data["normalized_score"] = normalized
            per_page_scores.append(page_data)
        
        # Calculate overall score (average of normalized scores)
        if per_page_scores:
            overall_normalized = round(
                sum(p["normalized_score"] for p in per_page_scores) / len(per_page_scores),
                2
            )
        else:
            overall_normalized = 5.0  # Default mid-range
        
        # Find most and least complex pages
        most_complex = max(per_page_scores, key=lambda x: x["normalized_score"])
        least_complex = min(per_page_scores, key=lambda x: x["normalized_score"])
        
        return {
            "per_page_scores": per_page_scores,
            "overall_normalized_score": overall_normalized,
            "aggregation_method": "average",
            "page_count": len(screenshots),
            "complexity_range": {
                "min": least_complex["normalized_score"],
                "max": most_complex["normalized_score"],
                "spread": most_complex["normalized_score"] - least_complex["normalized_score"]
            },
            "most_complex_page": most_complex["page_name"],
            "least_complex_page": least_complex["page_name"]
        }
    
    except json.JSONDecodeError as e:
        # Fallback on parsing error
        return {
            "error": "Failed to parse VLM response",
            "details": str(e),
            "raw_response": response.text if 'response' in locals() else None,
            "overall_normalized_score": 5.0,
            "per_page_scores": []
        }
    
    except Exception as e:
        # Fallback on any error
        return {
            "error": "VLM request failed",
            "details": str(e),
            "overall_normalized_score": 5.0,
            "per_page_scores": []
        }


def build_multi_page_prompt(page_names: List[str]) -> str:
    """
    Build the VLM prompt for multi-page analysis.
    """
    
    pages_list = "\n".join([f"  - {name}" for name in page_names])
    
    prompt = f"""
You are a UI/UX expert analyzing visual complexity of multiple user interface pages.

You will receive {len(page_names)} screenshots labeled as follows:
{pages_list}

Your task: Analyze EACH screenshot separately from a VISUAL perspective. 
Focus on what a user SEES and PERCEIVES.

For EACH page, rate these 6 visual dimensions on a scale of 0-10:

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. VISUAL DENSITY (0-10)
   0-2:  Minimal content, lots of white space
   3-4:  Light content, comfortable spacing
   5-6:  Moderate density, balanced
   7-8:  Dense content, limited white space
   9-10: Very crowded, overwhelming

2. COLOR COMPLEXITY (0-10)
   0-2:  Monochrome or 1-2 colors
   3-4:  Limited palette (3-4 colors)
   5-6:  Moderate variety (5-6 colors)
   7-8:  Many colors (7-10)
   9-10: Very colorful (10+)

3. LAYOUT CLARITY (0-10, INVERTED: lower = better)
   0-2:  Crystal clear organization
   3-4:  Clear structure
   5-6:  Moderately clear
   7-8:  Somewhat unclear
   9-10: Chaotic

4. VISUAL HIERARCHY (0-10, INVERTED: lower = better)
   0-2:  Extremely clear focal points
   3-4:  Clear focal points
   5-6:  Somewhat clear
   7-8:  Difficult to identify important elements
   9-10: No hierarchy

5. INFORMATION DENSITY (0-10)
   0-2:  Minimal information
   3-4:  Light information load
   5-6:  Moderate information
   7-8:  Heavy information
   9-10: Information overload

6. COGNITIVE LOAD (0-10)
   0-2:  Very simple, instantly understandable
   3-4:  Simple, easy to grasp
   5-6:  Moderate, requires attention
   7-8:  Complex, requires focus
   9-10: Overwhelming, intimidating

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

IMPORTANT INSTRUCTIONS:
- Analyze each page independently
- Be consistent in your scoring across pages
- Layout clarity and visual hierarchy are INVERTED (lower score = better)
- Consider first impressions (0-3 second glance)

RESPONSE FORMAT:
Return ONLY valid JSON (no markdown, no code fences) with this structure:

{{
  "pages": [
    {{
      "page_name": "{page_names[0]}",
      "visual_density": <0-10>,
      "color_complexity": <0-10>,
      "layout_clarity": <0-10>,
      "visual_hierarchy": <0-10>,
      "information_density": <0-10>,
      "cognitive_load": <0-10>,
      "total_score": <sum of all 6>,
      "reasoning": "<brief explanation>"
    }},
    ... (one object per page)
  ],
  "overall_assessment": "<1-2 sentences about the overall UI complexity across all pages>"
}}

CRITICAL: 
- Return raw JSON only
- No markdown code fences
- No ```json or ```
- Start with {{ and end with }}

Your JSON response:
"""
    
    return prompt




images=[]
names=[]
for i in range(0,3) : 
    images.append(encode_image("examples/sample_ui/test.png")
)
    names.append(i)

print(analyze_multiple_screenshots_complexity(images,names))