# Chapter 3: Node.js, Express, EJS and APIs

## What this covers

This chapter maps to the back-end sections of the bootcamp: running JavaScript
outside the browser with Node.js, building an HTTP server with Express (routing,
middleware, static files), rendering dynamic HTML with EJS templates, reading
submitted form data, and calling third-party REST APIs from the server. Version
assumptions (as of 2026): Node.js 20+ LTS, Express 4.x with a note on 5.x, and
EJS 3.x. Native `fetch` is stable in Node 18+, so it is used alongside axios.

## Key concepts

### Node.js and the module system

Node runs JavaScript on the V8 engine outside the browser, so there is no `window`
or `document` but there are `process`, `fs`, and network APIs. Node has two module
styles: CommonJS (`require`/`module.exports`) and ES Modules (`import`/`export`).
CommonJS is still the bootcamp default; ESM is enabled by `"type": "module"` in
`package.json` or a `.mjs` extension.

```js
// math.js (CommonJS)
function add(a, b) {
  return a + b;
}
module.exports = { add };

// app.js
const { add } = require("./math");
console.log(add(2, 3)); // 5
```

**Why it matters:** mixing the two styles in one project is the most common
"Cannot use import statement outside a module" error. Pick one per project.

### npm and package.json

`npm` installs packages into `node_modules` and records them in `package.json`.
Run `npm init -y` to create the manifest, then `npm install express` to add a
dependency. `dependencies` ship to production; `devDependencies` (installed with
`npm install --save-dev nodemon`) are only for development. `package-lock.json`
pins exact versions so installs are reproducible.

```json
{
  "name": "my-app",
  "type": "commonjs",
  "scripts": {
    "start": "node app.js",
    "dev": "nodemon app.js"
  },
  "dependencies": {
    "express": "^4.19.2"
  }
}
```

**Gotcha:** the `^` caret allows minor and patch upgrades. Commit
`package-lock.json` so teammates and CI get identical trees.

### The event loop and non-blocking I/O

Node is single-threaded for your JavaScript but offloads I/O (disk, network,
timers) to the libuv thread pool and the OS. When I/O finishes, its callback is
queued and run when the call stack is clear. This is why Node handles many
concurrent connections cheaply, and why a long synchronous loop blocks
everything.

```js
console.log("first");
setTimeout(() => console.log("third (async)"), 0);
Promise.resolve().then(() => console.log("second (microtask)"));
console.log("first-and-a-half");
// Order: first, first-and-a-half, second, third
```

**Why it matters:** promises (microtasks) run before timers (macrotasks). Never
put heavy CPU work on the main thread of a server; use async APIs or a worker.

### Express: a minimal server

Express is a thin routing and middleware layer over Node's `http` module. You
create an app, attach route handlers, and listen on a port. Each handler receives
`req` (the request) and `res` (the response).

```js
const express = require("express");
const app = express();

app.get("/", (req, res) => {
  res.send("Hello from Express");
});

app.listen(3000, () => console.log("Listening on http://localhost:3000"));
```

**Gotcha:** `res.send()`, `res.json()`, or `res.render()` must be called once per
request. Calling two of them throws "Cannot set headers after they are sent".

### Routing: methods, paths, and params

Routes match an HTTP method plus a path. Path segments starting with `:` become
route parameters on `req.params`; the query string (`?q=cats`) lands on
`req.query`. Order matters: Express tries routes top to bottom and uses the first
match.

```js
app.get("/users/:id", (req, res) => {
  res.send(`User ${req.params.id}, sort=${req.query.sort}`);
});

app.post("/users", (req, res) => {
  res.status(201).send("Created");
});
```

**Why it matters:** put specific routes (`/users/new`) before dynamic ones
(`/users/:id`), or `:id` will greedily capture "new".

### Middleware and the request pipeline

Middleware are functions with the signature `(req, res, next)` that run in order
for matching requests. They can inspect or mutate `req`/`res`, end the response,
or call `next()` to pass control on. This is how logging, parsing, auth, and
error handling are layered.

