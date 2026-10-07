"use strict";
/**
 * genz parser (Node.js port) - mirrors compiler-py/genz/parser.py.
 */

const EVENT_VERBS = new Set([
  "click", "hover", "submit", "change", "input", "load",
  "dblclick", "keyup", "keydown", "mouseover", "mouseout", "focus", "blur",
]);

class ParseError extends Error {
  constructor(message, line) {
    super(`line ${line}: ${message}`);
    this.line = line;
  }
}

function rawJoin(tokens) {
  return tokens
    .map((t) => (t.kind === "STRING" ? `"${t.value.replace(/\\/g, "\\\\").replace(/"/g, '\\"')}"` : t.value))
    .join(" ");
}

function parseSelectorWord(word) {
  const classes = [];
  let elemId = null;
  let mode = null;
  let buf = "";
  for (const ch of word) {
    if (ch === "." || ch === "#") {
      if (mode === "." && buf) classes.push(buf);
      else if (mode === "#" && buf) elemId = buf;
      mode = ch;
      buf = "";
    } else {
      buf += ch;
    }
  }
  if (mode === "." && buf) classes.push(buf);
  else if (mode === "#" && buf) elemId = buf;
  return [classes, elemId];
}

class Parser {
  constructor(tokens) {
    this.tokens = tokens;
    this.pos = 0;
  }
  peek(offset = 0) {
    const idx = Math.min(this.pos + offset, this.tokens.length - 1);
    return this.tokens[idx];
  }
  advance() {
    const t = this.tokens[this.pos];
    if (this.pos < this.tokens.length - 1) this.pos++;
    return t;
  }
  expect(kind) {
    const t = this.peek();
    if (t.kind !== kind) throw new ParseError(`expected ${kind} but got ${t.kind} ${JSON.stringify(t.value)}`, t.line);
    return this.advance();
  }
  skipNewlines() {
    while (this.peek().kind === "NEWLINE") this.advance();
  }
  lineTokens() {
    const toks = [];
    while (!["NEWLINE", "EOF", "INDENT", "DEDENT", "COLON"].includes(this.peek().kind)) {
      toks.push(this.advance());
    }
    return toks;
  }

  parseProgram() {
    const prog = { title: "CodeGenZ App", styleRules: [], body: [], vars: [], rawScriptLines: [] };
    this.skipNewlines();
    while (this.peek().kind !== "EOF") {
      this.skipNewlines();
      if (this.peek().kind === "EOF") break;
      const tok = this.peek();
      if (tok.kind === "WORD" && tok.value === "page") {
        this.advance();
        const titleTok = this.expect("STRING");
        prog.title = titleTok.value;
        this.expect("NEWLINE");
      } else if (tok.kind === "WORD" && tok.value === "style" && this.peek(1).kind === "COLON") {
        prog.styleRules.push(...this.parseStyleBlock());
      } else if (tok.kind === "WORD" && tok.value === "script" && this.peek(1).kind === "COLON") {
        prog.rawScriptLines.push(...this.parseScriptBlock());
      } else if (tok.kind === "WORD" && tok.value === "var") {
        prog.vars.push(this.parseVar());
      } else if (tok.kind === "WORD" && tok.value === "box" && this.peek(1).kind !== "NEWLINE") {
        prog.body.push(this.parseBox());
      } else if (tok.kind === "WORD") {
        prog.body.push(this.parseElementLine());
      } else {
        throw new ParseError(`unexpected token ${JSON.stringify(tok.value)}`, tok.line);
      }
      this.skipNewlines();
    }
    return prog;
  }

  parseVar() {
    const line = this.peek().line;
    this.advance();
    const nameTok = this.expect("WORD");
    this.expect("SYM");
    const rest = this.lineTokens();
    this.expect("NEWLINE");
    return { name: nameTok.value, expr: rawJoin(rest), line };
  }

