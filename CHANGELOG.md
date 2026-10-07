# Changelog

## v1.0.0

First tagged release.

- Core language: `page`, `box`, elements, `style:` blocks with CSS
  shorthand, `var`, `script:` escape hatch, event verbs (`click`,
  `hover`, `change`, ...).
- Two compilers, verified to produce byte-identical output:
  - `compiler-py` — Python ≥3.8, stdlib only.
  - `compiler-js` — Node.js, zero dependencies.
- Three example programs: `hello.gz`, `landing.gz`, `counter.gz`.
- One-line installers for macOS/Linux and Windows
  (`installers/install-mac.sh`, `installers/install-windows.ps1`)
  that install a real `genz` command onto your PATH.
- `docs/SYNTAX.md` full language reference, `docs/EXAMPLES.md`.

## v0.1.0

Initial commit: language design, both compilers, examples, docs.
