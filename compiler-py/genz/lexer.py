"""
genz.lexer
----------
Turns raw CodeGenZ (.gz) source text into a flat list of tokens.

CodeGenZ is indentation-based (like Python/YAML), so most of the work
here is converting leading whitespace into explicit INDENT / DEDENT
tokens that the parser can consume without caring about columns at all.
"""

from dataclasses import dataclass
from typing import List


class LexError(Exception):
    def __init__(self, message: str, line: int):
        super().__init__(f"line {line}: {message}")
        self.line = line


@dataclass
class Token:
    kind: str       # NEWLINE, INDENT, DEDENT, WORD, STRING, EOF
    value: str
    line: int

    def __repr__(self):
        return f"<{self.kind} {self.value!r}>"


def _split_logical_lines(src: str):
    """Yield (line_number, indent_spaces, content) for every non-blank,
    non-comment logical line. Comments start with '#'."""
    for i, raw in enumerate(src.splitlines(), start=1):
        # strip trailing whitespace/newlines only, keep leading
        line = raw.rstrip()
        stripped = line.strip()
        if stripped == "" or stripped.startswith("#"):
            continue
        indent = len(line) - len(line.lstrip(" "))
        if "\t" in line[:indent]:
            raise LexError("tabs are not allowed for indentation, use spaces", i)
        yield i, indent, line.strip()


def _tokenize_content(line: str, line_no: int) -> List[Token]:
    """Tokenize the content of a single logical line into WORD/STRING tokens.
    Strings are double-quoted and may contain escaped quotes with \\"."""
    tokens = []
    i = 0
    n = len(line)
    while i < n:
        c = line[i]
        if c == " ":
            i += 1
            continue
        if c == '"':
            j = i + 1
            buf = []
            while j < n and line[j] != '"':
                if line[j] == "\\" and j + 1 < n:
                    buf.append(line[j + 1])
                    j += 2
                else:
                    buf.append(line[j])
                    j += 1
            if j >= n:
                raise LexError("unterminated string literal", line_no)
            tokens.append(Token("STRING", "".join(buf), line_no))
            i = j + 1
            continue
        if c in "(),=":
            tokens.append(Token("SYM", c, line_no))
            i += 1
            continue
        # a bare "word" - runs until whitespace/quote/sym-char, keeping
        # hyphens, dots, colons etc. intact so hyphenated classes
        # (.nav-link), colors (#fff) and selectors (.card) survive as a
        # single WORD token. '(' ')' ',' '=' still split a word so that
        # `href="x"` and `alert("hi")` tokenize sanely.
        j = i
        while j < n and line[j] not in ' "(),=':
            j += 1
        word = line[i:j]
        tokens.append(Token("WORD", word, line_no))
        i = j
    return tokens


def tokenize(src: str) -> List[Token]:
    tokens: List[Token] = []
    indent_stack = [0]

    for line_no, indent, content in _split_logical_lines(src):
        if indent > indent_stack[-1]:
            indent_stack.append(indent)
            tokens.append(Token("INDENT", "", line_no))
        while indent < indent_stack[-1]:
            indent_stack.pop()
            tokens.append(Token("DEDENT", "", line_no))
        if indent not in indent_stack:
            raise LexError("inconsistent indentation", line_no)

        # does this line end with ':' -> block header
        is_block = content.endswith(":")
        body = content[:-1].strip() if is_block else content

        tokens.extend(_tokenize_content(body, line_no))
        tokens.append(Token("COLON" if is_block else "NEWLINE", "", line_no))
        if is_block:
            tokens.append(Token("NEWLINE", "", line_no))

    while len(indent_stack) > 1:
        indent_stack.pop()
        tokens.append(Token("DEDENT", "", 0))
    tokens.append(Token("EOF", "", 0))
    return tokens
