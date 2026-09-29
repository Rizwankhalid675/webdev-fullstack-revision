# Chapter 1: HTML, CSS and Bootstrap

## What this covers

This chapter revises the front-end foundations from the early bootcamp
sections: HTML5 document structure and semantic tags, building forms,
the CSS box model, selectors and specificity, the two modern layout
engines (flexbox and grid), positioning, responsive design with media
queries, and finally Bootstrap 5 (its grid, ready-made components, and
utility classes). The goal is to recall each idea fast and see a minimal
example, not to re-read the lectures.

## Key concepts

### HTML5 document structure

Every page starts with a doctype and a root `html` element that wraps a
`head` (metadata, not visible) and a `body` (the visible content). The
`meta charset` and `meta viewport` tags are effectively mandatory today:
the first fixes text encoding, the second makes the page scale correctly
on phones.

```html
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Revision Notes</title>
  </head>
  <body>
    <h1>Hello</h1>
  </body>
</html>
```

Why it matters: without the viewport meta, mobile browsers render at a
fake 980px width and shrink everything, so your media queries never fire.

### Semantic tags

Semantic elements name the *role* of a region instead of using generic
`div` soup. They help accessibility (screen readers), SEO, and make the
markup readable. Use `header`, `nav`, `main` (only one per page),
`section`, `article`, `aside`, and `footer` for structure; use
`figure`/`figcaption`, `time`, and `mark` for inline meaning.

```html
<header><nav>...</nav></header>
<main>
  <article>
    <h2>Post title</h2>
    <p>Body text...</p>
  </article>
  <aside>Related links</aside>
</main>
<footer>(c) 2026</footer>
```

Gotcha: a `section` should generally have a heading. If a wrapper exists
only for CSS/JS and carries no meaning, a plain `div` is still correct.

### Forms

A `form` collects input and submits it. Each control needs a `name` (the
key sent to the server) and, for accessibility, a `label` tied via
`for`/`id`. The `action` is the endpoint, `method` is usually `get`
(data in the URL) or `post` (data in the body). HTML5 adds input types
(`email`, `number`, `date`, `range`) and validation (`required`,
`min`, `pattern`) that run before submit.

```html
<form action="/subscribe" method="post">
  <label for="email">Email</label>
  <input id="email" name="email" type="email" required />
  <button type="submit">Sign up</button>
</form>
```

Why it matters: as a backend dev, remember the `name` attribute is what
lands in `req.body` (with body-parser / `express.urlencoded`). No `name`
means the field is silently not submitted.

### The box model

Every element is a box built of four layers, from inside out: content,
`padding`, `border`, and `margin`. Total rendered width depends on
`box-sizing`. The default `content-box` adds padding and border *on top*
of the width you set; `border-box` makes width include padding and
border, which is far more predictable.

```css
* {
  box-sizing: border-box;   /* width now covers padding + border */
}
.card {
  width: 300px;
  padding: 20px;            /* stays inside the 300px */
  border: 2px solid #333;
  margin: 16px;             /* space outside, not counted in width */
}
```

Gotcha: vertical margins between stacked block elements *collapse* (the
larger of the two wins, they do not add up). Padding never collapses.

### CSS selectors and specificity

Selectors target elements: by type (`p`), class (`.btn`), id (`#nav`),
attribute (`[type="text"]`), or relationship (descendant `a b`, child
`a > b`, adjacent `a + b`). When two rules set the same property, the
winner is decided by specificity, scored as (inline, ids, classes,
types). Higher tuple wins; ties go to whichever rule is written last.

```css
p { color: gray; }              /* 0,0,0,1 */
.note { color: blue; }          /* 0,0,1,0  -> wins over p */
#lead { color: red; }           /* 0,1,0,0  -> wins over .note */
```

Why it matters: reach for a more specific selector before resorting to
`!important`, which overrides everything and is painful to unwind later.

### Flexbox

