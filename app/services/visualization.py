import json

def hierarchy_to_mermaid(hierarchy_json: dict) -> str:
    """
    Convert document hierarchy JSON into Mermaid.js graph format.
    Example hierarchy_json:
    {
        "title": "Document",
        "sections": [
            {"heading": "Introduction", "subsections": []},
            {"heading": "Methods", "subsections": [
                {"heading": "Data Collection", "subsections": []}
            ]}
        ]
    }
    """
    mermaid = ["graph TD"]
    node_counter = 0
    node_map = {}

    def add_node(text):
        nonlocal node_counter
        node_id = f"N{node_counter}"
        node_counter += 1
        node_map[text] = node_id
        mermaid.append(f'{node_id}["{text}"]')
        return node_id

    def process_section(section, parent_id=None):
        node_id = add_node(section["heading"])
        if parent_id:
            mermaid.append(f"{parent_id} --> {node_id}")
        for sub in section.get("subsections", []):
            process_section(sub, node_id)

    root_id = add_node(hierarchy_json["title"])
    for section in hierarchy_json.get("sections", []):
        process_section(section, root_id)

    return "\n".join(mermaid)
