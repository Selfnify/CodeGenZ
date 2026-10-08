"""
genz.parser
-----------
Hand-written recursive-descent parser. Indentation was already resolved
into INDENT/DEDENT tokens by the lexer, so this module just has to walk
the token list and build up a Program AST.
"""

from typing import List, Tuple, Optional
from .lexer import Token
from .ast_nodes import (
    Program, StyleRule, StyleDecl, Element, VarDecl,
    ActSet, ActAdjust, ActVisibility, ActClass, ActCall, ActIf, WhenBlock,
)

EVENT_VERBS = {
    "click", "hover", "submit", "change", "input", "load",
    "dblclick", "keyup", "keydown", "mouseover", "mouseout", "focus", "blur",
}


class ParseError(Exception):
    def __init__(self, message: str, line: int):
        super().__init__(f"line {line}: {message}")
        self.line = line


def raw_join(tokens: List[Token]) -> str:
    """Reconstruct a plausible source string from a run of tokens.
    Used anywhere we want to hand raw JS straight to the output (event
    handlers, var values, script blocks, multi-word style values)."""
    parts = []
    for t in tokens:
        if t.kind == "STRING":
            esc = t.value.replace("\\", "\\\\").replace('"', '\\"')
            parts.append(f'"{esc}"')
        else:
            parts.append(t.value)
    return " ".join(parts)


def parse_selector_word(word: str) -> Tuple[List[str], Optional[str]]:
    """Split a selector token like '.card.highlight#main' into
    (classes, id)."""
    classes = []
    elem_id = None
    buf = ""
    mode = None  # '.' or '#'
    for ch in word:
        if ch in ".#":
            if mode == "." and buf:
                classes.append(buf)
            elif mode == "#" and buf:
                elem_id = buf
            mode = ch
            buf = ""
        else:
            buf += ch
    if mode == "." and buf:
        classes.append(buf)
    elif mode == "#" and buf:
        elem_id = buf
    return classes, elem_id


