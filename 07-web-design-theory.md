# Chapter 7: Web Design Theory

## What this covers

This chapter revises the Web Design School part of the bootcamp: the
design principles a developer needs to make a site look intentional
rather than default. It covers colour theory (the wheel, common schemes,
contrast and accessibility, and the tools to check it), typography
(serif vs sans-serif, pairing fonts, hierarchy, and readable line length
and height), User Interface (UI) design principles (whitespace,
alignment, hierarchy, consistency, and Fitts's law), User Experience
(UX) design principles (simplicity, feedback, affordances, and user
flows), and layout (grid systems, the classic 960 grid, and visual
hierarchy). The aim is to give you a checklist of reasons for the CSS
you already know how to write.

## Key concepts

### The colour wheel

The colour wheel arranges hues in a circle so you can reason about their
relationships by position. The three primary colours (red, yellow, blue
in the traditional artist's model) mix into secondaries (orange, green,
purple), and those mix into tertiaries. Position matters more than the
exact hue: colours near each other feel calm and related, colours
opposite each other feel high-energy and contrasting.

Three properties describe any single colour, and CSS `hsl()` maps
directly onto them, which is why it is the most designer-friendly colour
format:

```css
.brand {
  /* hue 210 (a blue), 80% saturation, 50% lightness */
  color: hsl(210, 80%, 50%);
}
.brand-muted { color: hsl(210, 30%, 50%); }  /* less saturated */
.brand-dark  { color: hsl(210, 80%, 30%); }  /* darker */
```

Why it matters: with `hsl()` you build a whole palette by holding the
hue fixed and only changing saturation and lightness, instead of
guessing hex codes.

### Colour schemes

A scheme is a rule for picking hues off the wheel so they work together.
Learn a few and you can generate a palette on demand:

- **Monochromatic**: one hue, varying lightness and saturation. Safe,
  cohesive, low effort.
- **Analogous**: 2-3 neighbouring hues (e.g. blue, blue-green, green).
  Harmonious, good for calm designs.
- **Complementary**: two opposite hues (e.g. blue and orange). Strong
  contrast, ideal for a call-to-action against a background.
- **Triadic**: three hues evenly spaced (120 apart). Vibrant but
  balanced.

```css
:root {
  --primary:   hsl(210, 80%, 50%);  /* blue */
  --accent:    hsl(30, 90%, 55%);   /* complementary orange */
  --neutral:   hsl(210, 15%, 25%);  /* dark, low-sat text colour */
}
```

Gotcha: use one dominant colour, one accent for actions, and neutrals
(near-greys) for most of the page. The common 60-30-10 guideline is 60%
dominant, 30% secondary, 10% accent.

### Contrast and accessibility

Contrast is the measured difference in luminance between two colours,
usually text and its background. The Web Content Accessibility
Guidelines (WCAG) set minimum contrast ratios so text stays readable for
low-vision users: **4.5:1** for normal body text (AA), **3:1** for large
text (roughly 24px, or 18.7px bold) and for UI components like input
borders. The stricter AAA level asks for 7:1.

```css
/* Passes AA: dark text on light bg is about 12:1 */
.body-text { color: hsl(210, 20%, 20%); background: hsl(0, 0%, 100%); }

/* Fails AA: light grey on white is often ~2:1 */
.too-faint { color: #bbbbbb; background: #ffffff; }
```

Why it matters: never signal meaning by colour alone (e.g. a red-only
error). Add an icon or text, so colour-blind users and anyone in bright
sunlight still get the message.

### Colour tools

You do not judge contrast or harmony by eye. Common tools, as of 2026:

- **Adobe Color** (color.adobe.com) and **Coolors** (coolors.co) to
  generate schemes from the wheel or from a photo.
- The **WebAIM Contrast Checker** (webaim.org/resources/contrastchecker)
  for a pass/fail against WCAG ratios.
- Browser **DevTools**: the colour picker in the Styles panel shows the
  contrast ratio and an AA/AAA badge inline, and the Lighthouse audit
  flags low-contrast text automatically.

```text
Workflow: pick hue in Coolors -> lock the accent ->
check text pairs in WebAIM -> confirm in DevTools contrast picker.
```

Gotcha: check contrast on the actual overlay colours, including text on
images and on semi-transparent overlays, not just your named tokens.

### Serif vs sans-serif

Serifs are the small feet on the ends of letter strokes. **Serif** faces
(Georgia, Times, Merriweather) feel traditional, formal, editorial, and
read well in long print passages. **Sans-serif** faces (Helvetica, Arial,
Inter, Roboto) feel modern, clean, and neutral, and are the default for
screen UI. There are also **monospace** faces (equal-width, for code)
and display faces (for large headings only).

```css
body { font-family: "Inter", system-ui, sans-serif; }  /* UI text */
code { font-family: "Fira Code", ui-monospace, monospace; }
```

Why it matters: the old "serif is unreadable on screen" rule is largely
gone with high-DPI displays, so choose by tone, not dogma. Sans-serif
remains the safe default for interface labels and small text.

### Font pairing

Pairing means choosing two (rarely three) typefaces that contrast enough
to create hierarchy but still feel related. The reliable recipes:

- One family, two weights (e.g. bold headings, regular body). Always
  works.
- A serif heading with a sans-serif body, or the reverse.
- A distinct display face for headings with a plain, neutral body face.

```css
h1, h2, h3 { font-family: "Playfair Display", serif; }  /* character */
body       { font-family: "Source Sans 3", sans-serif; } /* neutral */
```

Gotcha: avoid two faces that are subtly different (two humanist
sans-serifs) — the clash reads as a mistake. Contrast should be obvious
or absent. Limit a page to two families for performance and cohesion.

### Typographic hierarchy

Hierarchy is the visual ranking that tells the eye what to read first.
You build it with a **type scale**: a consistent ratio between sizes so
h1 > h2 > body > caption feel deliberately stepped. Vary size, weight,
colour, and spacing — not just size — to separate levels.

```css
:root {
  --step-0: 1rem;      /* body: 16px */
  --step-1: 1.25rem;   /* h3 */
  --step-2: 1.563rem;  /* h2  (ratio ~1.25, "major third") */
  --step-3: 1.953rem;  /* h1 */
}
h1 { font-size: var(--step-3); font-weight: 700; }
p  { font-size: var(--step-0); font-weight: 400; color: hsl(0,0%,25%); }
```

Why it matters: a shared ratio (1.2, 1.25, 1.333) makes every size
relate to the others, so the page looks composed rather than arbitrary.

### Readable line length and line height

Two settings do most of the work for reading comfort. **Line length**
(measure) should be about 45-75 characters per line; too long and the
eye loses its place returning to the next line, too short and it jumps
too often. The `ch` unit (width of "0") makes this easy. **Line height**
(leading) for body text should be roughly 1.4-1.6 (unitless), looser
than the default 1.2.

```css
.article {
  max-width: 65ch;      /* comfortable measure */
  line-height: 1.6;     /* airy body leading */
  font-size: 1.125rem;  /* ~18px reads better than 16 for long text */
}
```

Gotcha: headings want *tighter* line height (1.1-1.2) because their
lines are short and large; only body copy needs the loose leading.

### Whitespace

Whitespace (negative space) is the empty area between and around
elements. It is not wasted — it groups related things, separates
unrelated ones, and gives the eye somewhere to rest. Generous spacing is
the single biggest signal of a "premium" design. Use a consistent
spacing scale so gaps feel systematic.

```css
:root { --space-1: 8px; --space-2: 16px; --space-3: 24px; --space-4: 40px; }
.card { padding: var(--space-3); }
.stack > * + * { margin-top: var(--space-2); }  /* even vertical rhythm */
```

Why it matters: the **law of proximity** — items close together are
perceived as a group. Tighten space inside a component and widen it
between components to show structure without borders.

### Alignment

Every element should line up with something else; a shared edge creates
an invisible line that makes a layout feel ordered. Prefer strong left
(or start) alignment for text-heavy interfaces, and avoid mixing many
alignments on one screen. Centre small, symmetric blocks (a hero, a
short form) but left-align long text and lists.

```css
.form { display: grid; gap: 16px; }         /* labels + fields share
                                               a left edge automatically */
.hero { text-align: center; max-width: 50ch; margin-inline: auto; }
```

Gotcha: centred paragraphs of more than 2-3 lines are hard to read
because the left edge (where the eye returns) moves on every line.

### UI hierarchy and consistency

Visual hierarchy in UI means the most important action is the most
prominent — through size, colour, contrast, and position. Give a screen
exactly one primary button; everything else is secondary or a plain
link. **Consistency** means the same thing looks and behaves the same
everywhere: one button style set, one spacing scale, one set of colours.
This is what a design system or component library enforces.

```css
.btn            { padding: 10px 18px; border-radius: 8px; font-weight: 600; }
.btn-primary    { background: var(--primary); color: #fff; }
.btn-secondary  { background: transparent; border: 1px solid var(--primary); }
```

Why it matters: consistency lets users transfer what they learned on one
screen to the next, which lowers the effort of using the product.

### Fitts's law

Fitts's law states the time to reach a target grows as the target gets
smaller and farther away. In practice: make important, frequent controls
**bigger** and put them where the pointer already is or near a screen
edge (edges and corners are effectively infinite in size because the
cursor stops there). Give touch targets at least ~44px so fingers can
hit them.

```css
.cta { min-height: 48px; padding: 14px 28px; }   /* easy to hit */
.icon-btn { width: 44px; height: 44px; }         /* min touch target */
```

Gotcha: tiny close buttons, thin links crowded together, and important
actions buried in a corner of a large area all fight Fitts's law and
raise error rates.

### UX: simplicity

Simplicity means removing everything that is not essential so the core
task is obvious. Each element on a screen competes for attention, so
every extra option, field, or decoration has a cost. Prefer sensible
defaults over choices, progressive disclosure (hide advanced options
until needed) over showing everything, and clear copy over clever copy.

```text
Signup form, minimal: email + password + one button.
Not: email, confirm email, password, confirm password, referral code,
newsletter checkbox, and a captcha, all above the fold.
```

Why it matters: fewer elements mean fewer decisions (lower cognitive
load) and a faster path to the thing the user actually came to do.

### UX: feedback

Feedback is the system telling the user that an action registered and
what its result was. Every interaction should have a visible response:
hover and focus states on controls, a loading indicator for anything
that takes time, and a clear success or error message afterwards. Silence
makes users click again or assume the app is broken.

```css
.btn:hover  { filter: brightness(1.08); }
.btn:active { transform: translateY(1px); }
.btn:focus-visible { outline: 3px solid hsl(210,90%,70%); }
.btn[aria-busy="true"] { opacity: .6; pointer-events: none; }
```

Gotcha: keep the keyboard focus outline visible. Removing `outline` for
looks makes the app unusable for keyboard and screen-reader users; style
it with `:focus-visible` instead of deleting it.

### UX: affordances and signifiers

An affordance is what an element lets you do; a signifier is the visual
cue that advertises it. Good design makes things look like what they do:
buttons look pressable (raised, filled, cursor pointer), links look
clickable (colour + underline), text fields look editable (a bordered
box). Breaking these conventions to be "clever" makes users hunt for what
is interactive.

```css
a { color: var(--primary); text-decoration: underline; }
button { cursor: pointer; }         /* signal it is clickable */
input { border: 1px solid #ccc; }   /* signal it is a field */
```

Why it matters: users rely on learned conventions. Flat "buttons" with
no fill or border, or clickable text that looks like body copy, remove
the signifier and hurt discoverability.

### UX: user flows

A user flow is the sequence of screens and steps a person moves through
to complete a goal (e.g. browse -> add to cart -> checkout -> confirm).
Designing the flow, not just single screens, catches dead ends and
missing states. Map the **happy path** first, then the empty, loading,
and error states each step can enter.

```text
Checkout flow:
  Cart -> Shipping -> Payment -> Review -> Confirmation
  branches: empty cart, payment declined, address invalid
```

Gotcha: the states that are easy to forget — empty, loading, error, and
success — are exactly where users get stuck. Design them explicitly, not
as an afterthought.

### Grid systems

A grid is a set of evenly spaced columns (with gutters between them) that
you align content to, giving a page underlying structure and rhythm.
Most web grids use 12 columns because 12 divides cleanly into halves,
thirds, quarters, and sixths. You already use this: Bootstrap's grid and
CSS Grid both implement the same idea.

```css
.layout {
  display: grid;
  grid-template-columns: repeat(12, 1fr);  /* 12-col grid */
  gap: 24px;                                /* gutter */
}
.main    { grid-column: 1 / 9; }   /* span 8 columns */
.sidebar { grid-column: 9 / 13; }  /* span 4 columns */
```

Why it matters: aligning blocks to a shared column grid is what makes
independently designed sections look like one coherent page.

### The 960 grid

The 960 Grid System is a classic fixed-width layout convention from the
desktop era: a 960px content width divided into 12 columns (60px each)
with 20px gutters (or 16 columns of 40px). 960 was chosen because it
divides evenly many ways and fit the common 1024px monitors of the time.

```text
960px total = 12 columns x (60px col + 20px gutter)
Each column block = 80px; last gutter trimmed.
```

Gotcha: 960 is history now — modern layouts are fluid and responsive
(percentages, `fr`, `max-width`) rather than a fixed 960px. But the
12-column mental model it popularised is exactly what today's grids
still use, so it is worth knowing where the convention came from.

### Visual hierarchy in layout

Layout hierarchy guides the eye through the page in order of importance
using size, position, contrast, and spacing. Readers of left-to-right
languages tend to scan in an **F-pattern** (across the top, then down the
left) for text pages or a **Z-pattern** for sparse landing pages, so put
the most important content top-left and the primary action along that
path. Bigger, bolder, higher-contrast, and more isolated elements read
as more important.

```css
.hero h1  { font-size: 3rem; }                 /* size = importance */
.hero .cta { background: var(--accent); }      /* contrast draws eye */
.section  { margin-block: var(--space-4); }    /* isolation = emphasis */
```

Why it matters: you control reading order with visual weight, not just
DOM order. If everything is bold and large, nothing stands out and the
hierarchy collapses.

## Cheatsheet

| Concept | Rule of thumb | Note |
|---|---|---|
| Colour model | Use `hsl(h, s%, l%)` | Build palettes by tweaking l/s |
| Palette split | 60-30-10 | Dominant / secondary / accent |
| Complementary | Opposite hues | High contrast for CTAs |
| Body contrast | 4.5:1 (WCAG AA) | 3:1 for large text / UI |
| Contrast tool | WebAIM checker | Also DevTools colour picker |
| Body font | Sans-serif default | Serif fine on high-DPI |
| Pairing | 2 families max | Obvious contrast, not subtle |
| Type scale | Ratio 1.2-1.333 | Stepped, consistent sizes |
| Line length | 45-75 chars | `max-width: 65ch` |
| Body leading | line-height 1.4-1.6 | Headings tighter, ~1.1 |
| Whitespace | Consistent scale | Proximity = grouping |
| Primary action | One per screen | Size + colour + position |
| Fitts's law | Big, near, edges | Touch target >= 44px |
| Focus state | Keep `:focus-visible` | Never delete outline |
| Grid | 12 columns + gutter | Divides many ways |
| 960 grid | 960px / 12 / 20px gap | Historic, fixed-width |
| Scan pattern | F (text) / Z (sparse) | Key content top-left |

## Common mistakes

- Picking colours as random hex codes instead of an `hsl` system, so the
  palette never feels cohesive.
- Light-grey text on white that fails the 4.5:1 contrast minimum and is
  hard to read.
- Signalling errors or states by colour alone, invisible to colour-blind
  users.
- Pairing two subtly different fonts so the clash looks accidental, or
  loading four families at once.
- Full-width paragraphs with no `max-width`, giving 120-character lines
  that are tiring to read.
- Default tight line height (1.2) on body text, making paragraphs feel
  cramped.
- Cramming a screen so full that nothing has whitespace and no hierarchy
  emerges.
- More than one primary button per screen, so the main action is unclear.
- Tiny click targets and controls buried far from the pointer, ignoring
  Fitts's law.
- Removing the focus outline for aesthetics, breaking keyboard access.
- Designing only the happy path and forgetting empty, loading, and error
  states.
- Making interactive things look non-interactive (flat "buttons", links
  styled like plain text), removing the signifier.

## Quick self-check

1. In `hsl()`, which two values do you usually change to build tints and
   shades of one hue?
2. Name the four common colour schemes and which one gives the strongest
   contrast.
3. What is the WCAG AA contrast minimum for normal body text, and why is
   colour-only signalling a problem?
4. When would you reach for a serif face over a sans-serif?
5. What is a safe, always-works font pairing that uses only one family?
6. What is the recommended line length (measure) and body line height for
   comfortable reading?
7. What does the law of proximity say, and how do you use spacing to show
   grouping?
8. State Fitts's law in one sentence and give the minimum touch-target
   size.
9. Why should you style `:focus-visible` instead of removing the outline?
10. Why are web grids usually 12 columns, and where did the 960 grid come
    from?

### Answers

1. Saturation and lightness; hold the hue fixed and vary those to get a
   coherent set of tints and shades.
2. Monochromatic, analogous, complementary, and triadic; complementary
   (opposite hues) gives the strongest contrast.
3. 4.5:1. Colour alone excludes colour-blind users and anyone in poor
   viewing conditions, so pair it with an icon or text.
4. When the tone is editorial, formal, or traditional, or for long-form
   reading; on high-DPI screens serifs read fine.
5. One family in two weights, e.g. bold for headings and regular for
   body text.
6. About 45-75 characters per line (roughly `65ch`), with body line
   height around 1.4-1.6.
7. Items placed close together are perceived as a group; tighten space
   inside a component and widen it between components.
8. Time to hit a target grows as it gets smaller and farther away; make
   key controls large (touch targets at least ~44px) and near.
9. `:focus-visible` keeps a visible focus ring for keyboard users while
   avoiding it on mouse clicks; deleting the outline breaks keyboard and
   screen-reader navigation.
10. 12 divides cleanly into halves, thirds, quarters, and sixths; the 960
    grid was a fixed 960px, 12-column desktop-era convention that
    popularised that column model.
