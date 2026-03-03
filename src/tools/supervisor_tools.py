from utils.models import UiPage
from typing import List
from utils.helpers import calculate_accessibility_complexity,calculate_ui_source_complexity,analyze_screenshot_complexity


def analyze_ui_complexity(ui_pages : List[UiPage]) :
    results=[]
    for page in ui_pages :
        a11y_score=calculate_accessibility_complexity(page.accessibility_tree)
        source_code_score= calculate_ui_source_complexity(page.code)
        screenshots_score= analyze_screenshot_complexity(page.)
        
    
    
    return 


