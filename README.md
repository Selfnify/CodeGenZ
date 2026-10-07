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

v0.1 — core language works end to end, both compilers tested against
all three bundled examples with matching output. No component system,
no pseudo-selectors, no package manager yet. Contributions welcome.

## License

MIT, see [`LICENSE`](LICENSE).