Flexbox lays out items along a single axis (a row or a column). Set
`display: flex` on the parent; it becomes a flex container and its direct
children become flex items. `justify-content` aligns along the main axis,
`align-items` aligns along the cross axis, and `gap` spaces items without
margins.

```css
.toolbar {
  display: flex;
  justify-content: space-between;  /* main axis: push to edges */
  align-items: center;             /* cross axis: vertical center */
  gap: 12px;
}
```

Gotcha: `flex-direction: column` swaps the axes, so `justify-content`
now controls vertical and `align-items` controls horizontal. Use
`flex: 1` on an item to let it grow and fill remaining space.

### CSS grid

Grid is two-dimensional: you define rows *and* columns and place items
into cells. `grid-template-columns` sets the tracks; the `fr` unit is a
fraction of free space, and `repeat()` plus `minmax()` build responsive
layouts without media queries.

```css
.gallery {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 16px;
}
```

Why it matters: use flexbox for one-dimensional strips (nav bars, button
rows) and grid for true 2D page layouts. The `auto-fill`/`minmax` pattern
above gives a self-adjusting card grid in one line.

### Positioning

`position` controls how an element is placed and whether `top`/`right`/
`bottom`/`left` apply. `static` is the default (normal flow). `relative`
nudges an element from its normal spot and creates a positioning context.
`absolute` removes it from flow and positions it against the nearest
positioned ancestor. `fixed` pins to the viewport; `sticky` toggles
between relative and fixed as you scroll.

```css
.badge-wrap { position: relative; }
.badge {
  position: absolute;   /* relative to .badge-wrap */
  top: -8px;
  right: -8px;
}
.header { position: sticky; top: 0; }  /* stays on screen when scrolling */
```

Gotcha: `absolute` anchors to the closest ancestor with a non-`static`
position. Forgetting to set `position: relative` on the parent makes it
jump to the whole page instead.

### Media queries and responsive design

Media queries apply CSS only when conditions hold, most often a viewport
width. The modern habit is mobile-first: write the base styles for small
screens, then use `min-width` queries to add layout as the screen grows.
Combine this with fluid units (`%`, `rem`, `fr`, `clamp()`) so the design
flexes between breakpoints too.

```css
.container { padding: 16px; }          /* mobile base */

@media (min-width: 768px) {            /* tablet and up */
  .container { display: flex; gap: 24px; }
}
```

Why it matters: mobile-first keeps overrides additive and simpler. Pick
breakpoints where the content breaks, not around specific device models.

### Bootstrap 5 grid

Bootstrap is a CSS framework with a 12-column responsive grid. Wrap rows
in `.container`, each row in `.row`, and size columns with `.col-*`
classes using breakpoint infixes (`sm`, `md`, `lg`, `xl`, `xxl`).
Bootstrap 5 dropped jQuery, so components use plain JS, and it added an
`xxl` breakpoint.

```html
<div class="container">
  <div class="row">
    <div class="col-12 col-md-6">Half on tablet+, full on phone</div>
    <div class="col-12 col-md-6">Second half</div>
  </div>
</div>
```

Gotcha: columns must be direct children of `.row`, and rows should sit
inside a `.container` (or `.container-fluid`) or the negative row margins
cause horizontal overflow.

### Bootstrap 5 components and utilities

Components are pre-styled widgets: `card`, `navbar`, `modal`, `alert`,
`btn`. Interactive ones (modal, dropdown, collapse) need Bootstrap's JS
bundle and are wired with `data-bs-*` attributes. Utilities are tiny
single-purpose classes for spacing (`m`/`p` + side + size, e.g. `mt-3`),
color (`text-primary`, `bg-light`), display (`d-flex`, `d-none`), and
more, so you rarely write custom CSS for common tweaks.

```html
<div class="card p-3 shadow-sm">
  <h5 class="card-title mb-2">Title</h5>
  <p class="card-text text-muted">Body</p>
  <button class="btn btn-primary" data-bs-toggle="modal"
          data-bs-target="#info">Open</button>
</div>
```

