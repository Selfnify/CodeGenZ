#!/usr/bin/env node
"use strict";

const fs = require("fs");
const path = require("path");
const { tokenize, LexError } = require("./lexer");
const { parse, ParseError } = require("./parser");
const { generateHtml, generateCss, generateJs } = require("./codegen");

function compileSource(source) {
  const tokens = tokenize(source);
  const program = parse(tokens);
  const html = generateHtml(program.title, program.body, "style.css", "script.js");
  const css = generateCss(program.styleRules);
  const js = generateJs(program.vars, program.rawScriptLines);
  return { html, css, js };
}

function buildOnce(srcPath, outDir) {
  let source;
  try {
    source = fs.readFileSync(srcPath, "utf8");
  } catch (e) {
    console.error(`genz: cannot read ${srcPath}: ${e.message}`);
    return false;
  }
  let out;
  try {
    out = compileSource(source);
  } catch (e) {
    if (e instanceof LexError || e instanceof ParseError) {
      console.error(`genz: ${srcPath}: ${e.message}`);
      return false;
    }
    throw e;
  }
  fs.mkdirSync(outDir, { recursive: true });
  fs.writeFileSync(path.join(outDir, "index.html"), out.html);
  fs.writeFileSync(path.join(outDir, "style.css"), out.css);
  fs.writeFileSync(path.join(outDir, "script.js"), out.js);
  console.log(`genz: built ${srcPath} -> ${outDir}/ (index.html, style.css, script.js)`);
  return true;
}

function main(argv) {
  const [cmd, srcPath, ...rest] = argv;
  if (cmd !== "build" || !srcPath) {
    console.error("usage: genz build <file.gz> [-o outdir] [--watch]");
    process.exit(1);
  }
  let outDir = "dist";
  let watch = false;
  for (let i = 0; i < rest.length; i++) {
    if (rest[i] === "-o" || rest[i] === "--out") outDir = rest[++i];
    else if (rest[i] === "--watch") watch = true;
  }

  const ok = buildOnce(srcPath, outDir);
  if (!watch) process.exit(ok ? 0 : 1);

  console.log("genz: watching for changes (ctrl+c to stop)...");
  fs.watchFile(srcPath, { interval: 300 }, () => buildOnce(srcPath, outDir));
}

if (require.main === module) {
  main(process.argv.slice(2));
}

module.exports = { compileSource, buildOnce };
