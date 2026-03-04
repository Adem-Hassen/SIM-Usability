from utils.models import UiPage
from typing import List
from langchain.tools import tool
from utils.helpers import calculate_accessibility_complexity,calculate_ui_source_complexity,analyze_screenshot_complexity



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






   