from langchain.tools import tool
from src.utils.models import UiPage
from typing import List,Dict
from bs4 import BeautifulSoup

import math
from collections import defaultdict

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




def analyze_ui_complexity(ui_pages : List[UiPage]) :
    
    
    
    
    return 