class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0

    # -- low-level helpers -------------------------------------------------
    def peek(self, offset: int = 0) -> Token:
        idx = min(self.pos + offset, len(self.tokens) - 1)
        return self.tokens[idx]

    def advance(self) -> Token:
        t = self.tokens[self.pos]
        if self.pos < len(self.tokens) - 1:
            self.pos += 1
        return t

    def expect(self, kind: str) -> Token:
        t = self.peek()
        if t.kind != kind:
            raise ParseError(f"expected {kind} but got {t.kind} {t.value!r}", t.line)
        return self.advance()

    def skip_newlines(self):
        while self.peek().kind == "NEWLINE":
            self.advance()

    def line_tokens(self) -> List[Token]:
        """Collect tokens up to (not including) the next NEWLINE/EOF/COLON."""
        toks = []
        while self.peek().kind not in ("NEWLINE", "EOF", "INDENT", "DEDENT", "COLON"):
            toks.append(self.advance())
        return toks

    # -- entry point ---------------------------------------------------
    def parse_program(self) -> Program:
        prog = Program()
        self.skip_newlines()
        while self.peek().kind != "EOF":
            self.skip_newlines()
            if self.peek().kind == "EOF":
                break
            tok = self.peek()
            if tok.kind == "WORD" and tok.value == "page":
                self._parse_page(prog)
            elif tok.kind == "WORD" and tok.value == "style" and self.peek(1).kind == "COLON":
                prog.style_rules.extend(self._parse_style_block())
            elif tok.kind == "WORD" and tok.value == "script" and self.peek(1).kind == "COLON":
                prog.raw_script_lines.extend(self._parse_script_block())
            elif tok.kind == "WORD" and tok.value == "var":
                prog.vars.append(self._parse_var())
            elif tok.kind == "WORD" and tok.value == "when" and self.peek(1).kind == "WORD":
                prog.when_blocks.append(self._parse_when_block())
            elif tok.kind == "WORD" and tok.value == "box" and self.peek(1).kind != "NEWLINE":
                prog.body.append(self._parse_box())
            elif tok.kind == "WORD":
                prog.body.append(self._parse_element_line())
            else:
                raise ParseError(f"unexpected token {tok.value!r}", tok.line)
            self.skip_newlines()
        return prog

    # -- top-level statements -------------------------------------------
    def _parse_page(self, prog: Program):
        self.advance()  # 'page'
        title_tok = self.expect("STRING")
        prog.title = title_tok.value
        self.expect("NEWLINE")

    def _parse_var(self) -> VarDecl:
        line = self.peek().line
        self.advance()  # 'var'
        name_tok = self.expect("WORD")
        self.expect("SYM")  # '='
        rest = self.line_tokens()
        self.expect("NEWLINE")
        return VarDecl(name=name_tok.value, expr=raw_join(rest), line=line)

    # -- the `when ... :` action language ------------------------------
    def _parse_when_block(self) -> WhenBlock:
        line = self.peek().line
        self.advance()  # 'when'
        event_tok = self.expect("WORD")
        sel_tok = self.expect("WORD")
        self.expect("COLON")
        self.expect("NEWLINE")
        self.expect("INDENT")
        actions = self._parse_actions()
        self.expect("DEDENT")
        return WhenBlock(event=event_tok.value, selector=sel_tok.value, actions=actions, line=line)

    def _parse_actions(self) -> list:
        actions = []
        while self.peek().kind != "DEDENT":
            self.skip_newlines()
            if self.peek().kind == "DEDENT":
                break
            actions.append(self._parse_action_stmt())
            self.skip_newlines()
        return actions

    def _parse_action_stmt(self):
        tok = self.peek()
        line = tok.line

        if tok.kind != "WORD":
            raise ParseError(f"expected an action, got {tok.value!r}", line)

        if tok.value == "set":
            self.advance()
            w2 = self.peek()
            if w2.kind == "WORD" and w2.value in ("text", "value") and self.peek(1).value == "of":
                kind = w2.value
                self.advance()  # text/value
                self.advance()  # 'of'
                target_tok = self.expect("WORD")
                of_to = self.expect("WORD")
                if of_to.value != "to":
                    raise ParseError("expected 'to' in set statement", line)
                rest = self.line_tokens()
                self.expect("NEWLINE")
                return ActSet(target=f"{kind}:{target_tok.value.lstrip('#')}", expr=raw_join(rest), line=line)
            else:
                name_tok = self.expect("WORD")
                to_tok = self.expect("WORD")
                if to_tok.value != "to":
                    raise ParseError("expected 'to' in set statement", line)
                rest = self.line_tokens()
                self.expect("NEWLINE")
                return ActSet(target=name_tok.value, expr=raw_join(rest), line=line)

        if tok.value in ("increase", "decrease"):
            self.advance()
            name_tok = self.expect("WORD")
            expr = "1"
            if self.peek().kind == "WORD" and self.peek().value == "by":
                self.advance()
                rest = self.line_tokens()
                expr = raw_join(rest)
            self.expect("NEWLINE")
            return ActAdjust(name=name_tok.value, op=tok.value, expr=expr, line=line)

        if tok.value in ("show", "hide"):
            self.advance()
            target_tok = self.expect("WORD")
            self.expect("NEWLINE")
            return ActVisibility(target_id=target_tok.value.lstrip("#"), show=(tok.value == "show"), line=line)

        if tok.value in ("add", "remove", "toggle") and self.peek(1).kind == "WORD" and self.peek(1).value == "class":
            op = tok.value
            self.advance()
            self.advance()  # 'class'
            cls_tok = self.expect("STRING")
            on_tok = self.expect("WORD")
            if on_tok.value != "on":
                raise ParseError("expected 'on' in class statement", line)
            target_tok = self.expect("WORD")
            self.expect("NEWLINE")
            return ActClass(op=op, cls=cls_tok.value, target_id=target_tok.value.lstrip("#"), line=line)

        if tok.value in ("alert", "log"):
            self.advance()
            rest = self.line_tokens()
            self.expect("NEWLINE")
            return ActCall(kind=tok.value, expr=raw_join(rest), line=line)

        if tok.value == "if":
            self.advance()
            cond_toks = self.line_tokens()
            self.expect("COLON")
            self.expect("NEWLINE")
            self.expect("INDENT")
            then_actions = self._parse_actions()
            self.expect("DEDENT")
            else_actions = []
            self.skip_newlines()
            if self.peek().kind == "WORD" and self.peek().value == "else":
                self.advance()
                self.expect("COLON")
                self.expect("NEWLINE")
                self.expect("INDENT")
                else_actions = self._parse_actions()
                self.expect("DEDENT")
            return ActIf(cond=raw_join(cond_toks), then=then_actions, else_=else_actions, line=line)

        raise ParseError(f"unknown action {tok.value!r}", line)

    def _parse_script_block(self) -> List[str]:
        self.advance()  # 'script'
        self.expect("COLON")
        self.expect("NEWLINE")
        self.expect("INDENT")
        lines: List[str] = []
        depth = 1
        while True:
            tok = self.peek()
            if tok.kind == "INDENT":
                depth += 1
                self.advance()
                continue
            if tok.kind == "DEDENT":
                depth -= 1
                self.advance()
                if depth == 0:
                    break
                continue
            if tok.kind == "NEWLINE":
                self.advance()
                continue
            line_toks = self.line_tokens()
            lines.append(("  " * depth) + raw_join(line_toks))
        return lines

    def _parse_style_block(self) -> List[StyleRule]:
        self.advance()  # 'style'
        self.expect("COLON")
        self.expect("NEWLINE")
        self.expect("INDENT")
        rules: List[StyleRule] = []
        while self.peek().kind != "DEDENT":
            self.skip_newlines()
            if self.peek().kind == "DEDENT":
                break
            sel_toks = self.line_tokens()
            selector = raw_join(sel_toks)
            self.expect("COLON")
            self.expect("NEWLINE")
            self.expect("INDENT")
            rule = StyleRule(selector=selector)
            while self.peek().kind != "DEDENT":
                self.skip_newlines()
                if self.peek().kind == "DEDENT":
                    break
                line = self.peek().line
                prop_tok = self.expect("WORD")
                val_toks = self.line_tokens()
                self.expect("NEWLINE")
                rule.decls.append(StyleDecl(prop=prop_tok.value, value=raw_join(val_toks), line=line))
            self.expect("DEDENT")
            rules.append(rule)
            self.skip_newlines()
        self.expect("DEDENT")
        return rules

    # -- elements ---------------------------------------------------------
    def _parse_box(self) -> Element:
        line = self.peek().line
        self.advance()  # 'box'
        classes: List[str] = []
        elem_id = None
        if self.peek().kind == "WORD":
            sel_tok = self.advance()
            classes, elem_id = parse_selector_word(sel_tok.value)
        self.expect("COLON")
        self.expect("NEWLINE")
        self.expect("INDENT")
        children = []
        while self.peek().kind != "DEDENT":
            self.skip_newlines()
            if self.peek().kind == "DEDENT":
                break
            tok = self.peek()
            if tok.kind == "WORD" and tok.value == "box" and self.peek(1).kind != "NEWLINE":
                children.append(self._parse_box())
            else:
                children.append(self._parse_element_line())
            self.skip_newlines()
        self.expect("DEDENT")
        return Element(tag="div", classes=classes, elem_id=elem_id, children=children, line=line)

    def _parse_element_line(self) -> Element:
        line = self.peek().line
        tag_tok = self.expect("WORD")
        el = Element(tag=tag_tok.value, line=line)
        toks = self.line_tokens()
        i = 0
        n = len(toks)
        while i < n:
            t = toks[i]
            if t.kind == "STRING" and el.text is None:
                el.text = t.value
                i += 1
                continue
            if t.kind == "WORD" and (t.value.startswith(".") or t.value.startswith("#")):
                cls, eid = parse_selector_word(t.value)
                el.classes.extend(cls)
                if eid:
                    el.elem_id = eid
                i += 1
                continue
            if t.kind == "WORD" and t.value in EVENT_VERBS:
                rest = toks[i + 1:]
                el.events[t.value] = raw_join(rest)
                i = n
                continue
            if t.kind == "WORD" and i + 1 < n and toks[i + 1].kind == "SYM" and toks[i + 1].value == "=":
                attr_name = t.value
                value_tok = toks[i + 2] if i + 2 < n else None
                el.attrs[attr_name] = value_tok.value if value_tok else ""
                i += 3
                continue
            raise ParseError(f"unexpected token {t.value!r} in element line", t.line)
        self.expect("NEWLINE")
        return el


def parse(tokens: List[Token]) -> Program:
    return Parser(tokens).parse_program()
