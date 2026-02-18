from playwright.async_api import async_playwright
from typing import Dict


IGNORED_ROLES = {
    "StaticText",
    "RootWebArea",
    "InlineTextBox",
    "generic",
    "none"
}

# Map accessibility roles → possible actions
ROLE_ACTIONS = {
    "button": ["click"],
    "link": ["click"],
    "textbox": ["type"],
    "searchbox": ["type"],
    "checkbox": ["click", "toggle"],
    "radio": ["click", "select"],
    "combobox": ["select"],
    "menuitem": ["click"],
    "tab": ["click"],
    "option": ["select"],
    "slider": ["drag"],
}


def extract_focusable(node: Dict) -> bool:
    for prop in node.get("properties", []):
        if prop.get("name") == "focusable":
            return prop.get("value", {}).get("value", False)
    return False


def build_semantic_tree(snapshot: Dict) -> Dict:
    """
    Convert raw CDP Accessibility.getFullAXTree output
    into a clean semantic interaction tree.
    """

    raw_nodes = snapshot.get("nodes", [])

    # Step 1: Index nodes by ID
    node_map = {node["nodeId"]: node for node in raw_nodes}

    # Step 2: Prepare clean nodes container
    semantic_nodes = {}

    counter = 0

    for node in raw_nodes:
        if node.get("ignored"):
            continue

        role = node.get("role", {}).get("value")
        name = node.get("name", {}).get("value", "")

        if role in IGNORED_ROLES:
            continue

        counter += 1
        semantic_id = f"node_{counter}"

        semantic_nodes[node["nodeId"]] = {
            "id": semantic_id,
            "role": role,
            "name": name,
            "actions": ROLE_ACTIONS.get(role, []),
            "focusable": extract_focusable(node),
            "children": []
        }

    # Step 3: Rebuild hierarchy
    root = {
        "id": "root",
        "role": "root",
        "children": []
    }

    for node in raw_nodes:
        node_id = node["nodeId"]

        if node_id not in semantic_nodes:
            continue

        parent_id = node.get("parentId")

        if parent_id and parent_id in semantic_nodes:
            semantic_nodes[parent_id]["children"].append(
                semantic_nodes[node_id]
            )
        else:
            # Attach to root if no valid semantic parent
            root["children"].append(semantic_nodes[node_id])

    return root
async def get_a11y_tree(source_code: str)-> Dict:

    async with async_playwright() as p:
        # Launch browser
        browser = await p.chromium.launch()
        
        # Create context with consistent viewport
        context = await browser.new_context(
            viewport={'width': 1280, 'height': 800}
        )
        page = await context.new_page()
        
        try:
        
            await page.set_content(source_code)
            await page.wait_for_timeout(500)
            
            # Determine root eleme
            # Get the comprehensive snapshot
            client = await context.new_cdp_session(page)
            
            snapshot = await client.send("Accessibility.getFullAXTree")
            
            return build_semantic_tree(snapshot) if snapshot  else {}
            
        finally:
            await browser.close()


