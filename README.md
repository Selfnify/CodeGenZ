# CodeGenZ

A tiny indentation-based language that compiles straight to plain
**HTML, CSS and JS**. No closing tags, no build config, no framework
to learn — write something that looks like this:

```
page "Hello CodeGenZ"

style:
  body:
    bg #0f0f17
    color #f5f5f5
    font "Poppins", sans-serif

  .title:
    size 48px
    weight 800
    center

var clicks = 0

box .title:
  h1 "Welcome to CodeGenZ"
  p "the easy way to build the web"

button "Click me" click handleClick()

script:
  function handleClick() {
    clicks = clicks + 1
    console.log(clicks)
  }
```

...and get a real, static, zero-dependency website out the other end.
Open the output `index.html` in a browser. That's the whole deploy
story.

## Why

HTML/CSS/JS are genuinely simple once you strip the ceremony. CodeGenZ
is that: real web pages, friendly syntax, no hidden runtime. There's
nothing here you can't fully read in an afternoon — see
[`docs/SYNTAX.md`](docs/SYNTAX.md).

## Two compilers, same language

| | Language | Entry point |
|---|---|---|
| [`compiler-py/`](compiler-py) | Python ≥3.8, stdlib only | `genz.cli` |
| [`compiler-js/`](compiler-js) | Node.js, zero deps | `src/cli.js` |

Both implement the exact same lexer → parser → codegen pipeline and
produce **byte-identical output** on every example in this repo. Use
whichever fits your stack; pick on vibes otherwise.

## Install

One-liner installers that set up a real `genz` command on your PATH
(Python-based, so Node isn't required just to use the CLI):

**macOS / Linux**
```sh
curl -fsSL https://raw.githubusercontent.com/enderairstudio/CodeGenZ/main/installers/install-mac.sh | bash
```

**Windows (PowerShell)**
```powershell
irm https://raw.githubusercontent.com/enderairstudio/CodeGenZ/main/installers/install-windows.ps1 | iex
```

Both clone the repo into `~/.codegenz` (`%USERPROFILE%\.codegenz` on
Windows) and `pip install --user -e` the Python compiler, so `genz` is
a real command afterward:

```sh
genz build path/to/site.gz -o dist/
```

Prefer no installer? Skip straight to **Quick start** below and run
either compiler directly from a clone.

## Quick start

### Python

```sh
cd compiler-py
python3 -m genz.cli build ../examples/hello.gz -o ../dist/hello
open ../dist/hello/index.html   # or just double-click it
```

Optional install for a real `genz` command:

```sh
cd compiler-py
pip install -e .
genz build ../examples/hello.gz -o dist/
```

### Node.js

```sh
cd compiler-js
node src/cli.js build ../examples/hello.gz -o ../dist/hello
```

Both support `--watch` to rebuild on save:

```sh
python3 -m genz.cli build site.gz -o dist/ --watch
```

## Project layout

```
CodeGenZ/
├── compiler-py/        # reference compiler (Python)
│   └── genz/
│       ├── lexer.py        # source -> tokens (indentation -> INDENT/DEDENT)
│       ├── parser.py       # tokens -> AST
│       ├── ast_nodes.py    # AST dataclasses
│       ├── codegen_html.py # AST -> index.html
│       ├── codegen_css.py  # AST -> style.css
│       ├── codegen_js.py   # AST -> script.js
│       └── cli.py          # `genz build ...`
├── compiler-js/         # Node.js port of the same pipeline
│   └── src/
│       ├── lexer.js
│       ├── parser.js
│       ├── codegen.js
│       └── cli.js
├── examples/             # .gz source files, see docs/EXAMPLES.md
│   ├── hello.gz
│   ├── landing.gz
│   └── counter.gz
├── installers/           # one-line installers (see Install above)
│   ├── install-mac.sh
│   └── install-windows.ps1
└── docs/
    ├── SYNTAX.md          # full language reference
    └── EXAMPLES.md        # walkthrough of each example
```

## The language, in one page

- `page "Title"` sets the `<title>`.
- Any line like `h1 "text" .class click handler()` is an element.
- `box .selector:` is a `<div>` that nests other elements.
- `style:` holds nested selector blocks with friendly CSS shorthand
  (`bg`, `pad`, `round`, `center`, ...) — real CSS property names also
  pass straight through.
- `var name = value` becomes a `let` in the generated JS.
- `script:` is a raw-JS escape hatch for anything the shorthand
  doesn't cover yet.

Full details, including the shorthand property table and supported
event verbs, live in [`docs/SYNTAX.md`](docs/SYNTAX.md).

## Status

v1.0.0 — core language works end to end, both compilers tested against
all three bundled examples with matching output, one-line installers
for macOS/Linux/Windows. No component system, no pseudo-selectors
yet. See [`CHANGELOG.md`](CHANGELOG.md). Contributions welcome.

## License

MIT, see [`LICENSE`](LICENSE).
