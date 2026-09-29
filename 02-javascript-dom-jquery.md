# Chapter 2: JavaScript, the DOM and jQuery

## What this covers

This chapter revises the JavaScript sections of the bootcamp: the language
fundamentals (types, variable declarations, functions, arrays, objects,
loops), the modern ES6+ features you use every day (arrow functions,
template literals, destructuring, spread, modules, promises, async/await),
how JavaScript talks to the page through the DOM (selecting elements,
listening for events, changing the document), and a short tour of jQuery
(selection, events, effects). jQuery is treated as legacy: worth
recognising in old code, but not what you reach for in new projects.
Version note: everything here targets modern browsers and Node 18+ as of
2026, where ES modules and async/await are fully supported.

## Key concepts

### Types and coercion

JavaScript has seven primitive types (`string`, `number`, `boolean`,
`null`, `undefined`, `symbol`, `bigint`) plus `object` (which includes
arrays and functions). Primitives are compared by value; objects by
reference. The trap is coercion: `==` converts operands before comparing,
so prefer `===`.

```js
typeof "hi";        // "string"
typeof null;        // "object"  (a historical bug, but stable)
1 == "1";           // true  -- coerced
1 === "1";          // false -- strict, no coercion
[] == false;        // true  -- avoid; use === and Boolean() explicitly
```

Why it matters: almost every "weird JavaScript" bug is loose equality or
an unexpected coercion. Default to `===` and convert types on purpose with
`Number()`, `String()`, `Boolean()`.

### var, let and const

`var` is function-scoped and hoisted (initialised as `undefined` before
its line runs). `let` and `const` are block-scoped and live in a "temporal
dead zone" until declared, so using them early throws. `const` forbids
reassignment of the binding, not mutation of the object it points at.

```js
function scopeDemo() {
  if (true) {
    var a = 1;    // leaks to the whole function
    let b = 2;    // only inside this block
  }
  console.log(a); // 1
  // console.log(b); // ReferenceError
}

const nums = [1, 2];
nums.push(3);     // fine -- mutating the array
// nums = [4];    // TypeError -- reassigning the binding
```

Gotcha: reach for `const` by default, `let` when you must reassign, and
avoid `var` in new code.

### Functions

Three ways to define them: declarations (hoisted, callable before their
line), expressions (assigned to a variable), and arrow functions (compact,
no own `this`). Functions are first-class values, so you can pass them
around and return them.

```js
function add(a, b) { return a + b; }      // declaration
const mul = function (a, b) { return a * b; }; // expression
const sub = (a, b) => a - b;              // arrow

function greet(name = "world") {          // default parameter
  return `Hello, ${name}`;
}
```

Why it matters: passing functions as arguments (callbacks) is the backbone
of array methods, event handlers, and async code.

### Arrays

Ordered, zero-indexed lists. The high-value methods are the iterators that
return new data instead of mutating: `map`, `filter`, `reduce`, `find`,
`some`, `every`. Mutating methods (`push`, `pop`, `splice`, `sort`) change
in place.

```js
const nums = [5, 2, 8, 1];
const doubled = nums.map(n => n * 2);        // [10, 4, 16, 2]
const evens = nums.filter(n => n % 2 === 0); // [2, 8]
const total = nums.reduce((sum, n) => sum + n, 0); // 16
const first = nums.find(n => n > 4);         // 5
```

Gotcha: `sort()` compares as strings by default, so `[10, 2].sort()` gives
`[10, 2]` unwanted. Pass a comparator: `.sort((a, b) => a - b)`.

### Objects

Key-value collections. Access with dot or bracket notation; bracket lets
you use dynamic or non-identifier keys. Methods are just function-valued
properties, and `this` inside a normal method refers to the object it was
called on.

```js
const user = {
  name: "Rizwan",
  role: "developer",
  greet() { return `Hi, I'm ${this.name}`; },
};

user.name;          // "Rizwan"
user["role"];       // "developer"
const key = "name";
user[key];          // "Rizwan"
Object.keys(user);  // ["name", "role", "greet"]
```

Why it matters: objects model almost everything (config, API responses,
records). Knowing `Object.keys/values/entries` makes iterating them easy.

### Loops

`for` for counting, `for...of` for values of an iterable (array, string,
Map), `for...in` for keys of an object (use sparingly), and `while` for
condition-driven repetition. For arrays, the iterator methods above are
usually clearer than a manual loop.

```js
for (let i = 0; i < 3; i++) { /* 0,1,2 */ }

for (const n of [10, 20, 30]) { /* 10,20,30 */ }

