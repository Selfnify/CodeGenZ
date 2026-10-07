"""
genz.codegen_css
-----------------
Turns the parsed `style:` block into plain CSS. CodeGenZ properties are
mostly shorthand aliases for real CSS properties so beginners don't need
to memorize `text-align` vs `justify-content` on day one — but any real
CSS property name also passes straight through, so nothing is ever
actually hidden from you.
"""

from typing import List
from .ast_nodes import StyleRule

# friendly-name -> real CSS property
PROPERTY_ALIASES = {
    "bg": "background",
    "color": "color",
    "size": "font-size",
    "weight": "font-weight",
    "font": "font-family",
    "pad": "padding",
    "margin": "margin",
    "round": "border-radius",
    "gap": "gap",
    "width": "width",
    "height": "height",
    "shadow": "box-shadow",
    "border": "border",
    "opacity": "opacity",
    "cursor": "cursor",
    "transition": "transition",
    "display": "display",
    "align": "align-items",
    "justify": "justify-content",
    "position": "position",
    "top": "top",
    "left": "left",
    "right": "right",
    "bottom": "bottom",
    "z": "z-index",
    "line": "line-height",
    "spacing": "letter-spacing",
    "overflow": "overflow",
}

# bare keywords (no value needed) that expand into a fixed declaration
NO_VALUE_PROPS = {
    "center": "text-align: center;",
    "flex": "display: flex;",
    "grid": "display: grid;",
    "hidden": "display: none;",
    "bold": "font-weight: bold;",
    "italic": "font-style: italic;",
    "underline": "text-decoration: underline;",
    "pointer": "cursor: pointer;",
    "rounded": "border-radius: 9999px;",
}


def _decl_to_css(prop: str, value: str) -> str:
    value = value.strip()
    if not value and prop in NO_VALUE_PROPS:
        return NO_VALUE_PROPS[prop]
    css_prop = PROPERTY_ALIASES.get(prop, prop)
    return f"{css_prop}: {value};"


def generate_css(style_rules: List[StyleRule]) -> str:
    out_lines = []
    for rule in style_rules:
        out_lines.append(f"{rule.selector} {{")
        for decl in rule.decls:
            out_lines.append(f"  {_decl_to_css(decl.prop, decl.value)}")
        out_lines.append("}")
        out_lines.append("")
    return "\n".join(out_lines).rstrip() + "\n"
