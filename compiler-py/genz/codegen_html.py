"""
genz.codegen_html
-------------------
Walks the parsed Element tree (top-level `box`/element statements) and
renders real HTML. Event verbs (click, hover, ...) become inline
on* attributes wired to the generated <script>.
"""

from typing import List
from .ast_nodes import Element

VOID_TAGS = {"img", "input", "br", "hr", "meta", "link"}

EVENT_ATTR = {
    "click": "onclick",
    "hover": "onmouseover",
    "submit": "onsubmit",
    "change": "onchange",
    "input": "oninput",
    "load": "onload",
    "dblclick": "ondblclick",
    "keyup": "onkeyup",
    "keydown": "onkeydown",
    "mouseover": "onmouseover",
    "mouseout": "onmouseout",
    "focus": "onfocus",
    "blur": "onblur",
}


def _esc_text(s: str) -> str:
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def _esc_attr(s: str) -> str:
    return _esc_text(s).replace('"', "&quot;")


def _render_element(el: Element, indent: int = 0) -> str:
    pad = "  " * indent
    attrs = []
    if el.elem_id:
        attrs.append(f'id="{_esc_attr(el.elem_id)}"')
    if el.classes:
        attrs.append(f'class="{_esc_attr(" ".join(el.classes))}"')
    for name, value in el.attrs.items():
        attrs.append(f'{name}="{_esc_attr(value)}"')
    for verb, js in el.events.items():
        attr_name = EVENT_ATTR.get(verb, "on" + verb)
        attrs.append(f'{attr_name}="{_esc_attr(js)}"')

    attr_str = (" " + " ".join(attrs)) if attrs else ""

    if el.tag in VOID_TAGS:
        return f"{pad}<{el.tag}{attr_str}>"

    if el.children:
        inner = "\n".join(_render_element(c, indent + 1) for c in el.children)
        text_line = f"{pad}  {_esc_text(el.text)}\n" if el.text else ""
        return f"{pad}<{el.tag}{attr_str}>\n{text_line}{inner}\n{pad}</{el.tag}>"

    text = _esc_text(el.text) if el.text else ""
    return f"{pad}<{el.tag}{attr_str}>{text}</{el.tag}>"


def generate_body(body: List[Element]) -> str:
    return "\n".join(_render_element(el, 1) for el in body)


def generate_html(title: str, body: List[Element], css_href: str, js_href: str) -> str:
    body_html = generate_body(body)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{_esc_text(title)}</title>
  <link rel="stylesheet" href="{css_href}">
</head>
<body>
{body_html}
  <script src="{js_href}"></script>
</body>
</html>
"""