for (const key in { a: 1, b: 2 }) { /* "a","b" */ }
```

Gotcha: `for...in` also walks inherited enumerable keys and gives string
indexes for arrays. Use `for...of` or `Object.keys()` instead.

### Arrow functions and this

Arrows have no own `this`, `arguments`, or `prototype`; they inherit `this`
from the enclosing scope. That makes them ideal for callbacks inside a
method, and wrong as object methods that need their own `this`.

```js
const timer = {
  count: 0,
  start() {
    setInterval(() => { this.count++; }, 1000); // this = timer, correct
  },
};
```

Gotcha: a `const obj = { bad: () => this.x }` arrow method does not see the
object as `this` -- use a normal method there.

### Template literals

Backtick strings with `${}` interpolation and real newlines. They replace
clumsy string concatenation and make small HTML fragments readable.

```js
const name = "Rizwan";
const items = ["a", "b"];
const html = `
  <h1>Hi ${name}</h1>
  <p>${items.length} items</p>
`;
```

Why it matters: cleaner than `"Hi " + name + "..."` and safer to read, so
fewer misplaced-quote bugs.

### Destructuring

Pull values out of arrays or objects into variables in one step. Works in
parameters too, which is the common way to receive an options object.

```js
const [first, second] = [10, 20];        // first=10, second=20
const { name, role = "guest" } = user;   // with a default

function connect({ host, port = 5432 }) { // destructured param
  return `${host}:${port}`;
}
```

Gotcha: destructuring `undefined` throws. Guard with a default:
`function f({ a } = {}) {}`.

### Spread and rest

The `...` operator spreads an iterable into elements/args, or collects the
rest into an array/object. It is the idiomatic way to copy and merge
without mutating.

```js
const a = [1, 2];
const b = [...a, 3];              // [1, 2, 3] -- shallow copy + add
const merged = { ...user, active: true }; // clone object + field

function sum(...nums) {           // rest gathers args
  return nums.reduce((s, n) => s + n, 0);
}
```

Gotcha: spread copies are shallow -- nested objects/arrays are still
shared references.

### Modules

ES modules split code into files with `export` and `import`. Each file has
its own scope; nothing is global. Named exports for many values, one
`default` export per file. In HTML use `<script type="module">`; in Node
use `.mjs` or `"type": "module"` in package.json.

```js
// math.js
export const PI = 3.14159;
export function area(r) { return PI * r * r; }
export default function circumference(r) { return 2 * PI * r; }

// app.js
import circumference, { PI, area } from "./math.js";
```

Why it matters: modules replace the old pattern of many global scripts and
are what every bundler and framework expects.

### Promises

A promise represents a value that arrives later; it is `pending`, then
`fulfilled` or `rejected`. Chain with `.then()` and handle errors with
`.catch()`. `Promise.all` runs several in parallel and resolves when all
finish.

```js
fetch("/api/users")
  .then(res => res.json())
  .then(data => console.log(data))
  .catch(err => console.error("failed:", err));