Why it matters: the spacing scale runs 0-5 (roughly 0 to 3rem), and `x`
means left+right, `y` means top+bottom (e.g. `px-4`, `my-2`). Learning
the utility shorthand is most of what makes Bootstrap fast.

## Cheatsheet

| Item | Syntax / class | Purpose |
|---|---|---|
| Viewport meta | `width=device-width` | Enable responsive scaling |
| Semantic layout | `header nav main footer` | Meaningful page regions |
| Label a field | `<label for="id">` | Accessible form control |
| Predictable sizing | `box-sizing: border-box` | Width includes pad+border |
| Class selector | `.name` | Score 0,0,1,0 |
| Id selector | `#name` | Score 0,1,0,0 |
| Center in flex | `justify + align-items` | Main and cross axis |
| Grow to fill | `flex: 1` | Take remaining space |
| Responsive grid | `repeat(auto-fill,minmax())` | Self-adjusting columns |
| Anchor child | parent `position: relative` | Base for `absolute` |
| Stick on scroll | `position: sticky; top: 0` | Pin while scrolling |
| Breakpoint up | `@media (min-width: 768px)` | Mobile-first query |
| BS grid column | `col-12 col-md-6` | 12-col responsive |
| BS spacing | `mt-3`, `px-4`, `my-2` | Margin/padding scale 0-5 |
| BS JS trigger | `data-bs-toggle` | Modal, dropdown, collapse |

## Common mistakes

- Omitting the viewport meta, so media queries never trigger on mobile.
- Leaving `box-sizing` at default, then fighting widths that overflow
  once padding is added.
- Forgetting the `name` attribute, so the field is not submitted to the
  server (empty `req.body`).
- Reaching for `!important` instead of a slightly more specific selector.
- Mixing up flex axes: assuming `align-items` is always vertical, even
  after `flex-direction: column`.
- Positioning `absolute` without a positioned ancestor, so it anchors to
  the whole page.
- Nesting Bootstrap columns that are not direct children of `.row`, or a
  `.row` without a container, causing horizontal overflow.
- Assuming Bootstrap 5 needs jQuery (it does not) or loading the old
  `data-toggle` attributes (v5 uses `data-bs-toggle`).

## Quick self-check

1. What are the two `meta` tags almost every page needs, and what does
   each do?
2. In `content-box` vs `border-box`, which includes padding inside the
   declared width?
3. Rank these by specificity: `p`, `.note`, `#lead`.
4. Which layout tool is one-dimensional and which is two-dimensional?
5. For `position: absolute` to anchor to a parent, what must the parent
   have?
6. What does the `fr` unit mean in CSS grid?
7. Why is mobile-first (`min-width` queries) usually preferred?
8. In Bootstrap, what does `col-12 col-md-6` produce across screen sizes?
9. What does the Bootstrap class `my-2` set?
10. Which attribute prefix wires Bootstrap 5 interactive components?

### Answers

1. `meta charset` sets text encoding; `meta viewport` with
   `width=device-width` enables correct mobile scaling.
2. `border-box` includes padding (and border) inside the declared width;
   `content-box` adds them on top.
3. `#lead` (0,1,0,0) > `.note` (0,0,1,0) > `p` (0,0,0,1).
4. Flexbox is one-dimensional (a row or column); grid is two-dimensional
   (rows and columns together).
5. A non-`static` position, typically `position: relative`, on the
   nearest ancestor.
6. A fraction of the remaining free space in the grid container.
7. Overrides stay additive: base styles cover small screens, and you add
   layout as width grows, which is simpler to reason about.
8. Full width (one column) on phones, and two half-width columns from
   the `md` breakpoint (768px) upward.
9. Vertical margin (top and bottom) at scale step 2.
10. The `data-bs-*` prefix, for example `data-bs-toggle` and
    `data-bs-target`.
