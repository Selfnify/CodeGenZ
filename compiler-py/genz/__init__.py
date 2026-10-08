"""
genz
----
The reference compiler for CodeGenZ, a tiny indentation-based language
that compiles down to plain HTML, CSS and JS. See the package README
and docs/SYNTAX.md for the language itself; this package is just the
Python implementation of it.
"""

from .lexer import tokenize, LexError
from .parser import parse, ParseError
from .codegen_html import generate_html
from .codegen_css import generate_css
from .codegen_js import generate_js

__version__ = "1.0.0"
__all__ = [
    "tokenize", "parse", "generate_html", "generate_css", "generate_js",
    "LexError", "ParseError", "compile_source",
]


def compile_source(source: str, html_filename="index.html", css_filename="style.css", js_filename="script.js"):
    """Compile CodeGenZ source into (html, css, js) strings."""
    tokens = tokenize(source)
    program = parse(tokens)
    html = generate_html(program.title, program.body, css_filename, js_filename)
    css = generate_css(program.style_rules)
    js = generate_js(program.vars, program.raw_script_lines, program.when_blocks)
    return html, css, js
