"""
genz.ast_nodes
--------------
Plain dataclasses describing a parsed CodeGenZ program. The parser builds
these; the codegen modules (codegen_html / codegen_css / codegen_js) walk
them to produce output.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional


@dataclass
class StyleDecl:
    """One property line inside a style selector block, e.g. `bg #111`."""
    prop: str
    value: str          # raw text, already reconstructed from tokens
    line: int


@dataclass
class StyleRule:
    """A selector block inside `style:`, e.g. `.hero:` with its declarations."""
    selector: str
    decls: List[StyleDecl] = field(default_factory=list)


@dataclass
class Element:
    """A single tag: a one-liner like `h1 "Hi"` or a `box` block with children."""
    tag: str
    text: Optional[str] = None
    classes: List[str] = field(default_factory=list)
    elem_id: Optional[str] = None
    attrs: Dict[str, str] = field(default_factory=dict)
    events: Dict[str, str] = field(default_factory=dict)   # event name -> raw JS
    children: List["Element"] = field(default_factory=list)
    line: int = 0


@dataclass
class VarDecl:
    name: str
    expr: str            # raw JS expression text
    line: int


# ---- CodeGenZ action language (the `when ... :` logic blocks) ----
# These are the "don't make me write document.getElementById / function"
# layer. Each Action subtype below is one easy-to-read statement; the
# JS codegen turns a list of them into real JS.

@dataclass
class ActSet:
    target: str   # "text:<id>", "value:<id>", or a bare var name
    expr: str
    line: int = 0


@dataclass
class ActAdjust:
    name: str
    op: str       # "increase" | "decrease"
    expr: str
    line: int = 0


@dataclass
class ActVisibility:
    target_id: str
    show: bool
    line: int = 0


@dataclass
class ActClass:
    op: str       # "add" | "remove" | "toggle"
    cls: str
    target_id: str
    line: int = 0


@dataclass
class ActCall:
    kind: str     # "alert" | "log"
    expr: str
    line: int = 0


@dataclass
class ActIf:
    cond: str
    then: List[object] = field(default_factory=list)
    else_: List[object] = field(default_factory=list)
    line: int = 0


@dataclass
class WhenBlock:
    event: str
    selector: str
    actions: List[object] = field(default_factory=list)
    line: int = 0


@dataclass
class Program:
    title: str = "CodeGenZ App"
    style_rules: List[StyleRule] = field(default_factory=list)
    body: List[Element] = field(default_factory=list)
    vars: List[VarDecl] = field(default_factory=list)
    when_blocks: List[WhenBlock] = field(default_factory=list)
    raw_script_lines: List[str] = field(default_factory=list)
