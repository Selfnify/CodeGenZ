# Changelog

## v1.1.0

- Added the `when`/action language — CodeGenZ's own logic layer:
  `when click #id:` blocks with `set`, `increase`/`decrease`,
  `show`/`hide`, `add/remove/toggle class`, `alert`, `log`, and
  `if`/`else`. No `document.getElementById` or `function` keyword
  required in source anymore.
- `hello.gz` and `counter.gz` rewritten to use it.
- `docs/SYNTAX.md` expanded with the full action-language reference.
- Note: `compiler-js` does not have this feature yet — `compiler-py`
  is the complete implementation as of this release.

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