  parseScriptBlock() {
    this.advance();
    this.expect("COLON");
    this.expect("NEWLINE");
    this.expect("INDENT");
    const lines = [];
    let depth = 1;
    while (true) {
      const tok = this.peek();
      if (tok.kind === "INDENT") { depth++; this.advance(); continue; }
      if (tok.kind === "DEDENT") {
        depth--;
        this.advance();
        if (depth === 0) break;
        continue;
      }
      if (tok.kind === "NEWLINE") { this.advance(); continue; }
      const lineToks = this.lineTokens();
      lines.push("  ".repeat(depth) + rawJoin(lineToks));
    }
    return lines;
  }

  parseStyleBlock() {
    this.advance();
    this.expect("COLON");
    this.expect("NEWLINE");
    this.expect("INDENT");
    const rules = [];
    while (this.peek().kind !== "DEDENT") {
      this.skipNewlines();
      if (this.peek().kind === "DEDENT") break;
      const selToks = this.lineTokens();
      const selector = rawJoin(selToks);
      this.expect("COLON");
      this.expect("NEWLINE");
      this.expect("INDENT");
      const rule = { selector, decls: [] };
      while (this.peek().kind !== "DEDENT") {
        this.skipNewlines();
        if (this.peek().kind === "DEDENT") break;
        const line = this.peek().line;
        const propTok = this.expect("WORD");
        const valToks = this.lineTokens();
        this.expect("NEWLINE");
        rule.decls.push({ prop: propTok.value, value: rawJoin(valToks), line });
      }
      this.expect("DEDENT");
      rules.push(rule);
      this.skipNewlines();
    }
    this.expect("DEDENT");
    return rules;
  }

  parseBox() {
    const line = this.peek().line;
    this.advance();
    let classes = [];
    let elemId = null;
    if (this.peek().kind === "WORD") {
      const selTok = this.advance();
      [classes, elemId] = parseSelectorWord(selTok.value);
    }
    this.expect("COLON");
    this.expect("NEWLINE");
    this.expect("INDENT");
    const children = [];
    while (this.peek().kind !== "DEDENT") {
      this.skipNewlines();
      if (this.peek().kind === "DEDENT") break;
      const tok = this.peek();
      if (tok.kind === "WORD" && tok.value === "box" && this.peek(1).kind !== "NEWLINE") {
        children.push(this.parseBox());
      } else {
        children.push(this.parseElementLine());
      }
      this.skipNewlines();
    }
    this.expect("DEDENT");
    return { tag: "div", text: null, classes, elemId, attrs: {}, events: {}, children, line };
  }

  parseElementLine() {
    const line = this.peek().line;
    const tagTok = this.expect("WORD");
    const el = { tag: tagTok.value, text: null, classes: [], elemId: null, attrs: {}, events: {}, children: [], line };
    const toks = this.lineTokens();
    let i = 0;
    const n = toks.length;
    while (i < n) {
      const t = toks[i];
      if (t.kind === "STRING" && el.text === null) { el.text = t.value; i++; continue; }
      if (t.kind === "WORD" && (t.value.startsWith(".") || t.value.startsWith("#"))) {
        const [cls, eid] = parseSelectorWord(t.value);
        el.classes.push(...cls);
        if (eid) el.elemId = eid;
        i++;
        continue;
      }
      if (t.kind === "WORD" && EVENT_VERBS.has(t.value)) {
        el.events[t.value] = rawJoin(toks.slice(i + 1));
        i = n;
        continue;
      }
      if (t.kind === "WORD" && i + 1 < n && toks[i + 1].kind === "SYM" && toks[i + 1].value === "=") {
        const valueTok = toks[i + 2];
        el.attrs[t.value] = valueTok ? valueTok.value : "";
        i += 3;
        continue;
      }
      throw new ParseError(`unexpected token ${JSON.stringify(t.value)} in element line`, t.line);
    }
    this.expect("NEWLINE");
    return el;
  }
}

function parse(tokens) {
  return new Parser(tokens).parseProgram();
}

module.exports = { parse, ParseError, parseSelectorWord, rawJoin };