```js
app.use((req, res, next) => {
  console.log(`${req.method} ${req.url}`);
  next(); // forget this and the request hangs
});

// Error-handling middleware has FOUR args
app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(500).send("Something broke");
});
```

**Gotcha:** an error handler is identified by its four parameters. Drop the
unused `next` and Express treats it as a normal middleware.

### Serving static files

`express.static` serves a folder of assets (CSS, images, client JS) directly.
Files are exposed at the URL path relative to that folder root, not the folder
name.

```js
app.use(express.static("public"));
// public/styles/main.css -> http://localhost:3000/styles/main.css
```

**Why it matters:** never hardcode `public/` into links; the middleware strips
it. Use a mount path (`app.use("/static", express.static("public"))`) if you
want a prefix.

### EJS: rendering dynamic HTML

EJS (Embedded JavaScript) lets you inject server data into HTML templates. Set
the view engine, keep templates in a `views/` folder with a `.ejs` extension, and
call `res.render("name", dataObject)`. `<%= %>` outputs an escaped value,
`<%- %>` outputs raw (unescaped) HTML, and `<% %>` runs logic without output.

```js
app.set("view engine", "ejs"); // views/ is the default folder

app.get("/", (req, res) => {
  res.render("index", { title: "Home", items: ["a", "b"] });
});
```

```html
<!-- views/index.ejs -->
<h1><%= title %></h1>
<ul>
  <% items.forEach(item => { %>
    <li><%= item %></li>
  <% }) %>
</ul>
```

**Gotcha:** referencing a variable you did not pass throws `X is not defined`.
Use `typeof x !== "undefined"` or pass a default.

### EJS partials and layout reuse

Repeated markup (header, footer, nav) goes into partial files included with
`<%- include("partials/header") %>`. Partials can receive data by passing a
second argument, which keeps them reusable.

```html
<!-- views/partials/header.ejs -->
<header><nav><a href="/">Home</a></nav></header>

<!-- views/index.ejs -->
<%- include("partials/header") %>
<main><%= content %></main>
<%- include("partials/footer") %>
```

**Why it matters:** use `<%-` (raw) for includes. `<%=` would escape the partial's
HTML and print angle brackets as text.

### Parsing submitted forms

An HTML form POSTs URL-encoded data by default. Express does not read the request
body until you add a body-parsing middleware. `express.urlencoded` handles form
fields; `express.json` handles JSON payloads (typical for API clients). Parsed
fields appear on `req.body`.

```js
app.use(express.urlencoded({ extended: true }));
app.use(express.json());

app.post("/submit", (req, res) => {
  const { username, email } = req.body;
  res.send(`Got ${username} / ${email}`);
});
```

```html
<form action="/submit" method="POST">
  <input name="username" />
  <input name="email" type="email" />
  <button>Send</button>
</form>
```

**Gotcha:** the input's `name` attribute becomes the `req.body` key. Without
`name`, the field is never submitted. `extended: true` allows nested objects and
arrays via the `qs` library.

### Consuming REST APIs from the server

Calling APIs from the back end (not the browser) keeps API keys secret and avoids
CORS issues. Use native `fetch` (built into Node 18+) or the axios library.
`fetch` does not reject on HTTP error statuses, so check `res.ok` yourself; axios
rejects on 4xx/5xx automatically.

```js
// Native fetch
app.get("/weather", async (req, res) => {
  const r = await fetch("https://api.example.com/now?city=London");
  if (!r.ok) return res.status(r.status).send("API error");
  const data = await r.json();
  res.render("weather", { temp: data.temp });
});
```

```js
// axios (npm install axios)
const axios = require("axios");
const { data } = await axios.get("https://api.example.com/now", {
  params: { city: "London" }
});
```

**Why it matters:** always `await` and wrap in `try/catch`. An unhandled
rejection in a route can crash the process.

### API keys, GET vs POST, and status codes

Most APIs need a key sent as a query parameter or, more securely, an
`Authorization` header. Keep keys in environment variables (`process.env.KEY`)
loaded from a `.env` file with the `dotenv` package, and never commit `.env`. Use
GET to read and POST to create; send POST bodies as JSON with the right
`Content-Type`.

