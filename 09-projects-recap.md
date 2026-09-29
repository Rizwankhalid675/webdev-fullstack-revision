# Chapter 9: Projects and Challenges Recap

## What this covers

This chapter recaps the signature projects built across the bootcamp so you can
revise by rebuilding rather than re-watching. Each project is a `### heading`
below with three parts: what it teaches, the key concepts and APIs it exercises,
and a short original build outline in your own words (not the instructor's code).
The set is deliberately representative: two DOM/event warm-ups (Dice Game, Drum
Kit), a state-machine game (Simon), a static personal site (HTML/CSS), a
server-rendered app (Blog with Node/Express/EJS), a full CRUD app on a real
database (To-Do List with Express + PostgreSQL), an authentication app (Secrets
with Passport, bcrypt, sessions, OAuth), a React app (Keeper notes), and a Web3
DApp (DBANK / token on the Internet Computer in Motoko). Rebuild each from the
outline before checking your old solution.

## Key concepts

### Dice Game

**What it teaches.** Your first taste of making a page *do* something: read the
DOM, react to a page load, generate randomness, and swap image sources based on
data. It cements the idea that HTML is a tree you manipulate with JavaScript.

**Key concepts / APIs.** `document.querySelector`, setting `.src` and other
attributes, `Math.random()` and `Math.floor()`, comparing two values, updating
text with `.textContent` or `innerHTML`, running code on load.

**Build outline.**

1. Lay out two dice images and a heading in HTML; give each die a class you can
   target (e.g. `.img1`, `.img2`).
2. Prepare six dice image files named predictably, e.g. `dice1.png`..`dice6.png`.
3. In JS, write a helper that returns a random integer 1-6:
   `Math.floor(Math.random() * 6) + 1`.
4. Roll both dice, then set each image's `src` to the matching file.
5. Compare the two rolls and set the heading to "Player 1 wins", "Player 2 wins",
   or "Draw".

```js
function roll() {
  return Math.floor(Math.random() * 6) + 1;
}
const a = roll(), b = roll();
document.querySelector(".img1").src = `images/dice${a}.png`;
document.querySelector(".img2").src = `images/dice${b}.png`;
```

**Gotcha:** `Math.random()` returns `[0, 1)`, so multiply by 6 and floor for
0-5, then add 1. Off-by-one here is the classic bug.

### Drum Kit

**What it teaches.** Event listeners for both mouse and keyboard, mapping many
similar elements to one handler, playing audio, and adding short-lived visual
feedback. It is the leap from "one button" to "handle a set of things uniformly".

**Key concepts / APIs.** `addEventListener`, looping over a `querySelectorAll`
NodeList, the `Audio` constructor and `.play()`, `KeyboardEvent.key`, `switch`
statements, toggling a CSS class and removing it with `setTimeout`.

**Build outline.**

1. Render a row of buttons, one per drum sound, each labelled with a letter and
   carrying that letter as its class or text.
2. Write one function that takes a key/letter and plays the matching sound via
   `new Audio("sounds/x.mp3").play()` (a `switch` maps letter to file).
3. Loop over all drum buttons and attach a click listener that calls the function
   with that button's letter.
4. Add a single `keydown` listener on the document that reads `event.key` and
   calls the same function.
5. On each trigger, add a `pressed` class for animation and remove it after
   ~100ms with `setTimeout`.

```js
document.querySelectorAll(".drum").forEach((btn) => {
  btn.addEventListener("click", () => play(btn.textContent));
});
document.addEventListener("keydown", (e) => play(e.key));
```

**Why it matters:** reusing one handler for click and keydown avoids duplicated
logic. Creating a fresh `Audio` per hit lets the same sound overlap itself.

### Simon (memory game)

**What it teaches.** Managing application **state** across time: a growing
sequence, the player's progress through it, and win/lose transitions. This is
where you stop reacting to single events and start running a small state machine.
The course builds it with jQuery, but plain JS works identically.

**Key concepts / APIs.** Arrays as a sequence, tracking an index into user
progress, random choice, event handlers that read game state, timed UI flashes,
sound feedback, and a reset path. In jQuery: `$(...)`, `.addClass`/`.removeClass`,
`.on("click")`, `setTimeout`.

**Build outline.**

1. Keep three pieces of state: the computer's `gamePattern` (array of colors),
   the player's `userPattern` (array), and a `level`/started flag.
2. On the first key press or start, begin the game and run `nextSequence()`.
3. `nextSequence()` picks a random color, pushes it to `gamePattern`, flashes and
   sounds that button, increments the level, and clears `userPattern`.
4. On each color click: push to `userPattern`, flash/sound it, then check the
   answer at the just-clicked index.
5. If it matches and the player has reproduced the whole pattern, wait briefly
   and call `nextSequence()` for the next round.
6. If it mismatches, play a fail sound, flash a "game over" style, and reset all
   state so a new press starts over.

```js
function checkAnswer(i) {
  if (userPattern[i] !== gamePattern[i]) return gameOver();
  if (userPattern.length === gamePattern.length) {
    setTimeout(nextSequence, 800); // player finished this round
  }
}
```

**Gotcha:** compare only the index the player just clicked, not the whole array,
so you catch a wrong press immediately instead of after the full sequence.

### Personal Site (HTML/CSS)

**What it teaches.** Structuring a real page with semantic HTML and styling it
with CSS: the box model, layout with Flexbox, typography, responsive behaviour,
and deploying a static site. No JavaScript required — it is about clean markup
and visual polish.

**Key concepts / APIs.** Semantic elements (`header`, `nav`, `main`, `section`,
`footer`), the CSS box model (margin/border/padding/content), Flexbox
(`display: flex`, `justify-content`, `align-items`), media queries for
responsiveness, web fonts, and static hosting (e.g. GitHub Pages).

**Build outline.**

1. Sketch the sections: hero/intro, about, skills or projects, contact.
2. Write semantic HTML top to bottom before touching CSS, so the document reads
   well unstyled.
3. Add a stylesheet: set a base font and colours on `body`, then style section by
   section. Use a container with a max-width centred via `margin: 0 auto`.
4. Use Flexbox for the nav bar and any card rows; let items wrap on small screens.
5. Add one or two media queries (`@media (max-width: 600px)`) to stack columns and
   shrink the hero on phones.
6. Deploy as static files to a host like GitHub Pages.

```css
.nav {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
@media (max-width: 600px) {
  .cards { flex-direction: column; }
}
```

**Why it matters:** getting semantic structure right first makes the CSS simpler
and the page accessible by default. Layout is Flexbox for rows; reach for Grid
only when you need two-dimensional layout.

### Blog Web App (Node / Express / EJS)

**What it teaches.** Moving from static pages to a server that renders HTML per
request. You learn routing, handling form posts, passing data into templates, and
keeping data in server memory before a database is introduced.

**Key concepts / APIs.** Express (`app.get`, `app.post`), the EJS view engine
(`res.render`, `<%= %>` output vs `<% %>` logic, partials with `<%- include %>`),
`express.urlencoded` for form bodies, `express.static` for CSS/assets, and route
parameters (`/posts/:id`).

**Build outline.**

1. Set up Express, point the view engine at EJS, serve a `public` folder, and add
   `express.urlencoded({ extended: true })` to read form posts.
2. Keep posts in an in-memory array of `{ id, title, body }` (a database comes
   later).
3. `GET /` renders a home template that loops over posts and links each to its
   detail page.
4. `GET /compose` shows a form; `POST /compose` reads `req.body`, builds a post,
   pushes it, and redirects home.
5. `GET /posts/:id` finds the post by `req.params.id` and renders a detail view;
   return a 404 view if not found.
6. Factor the header and footer into EJS partials so every page shares them.

```js
app.post("/compose", (req, res) => {
  posts.push({ id: nextId++, title: req.body.title, body: req.body.body });
  res.redirect("/");
});
app.get("/posts/:id", (req, res) => {
  const post = posts.find((p) => p.id === Number(req.params.id));
  post ? res.render("post", { post }) : res.status(404).render("404");
});
```

**Gotcha:** use `<%= %>` for text (it escapes HTML and prevents injection) and
`<%- %>` only for trusted markup like `include`. Redirect after a POST so a
refresh doesn't resubmit the form.

### To-Do List (Express + PostgreSQL CRUD)

**What it teaches.** Persisting data in a real relational database and wiring the
four CRUD operations end to end: create, read, update, delete. This is the first
project where data survives a server restart.

**Key concepts / APIs.** PostgreSQL, the `pg` client/`Pool`, parameterised
queries (`$1`, `$2`), SQL `INSERT`/`SELECT`/`UPDATE`/`DELETE`, mapping HTTP verbs
to CRUD, and rendering DB rows through EJS. As of 2026, prefer `async/await` with
`pool.query` over callbacks.

**Build outline.**

1. Create a `pg` `Pool` from a connection string in `.env`; create an `items`
   table with `id SERIAL PRIMARY KEY` and a `title TEXT`.
2. `GET /` runs `SELECT * FROM items ORDER BY id` and renders the list.
3. `POST /add` inserts `req.body.title` with a parameterised query, then redirects
   home.
4. `POST /edit` updates a row by id; `POST /delete` deletes by id. (With plain
   HTML forms you POST these; a JSON API would use PUT/PATCH and DELETE.)
5. Always pass user input as query parameters, never string-concatenated into SQL.

```js
// Read
const { rows } = await pool.query("SELECT * FROM items ORDER BY id");
// Create (parameterised — safe from SQL injection)
await pool.query("INSERT INTO items (title) VALUES ($1)", [req.body.title]);
// Delete
await pool.query("DELETE FROM items WHERE id = $1", [req.body.id]);
```

**Gotcha:** never build SQL by concatenating `req.body` into the string — use
`$1` placeholders so the driver escapes values and blocks SQL injection. Close or
pool connections; a `Pool` reuses them for you.

### Secrets (auth app: Passport, bcrypt, sessions, OAuth)

**What it teaches.** Real authentication built up in layers: hashed passwords,
server-side sessions to stay logged in, Passport strategies to structure it, and
finally "Log in with Google" via OAuth. It ties together security concepts from
Chapter 5 into one working app.

**Key concepts / APIs.** `bcrypt.hash`/`bcrypt.compare`, `express-session`,
`passport`, `passport-local`, `passport.serializeUser`/`deserializeUser`,
`passport-google-oauth20`, `req.isAuthenticated()`, `req.login`/`req.logout`,
and route guards. Secrets live in `.env`.

**Build outline.**

1. Start with a `users` table/collection and a register route: hash the password
   with `bcrypt.hash(pw, 12)` before saving; never store plaintext.
2. Add `express-session`, then `passport.initialize()` and `passport.session()`
   after it.
3. Configure the local strategy: look up the user, `bcrypt.compare` the password,
   and call `done(null, user)` or `done(null, false)`.
4. Implement `serializeUser` (store just the id) and `deserializeUser` (reload the
   user from the id).
5. Protect the "secrets" page with a guard: if `req.isAuthenticated()`, render;
   else redirect to login.
6. Add Google OAuth with `passport-google-oauth20`: on the callback, find-or-create
   a local account keyed by the Google profile id. Allow accounts with no password
   hash for OAuth-only users.

```js
app.get("/secrets", (req, res) => {
  if (req.isAuthenticated()) return res.render("secrets");
  res.redirect("/login");
});
```

**Gotcha:** the OAuth code exchange and client secret must stay on the server, not
in the browser. Put `express.session` before Passport, or logins won't persist.

### Keeper App (React notes app)

**What it teaches.** Composing a React UI from components, lifting state to a
parent, passing data down as props and callbacks up, rendering a list with keys,
and using controlled form inputs. It is the React counterpart to the earlier
vanilla-JS DOM work.

**Key concepts / APIs.** Function components, `useState`, props and `children`,
lifting state up, `array.map` with a stable `key`, controlled inputs
(`value`/`onChange`), immutable updates with the spread operator and
`filter`/`map`, and passing an `onDelete(id)` callback to children.

**Build outline.**

1. Build three components: `App` (owns the notes array), `CreateArea` (the form),
   and `Note` (one card).
2. Hold `notes` in `App` via `useState([])`. Render them with
   `notes.map((n) => <Note key={n.id} ... />)`.
3. `CreateArea` keeps its own controlled state for title/content, and on submit
   calls an `onAdd` prop passed from `App`.
4. `App`'s add handler appends immutably: `setNotes((prev) => [...prev, newNote])`.
5. `Note` gets an `onDelete` prop; clicking delete calls `onDelete(id)`, and `App`
   removes it with `setNotes((prev) => prev.filter((n) => n.id !== id))`.
6. Give each note a stable id (a counter or `crypto.randomUUID()`), not the array
   index, for its key.

```jsx
function App() {
  const [notes, setNotes] = useState([]);
  const addNote = (note) => setNotes((prev) => [...prev, note]);
  const deleteNote = (id) =>
    setNotes((prev) => prev.filter((n) => n.id !== id));
  return (
    <>
      <CreateArea onAdd={addNote} />
      {notes.map((n) => (
        <Note key={n.id} note={n} onDelete={deleteNote} />
      ))}
    </>
  );
}
```

**Why it matters:** state lives in the common parent (`App`) because both the form
and the list need it. Children stay "dumb" — they receive data and report events
up through callbacks.

### DBANK / Token DApp (Internet Computer, Motoko)

**What it teaches.** Building a decentralised app: writing backend logic as a
**canister** smart contract in Motoko, persisting state on-chain, exposing update
and query methods, and calling them from a web frontend. DBANK is a simple
interest-bearing balance; the token project extends it to transferable balances
and ownership. This is the Web3 capstone from Chapter 6.

**Key concepts / APIs.** The `dfx` CLI (`dfx start`, `dfx deploy`), Motoko `actor`
canisters, `stable` variables for upgrade-safe state, `public func` (update) vs
`public query func` (fast read-only), the `Principal` type for identity, a
`HashMap` for balances, and the generated JS actor used from the frontend. State
version assumption: dfx / DFINITY SDK as of 2026.

**Build outline (DBANK).**

1. Define an `actor` with a `stable var currentValue : Float`.
2. Add update methods `topUp(amount)` and `withdraw(amount)` that mutate
   `currentValue` (guard withdraw against overdraft).
3. Add a `query func checkBalance()` returning `currentValue` for cheap reads.
4. Optionally compute compound interest based on elapsed time on each call.
5. Deploy locally with `dfx deploy`; call the methods from an HTML/JS frontend
   through the generated actor.

**Build outline (Token).**

1. Keep balances in a `HashMap<Principal, Nat>` and a `stable` owner principal.
2. On first deploy, mint the supply to the owner.
3. Add `balanceOf(who)` as a query, and `transfer(to, amount)` as an update that
   checks the caller's balance via `msg.caller` before moving funds.
4. Expose a faucet or claim method for the demo, then wire buttons in the frontend
   to the actor's methods.

```motoko
actor DBank {
  stable var currentValue : Float = 0;

  public func topUp(amount : Float) : async () {
    currentValue += amount;
  };

  public query func checkBalance() : async Float {
    return currentValue;
  };
};
```

**Gotcha:** mark persistent fields `stable`, or their values reset on every
canister upgrade. Use `query` methods for reads (fast, not consensus-committed)
and plain `public func` for state changes; a `HashMap` itself is not stable, so
serialise it to a stable array in `preupgrade`/`postupgrade` hooks.

## Cheatsheet

| Project | Core API / idea |
|---|---|
| Dice Game | `Math.floor(Math.random()*6)+1`, set `.src` |
| Drum Kit | `addEventListener`, `new Audio().play()` |
| Simon | sequence array + index, state machine |
| Personal Site | semantic HTML, Flexbox, media query |
| Blog | Express routes, EJS `res.render` |
| To-Do List | `pool.query("... $1", [val])` CRUD |
| Secrets | bcrypt + session + Passport + OAuth |
| Keeper | lift state, props down, callbacks up |
| DBANK / Token | Motoko `actor`, `stable`, `query func` |
| Escape HTML in EJS | `<%= value %>` not `<%- value %>` |
| React immutable add | `setX(prev => [...prev, item])` |
| React immutable remove | `prev.filter(x => x.id !== id)` |
| Deploy canister | `dfx start` then `dfx deploy` |

## Common mistakes

- Off-by-one in the dice roll: multiplying `Math.random()` by 6 but forgetting
  `+ 1`, so you can never roll a 6 (or you index a missing image).
- Attaching the drum handler to only one button instead of looping the whole
  NodeList, or forgetting the document-level `keydown` listener.
- In Simon, comparing the entire pattern instead of just the index the player
  clicked, so you miss a wrong press until the round ends.
- Styling a personal site before writing semantic HTML, ending up with div soup
  that is hard to lay out and inaccessible.
- Forgetting `express.urlencoded` in the Blog app, so `req.body` is undefined on
  form posts; or not redirecting after POST, causing resubmits on refresh.
- Concatenating user input into SQL in the To-Do app instead of using `$1`
  placeholders (SQL injection).
- Putting the OAuth client secret or code exchange in the browser, or placing the
  session middleware after Passport in the Secrets app.
- Mutating React state directly in Keeper (`notes.push(...)`) instead of setting a
  new array; using the array index as a `key`.
- Not marking Motoko persistent state `stable`, so balances reset on every
  canister upgrade.

## Quick self-check

1. Why does the dice roll add `+ 1` after `Math.floor(Math.random() * 6)`?
2. In the Drum Kit, how do you make one handler serve both clicks and key presses?
3. In Simon, which index should you compare on each player click, and why?
4. Why write semantic HTML before CSS on the personal site?
5. What middleware lets the Blog app read `req.body` from a form POST, and why
   redirect after a POST?
6. How does the To-Do app avoid SQL injection when inserting a title?
7. In the Secrets app, where must the OAuth code exchange happen, and why?
8. In Keeper, where does the notes array live and how do you add one immutably?
9. What does the `stable` keyword do in a Motoko canister?
10. What is the difference between a Motoko `query func` and a plain `public func`?

### Answers

1. `Math.random()` returns `[0, 1)`, so `floor(*6)` gives 0-5; adding 1 shifts it
   to 1-6, matching the dice faces.
2. Write one `play(key)` function and call it from both a click listener on each
   button and a single `keydown` listener on the document.
3. The index of the button the player just clicked
   (`userPattern.length - 1`), so a wrong press is caught immediately rather than
   at the end of the sequence.
4. Correct semantic structure makes the CSS simpler, keeps the page accessible,
   and reads sensibly even before any styling is applied.
5. `express.urlencoded({ extended: true })` parses form bodies into `req.body`.
   Redirecting after POST follows the Post/Redirect/Get pattern so a refresh
   doesn't resubmit the form.
6. It uses parameterised queries with `$1` placeholders and passes values in an
   array, so the driver escapes them instead of concatenating into the SQL string.
7. On the server. The client secret and the one-time code must never be exposed in
   the browser; only the server exchanges the code for tokens.
8. In the parent `App` component via `useState`. Add immutably with
   `setNotes(prev => [...prev, newNote])` rather than mutating the array.
9. It marks a variable's value to be preserved across canister upgrades; without
   it the value resets to its initial state on redeploy.
10. A `query func` is read-only and fast (not consensus-committed), while a plain
    `public func` can change state and goes through consensus.