Promise.all([fetch("/a"), fetch("/b")]).then(([ra, rb]) => { /* both */ });
```

Gotcha: a rejected promise with no `.catch()` becomes an unhandled
rejection. Always terminate a chain with error handling.

### async / await

Syntactic sugar over promises: `await` pauses inside an `async` function
until a promise settles, so async code reads top-to-bottom. Wrap in
`try/catch` for errors.

```js
async function loadUsers() {
  try {
    const res = await fetch("/api/users");
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (err) {
    console.error("failed:", err);
    return [];
  }
}
```

Gotcha: awaiting in a loop serialises requests. For independent calls,
start them together and `await Promise.all([...])`.

### The DOM: selecting elements

The DOM is the browser's live object tree of the page. Modern selection
uses `querySelector` (first match) and `querySelectorAll` (a static
NodeList) with CSS selectors.

```js
const title = document.querySelector("#title");     // by id
const items = document.querySelectorAll(".item");   // NodeList
const nav = document.querySelector("nav > ul");     // any CSS selector
items.forEach(el => console.log(el.textContent));
```

Gotcha: `querySelectorAll` returns a static NodeList, not a live one and
not a real array -- spread it (`[...items]`) if you need `map`/`filter`.

### The DOM: events

Attach handlers with `addEventListener`. The handler gets an `event`
object; `event.target` is the element that triggered it. Use event
delegation (one listener on a parent) for lists that change.

```js
const btn = document.querySelector("#save");
btn.addEventListener("click", (event) => {
  event.preventDefault();          // stop default (e.g. form submit)
  console.log("clicked", event.target);
});

// delegation: one listener handles many children
list.addEventListener("click", (e) => {
  if (e.target.matches("li")) console.log("item:", e.target.textContent);
});
```

Why it matters: `addEventListener` allows many handlers and clean removal,
unlike the old `onclick` attribute.

### The DOM: manipulation

Change content with `textContent` (safe, plain text) or `innerHTML` (parses
HTML -- risky with untrusted input). Change styling with `classList`.
Create and insert nodes with `createElement` and `append`.

```js
el.textContent = "Safe text";
el.classList.add("active");
el.classList.toggle("open");
el.setAttribute("aria-hidden", "true");

const li = document.createElement("li");
li.textContent = "New item";
list.append(li);
```

Gotcha: setting `innerHTML` from user input is an XSS hole. Prefer
`textContent`, or sanitise before inserting HTML.

### jQuery basics (legacy)

jQuery wraps DOM work in a terse `$()` API that smoothed over old browser
differences. Those differences are gone, so new code uses the native DOM.
You still meet jQuery in legacy projects and WordPress themes. Selection
mirrors CSS; `.on()` binds events; effects like `.fadeIn()` animate.

```js
$("#save").on("click", function () {   // select + event
  $(this).addClass("active");          // manipulation
  $(".panel").fadeIn(200);             // effect
  $("#list").append("<li>New</li>");
});
```

Why it matters: recognise it, maintain it, but reach for `querySelector`
and `addEventListener` in anything new -- native APIs now cover what jQuery
was invented to fix.

## Cheatsheet

| Task | Modern JS | jQuery (legacy) |
|---|---|---|
| Select one | `document.querySelector(sel)` | `$(sel)` |
| Select many | `document.querySelectorAll(sel)` | `$(sel)` |
| On click | `el.addEventListener("click", fn)` | `$(el).on("click", fn)` |
| Set text | `el.textContent = s` | `$(el).text(s)` |
| Set HTML | `el.innerHTML = s` | `$(el).html(s)` |
| Add class | `el.classList.add("x")` | `$(el).addClass("x")` |
| Toggle class | `el.classList.toggle("x")` | `$(el).toggleClass("x")` |
| Append node | `parent.append(child)` | `$(parent).append(child)` |
| Show/hide | `el.style.display = "none"` | `$(el).hide()` / `.show()` |
| Fetch data | `await fetch(url)` | `$.ajax({ url })` |

| Feature | Syntax |
|---|---|
| Arrow fn | `const f = (a, b) => a + b;` |
| Template | `` `Hi ${name}` `` |
| Destructure | `const { a, b } = obj;` |
| Spread copy | `const c = [...arr];` |
| Rest param | `function f(...args) {}` |
| Default param | `function f(x = 1) {}` |
| Named export | `export function f() {}` |
| Default import | `import f from "./m.js";` |
| Promise chain | `p.then(fn).catch(fn)` |
| Await | `const x = await p;` |
| Map array | `arr.map(x => x * 2)` |
| Filter array | `arr.filter(x => x > 0)` |
| Reduce array | `arr.reduce((s, x) => s + x, 0)` |

## Common mistakes

- Using `==` instead of `===`, then chasing a coercion bug.
- Declaring with `var` and leaking a variable out of its block.
- Reassigning a `const` object versus mutating it -- only reassign throws.
- Using an arrow function as an object method that needs its own `this`.
- Forgetting `sort()` compares as strings; always pass a comparator.
- Treating a NodeList like an array; spread it first for `map`/`filter`.
- Setting `innerHTML` from user input and opening an XSS hole.
- Leaving a promise chain without `.catch()` (unhandled rejection).
- Awaiting inside a loop for independent calls instead of `Promise.all`.
- Reaching for jQuery in new code when native DOM APIs already suffice.

## Quick self-check

1. What does `typeof null` return, and why is that surprising?
2. Give the one-line rule for choosing `const`, `let`, or `var`.
3. Why does `[10, 2].sort()` produce `[10, 2]`, and how do you fix it?
4. When is an arrow function the wrong choice for a method?
5. What is the difference between `textContent` and `innerHTML`?
6. Why prefer event delegation for a list whose items change?
7. What does `Promise.all` do, and when do you use it over sequential awaits?
8. Name two things ES modules give you over old global `<script>` tags.
9. Is `querySelectorAll`'s result a real array? What do you do about it?
10. Why is jQuery considered legacy in 2026?

### Answers

1. `"object"` -- a long-standing bug in the language kept for compatibility.
   Check for null explicitly with `x === null`.
2. Default to `const`; use `let` only when you must reassign; avoid `var`.
3. `sort()` converts elements to strings, so "10" sorts before "2". Pass a
   numeric comparator: `.sort((a, b) => a - b)`.
4. When the method needs its own `this` bound to the object; arrows inherit
   `this` from the surrounding scope instead.
5. `textContent` sets plain text safely; `innerHTML` parses the string as
   HTML, which is powerful but an XSS risk with untrusted input.
6. One listener on the parent handles current and future children and costs
   less than binding a handler to every item.
7. It runs several promises in parallel and resolves when all fulfil (or
   rejects on the first failure). Use it for independent async calls.
8. Per-file scope (no globals) and explicit `import`/`export` dependencies;
   also static analysis and tree-shaking by bundlers.
9. No -- it is a static NodeList. Spread it into an array (`[...nodes]`) or
   use `Array.from` to get `map`/`filter`/`reduce`.
10. Native APIs (`querySelector`, `addEventListener`, `fetch`, `classList`)
    and modern syntax now cover what jQuery was built to smooth over, so it
    adds weight without unique value in new projects.