```js
require("dotenv").config(); // loads .env into process.env

const r = await fetch("https://api.example.com/items", {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
    Authorization: `Bearer ${process.env.API_KEY}`
  },
  body: JSON.stringify({ name: "Widget" })
});
```

**Gotcha:** a 401 means the key is missing or wrong; 403 means the key is valid
but not allowed; 429 means you are rate-limited. Read the status before the body.

## Cheatsheet

| Task | Command / syntax |
|---|---|
| Init project | `npm init -y` |
| Add dependency | `npm install express` |
| Add dev dependency | `npm install --save-dev nodemon` |
| Run with auto-reload | `npx nodemon app.js` |
| Import (CommonJS) | `const x = require("./x")` |
| Export (CommonJS) | `module.exports = { x }` |
| Create app | `const app = express()` |
| GET route | `app.get("/path", (req, res) => {})` |
| Route param | `req.params.id` |
| Query string | `req.query.sort` |
| Form / JSON body | `req.body.field` |
| Global middleware | `app.use(fn)` |
| Pass control | `next()` |
| Static files | `app.use(express.static("public"))` |
| Parse form | `app.use(express.urlencoded({extended:true}))` |
| Parse JSON | `app.use(express.json())` |
| Set EJS | `app.set("view engine", "ejs")` |
| Render view | `res.render("index", { data })` |
| EJS escaped output | `<%= value %>` |
| EJS raw output | `<%- html %>` |
| EJS logic | `<% if (x) { %> ... <% } %>` |
| EJS include | `<%- include("partials/header") %>` |
| Set status | `res.status(404).send("Not found")` |
| Send JSON | `res.json({ ok: true })` |
| Redirect | `res.redirect("/login")` |
| Env variable | `process.env.API_KEY` |
| Load .env | `require("dotenv").config()` |

## Common mistakes

- Forgetting `next()` in middleware, so the request hangs until it times out.
- Calling `res.send` and `res.render` in the same handler (headers already sent).
- Missing `express.urlencoded`/`express.json`, so `req.body` is `undefined`.
- Placing `/users/:id` before `/users/new`, letting `:id` swallow "new".
- Using `<%=` for an EJS `include`, which escapes and prints the partial's HTML.
- Not checking `res.ok` with `fetch`; a 404 or 500 is treated as success.
- Blocking the event loop with a synchronous loop or `fs.readFileSync` in a route.
- Committing `.env` or hardcoding API keys into source.
- Mixing `require` and `import` in one file without setting the module type.
- Forgetting the `name` attribute on form inputs, so fields never reach the server.

## Quick self-check

1. Which HTTP status code should a successful resource-creation POST return?
2. What is the difference between `<%= %>` and `<%- %>` in EJS?
3. Why does `req.body` come back `undefined` for a submitted form?
4. In what order do a `setTimeout(fn, 0)` callback and a resolved
   `Promise.then` callback run?
5. What does `express.static("public")` change about the URL of
   `public/img/logo.png`?
6. How does native `fetch` signal an HTTP 500, and how does that differ from
   axios?
7. What distinguishes an Express error-handling middleware from a normal one?
8. Where should an API key live, and why not in the source file?
9. What does calling `next()` do inside middleware?

### Answers

1. `201 Created` (optionally with a `Location` header for the new resource).
2. `<%= %>` HTML-escapes the value; `<%- %>` outputs it raw, used for includes
   and trusted HTML.
3. No body-parsing middleware is registered; add
   `express.urlencoded({ extended: true })`.
4. The promise callback (a microtask) runs first, then the timer callback (a
   macrotask).
5. It is served at `/img/logo.png`; the `public` folder name is stripped from
   the URL.
6. `fetch` still resolves on a 500, so you must check `res.ok`; axios rejects the
   promise on 4xx/5xx.
7. It declares four parameters `(err, req, res, next)`; the extra `err` marks it
   as an error handler.
8. In an environment variable loaded from an uncommitted `.env` file, so secrets
   are not exposed in version control or to the browser.
9. It passes control to the next matching middleware or route handler in the
   pipeline.
