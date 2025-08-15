import re
from typing import List, Dict, Any
from dataclasses import dataclass

# Heuristics for headings:
# - Numbered: 1, 1.1, 2.3.4, etc.
# - Markdown-ish: #, ##, ###
# - ALL CAPS short lines
# - Ends with colon and short length
HEADING_NUM = re.compile(r'^\s*(\d+(\.\d+)*)[)\.]?\s+(.+?)\s*$')
HEADING_MD = re.compile(r'^\s*(#{1,6})\s+(.+?)\s*$')
ALL_CAPS = re.compile(r'^[A-Z0-9 \-_/&]{3,60}$')

@dataclass
class SectionNode:
    title: str
    level: int
    start_line: int
    end_line: int
    content: str
    children: List['SectionNode']

def _level_from_numbering(num: str) -> int:
    return num.count('.') + 1

def _is_heading(line: str) -> (bool, int, str):
    m = HEADING_NUM.match(line)
    if m:
        lvl = _level_from_numbering(m.group(1))
        return True, lvl, m.group(3).strip()

    m = HEADING_MD.match(line)
    if m:
        return True, len(m.group(1)), m.group(2).strip()

    cap = line.strip()
    if len(cap) <= 80 and (ALL_CAPS.match(cap) or (cap.endswith(':') and len(cap.split()) <= 10)):
        return True, 1, cap.rstrip(':').title()

    return False, 0, ""

def detect_sections(text: str) -> List[SectionNode]:
    lines = text.splitlines()
    candidates = []
    for idx, ln in enumerate(lines):
        is_h, lvl, title = _is_heading(ln)
        if is_h:
            candidates.append((idx, lvl, title))

    # Fallback: if no headings detected, return single section
    if not candidates:
        return [SectionNode(title="Document", level=1, start_line=0, end_line=len(lines)-1,
                            content=text, children=[])]

    # Build hierarchy using a stack
    nodes: List[SectionNode] = []
    stack: List[SectionNode] = []
    for i, (start, lvl, title) in enumerate(candidates):
        end = (candidates[i+1][0]-1) if i+1 < len(candidates) else len(lines)-1
        content = "\n".join(lines[start+1:end+1]).strip()
        node = SectionNode(title=title, level=lvl, start_line=start, end_line=end, content=content, children=[])

        # place in hierarchy
        while stack and stack[-1].level >= node.level:
            stack.pop()
        if stack:
            stack[-1].children.append(node)
        else:
            nodes.append(node)
        stack.append(node)
    return nodes

def sections_to_json(nodes: List[SectionNode]) -> List[Dict[str, Any]]:
    def _pack(n: SectionNode) -> Dict[str, Any]:
        return {
            "title": n.title,
            "level": n.level,
            "start_line": n.start_line,
            "end_line": n.end_line,
            "content": n.content,
            "children": [ _pack(c) for c in n.children ]
        }
    return [ _pack(n) for n in nodes ]
