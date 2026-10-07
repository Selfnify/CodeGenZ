# CodeGenZ language reference

CodeGenZ is an indentation-based language that compiles to plain
`index.html`, `style.css` and `script.js`. No closing tags, no `{}` for
layout, no build config. Two spaces per indent level, like Python.

## `page`

Sets the `<title>`. Must appear once, usually at the top.

```
page "My Site"
```

## Elements

Any bare word followed by stuff on the same line is an HTML element.

```
h1 "Welcome"
p "a paragraph" .muted
a "Home" href="/"
img src="cat.png" alt="a cat"
button "Click me" click doStuff()
```

A single line can mix, in any order:

| piece | meaning |
|---|---|
| `"text"` | the element's text content (first string wins) |
| `.class` / `#id` | can be chained: `.card.highlight#main` |
| `attr="value"` | any HTML attribute, e.g. `href="/"`, `placeholder="name"` |
| `click <js>` | wires an event straight to raw JS (see Events) |

## `box`

A `box` is a `<div>` that can contain other elements, including nested
boxes. The selector after `box` is optional.

```
box .card:
  h3 "Title"
  p "Body text"

  box .footer:
    span "small print"
```

## `style`

Nested selector blocks, each containing property lines. Properties are
mostly friendly shorthand for real CSS - see the table below - but
**any real CSS property name also works untranslated**, so you're never
blocked waiting on a shorthand that doesn't exist yet.

```
style:
  body:
    bg #111
    color white
    font "Inter", sans-serif

  .card:
    pad 24px
    round 12px
    shadow 0 4px 12px rgba(0,0,0,.3)
```

### Shorthand properties

| CodeGenZ | CSS |
|---|---|
| `bg` | `background` |
| `size` | `font-size` |
| `weight` | `font-weight` |
| `font` | `font-family` |
| `pad` | `padding` |
| `round` | `border-radius` |
| `shadow` | `box-shadow` |
| `align` | `align-items` |
| `justify` | `justify-content` |
| `z` | `z-index` |
| `line` | `line-height` |
| `spacing` | `letter-spacing` |

(`color`, `margin`, `gap`, `width`, `height`, `border`, `opacity`,
`cursor`, `transition`, `display`, `position`, `top/left/right/bottom`,
`overflow` map straight to themselves.)

### No-value keywords

Some properties don't need a value — just write the word:

| keyword | expands to |
|---|---|
| `center` | `text-align: center;` |
| `flex` | `display: flex;` |
| `grid` | `display: grid;` |
| `hidden` | `display: none;` |
| `bold` | `font-weight: bold;` |
| `italic` | `font-style: italic;` |
| `underline` | `text-decoration: underline;` |
| `pointer` | `cursor: pointer;` |
| `rounded` | `border-radius: 9999px;` |

## Events

Any element line can end with an event verb followed by a raw JS
expression, which becomes an inline `on*` attribute:

```
button "Save" click saveForm()
input onchange handleTyping(this.value)
```

Supported verbs: `click, hover, submit, change, input, load, dblclick,
keyup, keydown, mouseover, mouseout, focus, blur`.

## `var`

Top-level variables become `let` declarations in the generated JS:

```
var count = 0
var name = "ZenX"
```

## `script`

Your escape hatch. Anything indented under `script:` is emitted into
`script.js` close to verbatim — write real JavaScript here, including
functions your `click` handlers call.

```
script:
  function saveForm() {
    console.log("saving...")
  }
```

## Comments

A line starting with `#` is ignored by the compiler.

```
# this won't show up in the output
h1 "visible"
```

## What CodeGenZ deliberately does NOT have (v0.1)

- No pseudo-selectors (`:hover` etc.) in `style:` blocks yet — use the
  `hover` event verb, or drop real CSS into a future `<style>` escape
  hatch.
- No component/import system yet — one `.gz` file compiles to one page.
- No reactivity/data-binding — `script:` + `document.getElementById`
  is the way, same as plain JS.

These are intentionally left out to keep the core language something
you can learn in five minutes. PRs welcome.
