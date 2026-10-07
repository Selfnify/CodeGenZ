# Examples

All three live in [`/examples`](../examples) and build cleanly with
both compilers (`compiler-py` and `compiler-js` produce byte-identical
output for all of them).

## `hello.gz`

The smallest useful program: a title, a couple of styled elements, a
`var`, and a click handler defined in a `script:` block. Good first
read if you're learning the syntax.

```sh
cd compiler-py
python3 -m genz.cli build ../examples/hello.gz -o ../dist/hello
```

## `landing.gz`

A small marketing-style landing page: a nav bar, a hero section with a
gradient CTA button, and a 3-card feature grid built with nested
`box` blocks. Shows `flex`, `gap`, multi-word CSS values (the
`linear-gradient(...)` background), and an event that calls a
`script:` function to smooth-scroll the page.

```sh
python3 -m genz.cli build ../examples/landing.gz -o ../dist/landing
```

## `counter.gz`

A tiny interactive app: one `var`, three buttons, and a `render()`
function in the `script:` block that keeps the DOM in sync. The
whole "state management" story in CodeGenZ right now: plain
variables, plain functions, plain `textContent` updates. No
framework required for something this size.

```sh
python3 -m genz.cli build ../examples/counter.gz -o ../dist/counter
```

Open any `dist/<name>/index.html` straight in a browser — no server
needed, nothing to bundle.
