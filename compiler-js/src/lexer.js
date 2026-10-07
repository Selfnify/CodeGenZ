"use strict";
/**
 * genz lexer (Node.js port)
 * Same indentation -> INDENT/DEDENT scheme as the Python reference lexer.
 */

class LexError extends Error {
  constructor(message, line) {
    super(`line ${line}: ${message}`);
    this.line = line;
  }
}

function splitLogicalLines(src) {
  const out = [];
  const rawLines = src.split("\n");
  for (let i = 0; i < rawLines.length; i++) {
    const line = rawLines[i].replace(/\s+$/, "");
    const stripped = line.trim();
    if (stripped === "" || stripped.startsWith("#")) continue;
    const indent = line.length - line.replace(/^ +/, "").length;
    if (line.slice(0, indent).includes("\t")) {
      throw new LexError("tabs are not allowed for indentation, use spaces", i + 1);
    }
    out.push([i + 1, indent, stripped]);
  }
  return out;
}

function tokenizeContent(line, lineNo) {
  const tokens = [];
  let i = 0;
  const n = line.length;
  const symChars = "(),=";
  while (i < n) {
    const c = line[i];
    if (c === " ") { i++; continue; }
    if (c === '"') {
      let j = i + 1;
      let buf = "";
      while (j < n && line[j] !== '"') {
        if (line[j] === "\\" && j + 1 < n) { buf += line[j + 1]; j += 2; }
        else { buf += line[j]; j += 1; }
      }
      if (j >= n) throw new LexError("unterminated string literal", lineNo);
      tokens.push({ kind: "STRING", value: buf, line: lineNo });
      i = j + 1;
      continue;
    }
    if (symChars.includes(c)) {
      tokens.push({ kind: "SYM", value: c, line: lineNo });
      i++;
      continue;
    }
    // bare word: keep hyphens/dots/colons intact, only split on
    // space/quote/paren/comma/equals so hyphenated classes and JS
    // expressions survive as sane single tokens.
    let j = i;
    while (j < n && !' "(),='.includes(line[j])) j++;
    tokens.push({ kind: "WORD", value: line.slice(i, j), line: lineNo });
    i = j;
  }
  return tokens;
}

function tokenize(src) {
  const tokens = [];
  const indentStack = [0];
  for (const [lineNo, indent, content] of splitLogicalLines(src)) {
    if (indent > indentStack[indentStack.length - 1]) {
      indentStack.push(indent);
      tokens.push({ kind: "INDENT", value: "", line: lineNo });
    }
    while (indent < indentStack[indentStack.length - 1]) {
      indentStack.pop();
      tokens.push({ kind: "DEDENT", value: "", line: lineNo });
    }
    if (!indentStack.includes(indent)) {
      throw new LexError("inconsistent indentation", lineNo);
    }
    const isBlock = content.endsWith(":");
    const body = isBlock ? content.slice(0, -1).trim() : content;
    tokens.push(...tokenizeContent(body, lineNo));
    tokens.push({ kind: isBlock ? "COLON" : "NEWLINE", value: "", line: lineNo });
    if (isBlock) tokens.push({ kind: "NEWLINE", value: "", line: lineNo });
  }
  while (indentStack.length > 1) {
    indentStack.pop();
    tokens.push({ kind: "DEDENT", value: "", line: 0 });
  }
  tokens.push({ kind: "EOF", value: "", line: 0 });
  return tokens;
}

module.exports = { tokenize, LexError };
