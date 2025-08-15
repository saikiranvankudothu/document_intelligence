import json
import hashlib

def hierarchy_to_mermaid(hierarchy_json: dict) -> str:
    """
    Convert document hierarchy JSON into Mermaid.js graph format.
    Handles duplicate section titles by generating unique IDs.
    """
    mermaid = ["graph TD"]

    def make_id(text, path):
        # Create unique ID from path hash
        hash_part = hashlib.md5(path.encode()).hexdigest()[:6]
        return f"N_{hash_part}"

    def add_node(text, path):
        node_id = make_id(text, path)
        safe_text = text.replace('"', '\\"')
        mermaid.append(f'{node_id}["{safe_text}"]')
        return node_id

    def process_section(section, parent_path="", parent_id=None):
        current_path = f"{parent_path}/{section['heading']}"
        node_id = add_node(section["heading"], current_path)
        if parent_id:
            mermaid.append(f"{parent_id} --> {node_id}")
        for idx, sub in enumerate(section.get("subsections", [])):
            process_section(sub, current_path, node_id)

    root_id = add_node(hierarchy_json["title"], hierarchy_json["title"])
    for section in hierarchy_json.get("sections", []):
        process_section(section, hierarchy_json["title"], root_id)

    return "\n".join(mermaid)
