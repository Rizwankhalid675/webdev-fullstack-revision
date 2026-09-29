# Chapter 5: Authentication and React

## What this covers

This chapter maps to the authentication and React sections of the bootcamp. The
first half covers how to store passwords safely with hashing, the difference
between server-side sessions and JSON Web Tokens, wiring up Passport.js with a
local username/password strategy, keeping secrets out of source control, and a
high-level look at OAuth "Log in with Google". The second half switches to the
front end: React 18 fundamentals — JSX, components, props, state with `useState`,
side effects with `useEffect`, event handling, rendering lists with keys,
controlled forms, conditional rendering, and why modern React uses hooks instead
of class components.

## Key concepts

### Never store plaintext passwords — hash with bcrypt

A password database should never contain the actual passwords. If it leaks, every
account is compromised. Instead you store a one-way hash. bcrypt is a slow,
salted hashing algorithm designed exactly for this: the salt defends against
rainbow tables, and the deliberate slowness defends against brute force. The
"cost factor" (salt rounds) controls how slow; 10-12 is a sensible default as of
2026.

```js
import bcrypt from "bcrypt";

const SALT_ROUNDS = 12;

// On registration: hash before saving
const hash = await bcrypt.hash(plainPassword, SALT_ROUNDS);
await User.create({ email, password: hash });

// On login: compare, never decrypt (bcrypt is one-way)
const user = await User.findOne({ email });
const ok = user && (await bcrypt.compare(plainPassword, user.password));
```

**Why it matters:** `bcrypt.compare` re-hashes the input with the stored salt and
checks in constant time. You never reverse a hash — there is no `bcrypt.decrypt`.

### Sessions vs JWT — two ways to stay logged in

HTTP is stateless, so after login you need a way to remember who the user is on
the next request. Two common approaches:

- **Sessions (stateful):** the server stores session data (e.g. in memory, Redis,
  or Mongo) and sends the client a signed cookie holding only a session ID. Each
  request looks the ID up server-side. Easy to revoke (delete the record), but
  the server must keep state.
- **JWT (stateless):** the server signs a token containing the user's claims and
  sends it to the client. The client returns it on each request; the server
  verifies the signature and trusts the payload without a lookup. Scales well,
  but hard to revoke before expiry.

```js
import jwt from "jsonwebtoken";

// Issue a token at login
const token = jwt.sign({ sub: user.id }, process.env.JWT_SECRET, {
  expiresIn: "1h",
});

// Verify on a protected route
const payload = jwt.verify(token, process.env.JWT_SECRET); // throws if invalid
```

**Gotcha:** a JWT payload is only base64-encoded, not encrypted — anyone can read
it. Never put secrets in it, and always check the signature before trusting it.
For revocation, keep tokens short-lived and pair them with a refresh token.

### Passport.js local strategy

Passport is authentication middleware for Express. A "strategy" is a plug-in for
one login method; the local strategy handles username/password. You give Passport
a verify callback, and it calls `done(err, user)` with the result. Passport then
manages the logged-in user, typically on the session.

```js
import passport from "passport";
import { Strategy as LocalStrategy } from "passport-local";

passport.use(
  new LocalStrategy({ usernameField: "email" }, async (email, pw, done) => {
    try {
      const user = await User.findOne({ email });
      if (!user) return done(null, false, { message: "No user" });
      const ok = await bcrypt.compare(pw, user.password);
      return ok ? done(null, user) : done(null, false);
    } catch (err) {
      return done(err);
    }
  })
);

// Store user id in the session, and reload the user from it
passport.serializeUser((user, done) => done(null, user.id));
passport.deserializeUser(async (id, done) => {
  done(null, await User.findById(id));
});
```

**Why it matters:** `serializeUser` decides what goes into the session (keep it
small — just the id), and `deserializeUser` rehydrates the full user on each
request. Wire it up with `app.use(passport.initialize())` and
`app.use(passport.session())` after your session middleware.

### Environment secrets — keep keys out of code

Secrets (DB passwords, `JWT_SECRET`, OAuth client secrets, API keys) must never
be committed. Put them in a `.env` file, load them into `process.env`, and add
`.env` to `.gitignore`. Commit a `.env.example` with the keys but no values so
teammates know what to set.

```js
import "dotenv/config"; // loads .env into process.env at startup

const secret = process.env.JWT_SECRET;
if (!secret) throw new Error("JWT_SECRET is not set");
```

```
# .env  (never commit this)
JWT_SECRET=some-long-random-string
GOOGLE_CLIENT_SECRET=xxxx
```

**Gotcha:** anything already pushed to git stays in history even after you delete
it. If a secret leaks, rotate it — don't just remove the line.

### OAuth and "Log in with Google" (high level)

OAuth 2.0 lets a user log in with an existing account (Google, GitHub, etc.)
without giving you their password. At a high level the "authorization code" flow
is:

1. Your app redirects the user to Google with your client ID and requested scopes.
2. The user authenticates with Google and consents.
3. Google redirects back to your callback URL with a one-time **code**.
4. Your server exchanges the code (plus your client secret) for tokens and the
   user's profile, then creates or looks up a local account.

```js
import { Strategy as GoogleStrategy } from "passport-google-oauth20";

passport.use(
  new GoogleStrategy(
    {
      clientID: process.env.GOOGLE_CLIENT_ID,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET,
      callbackURL: "/auth/google/callback",
    },
    async (accessToken, refreshToken, profile, done) => {
      const user = await User.findOrCreateByGoogle(profile);
      done(null, user);
    }
  )
);
```

**Why it matters:** the client secret and the code exchange happen server-side,
never in the browser. Users with Google login have no password row at all, so
your schema should allow accounts without a password hash.

### JSX and components

React UI is built from **components** — functions that return markup. The markup
is **JSX**, which looks like HTML but is really JavaScript: it compiles to
`React.createElement` calls. A component name must be capitalized, and each
component returns a single root element (use a `<>...</>` fragment to avoid an
extra wrapper).

```jsx
function Greeting() {
  const name = "Rizwan";
  return (
    <>
      <h1>Hello, {name}</h1>
      <p>Welcome back.</p>
    </>
  );
}
```

**Gotcha:** JSX uses `className` instead of `class` and `htmlFor` instead of
`for`, because `class`/`for` are reserved words in JavaScript. Curly braces `{ }`
embed any JS expression.

### Props — passing data down

**Props** are the inputs to a component, passed like HTML attributes. They are
read-only: a component must never modify its own props. Data flows one way, from
parent to child.

```jsx
function UserCard({ name, role }) {
  return <div className="card">{name} - {role}</div>;
}

function App() {
  return <UserCard name="Rizwan" role="Full-stack dev" />;
}
```

**Why it matters:** `children` is a special prop holding whatever you nest between
a component's tags, which is how you build wrappers and layouts.

### State and useState

**State** is data a component owns and can change over time; changing it re-renders
the component. In function components you declare state with the `useState` hook,
which returns the current value and a setter.

```jsx
import { useState } from "react";

function Counter() {
  const [count, setCount] = useState(0);
  return <button onClick={() => setCount(count + 1)}>Clicked {count}</button>;
}
```

**Gotcha:** never mutate state directly (`count++`) — always call the setter. When
the next value depends on the previous one, use the functional form
`setCount(c => c + 1)` to avoid stale values, especially inside async code or
multiple updates in one handler.

### useEffect — side effects

`useEffect` runs code after render for things outside React's render flow: data
fetching, subscriptions, timers, manual DOM work. The dependency array controls
when it re-runs, and an optional returned function cleans up.

```jsx
import { useEffect, useState } from "react";

function Profile({ userId }) {
  const [user, setUser] = useState(null);

  useEffect(() => {
    let active = true;
    fetch(`/api/users/${userId}`)
      .then((r) => r.json())
      .then((data) => active && setUser(data));
    return () => {
      active = false; // cleanup: ignore result if unmounted/changed
    };
  }, [userId]); // re-run only when userId changes

  return <p>{user ? user.name : "Loading..."}</p>;
}
```

**Gotcha:** `[]` runs the effect once on mount; omitting the array runs it after
every render (usually a bug). List every value from the component that the effect
uses, or you get stale data. In React 18 Strict Mode (dev only), effects run
twice on mount to surface missing cleanup — that is expected.

### Event handling

React events use camelCase names (`onClick`, `onChange`, `onSubmit`) and take a
function, not a string. You usually pass an inline arrow or a named handler. The
event object is a synthetic wrapper over the native one.

```jsx
function SearchBox() {
  function handleSubmit(e) {
    e.preventDefault(); // stop the browser's full-page reload
    console.log("searching...");
  }
  return <form onSubmit={handleSubmit}><button>Go</button></form>;
}
```

**Why it matters:** pass `onClick={handleClick}`, not `onClick={handleClick()}` —
the second calls the function during render instead of on the click.

### Lists and keys

Render a collection by mapping an array to elements. Each sibling element needs a
stable, unique `key` so React can track items across re-renders efficiently.

```jsx
function TodoList({ todos }) {
  return (
    <ul>
      {todos.map((t) => (
        <li key={t.id}>{t.title}</li>
      ))}
    </ul>
  );
}
```

**Gotcha:** don't use the array index as a key if the list can reorder, filter, or
have items inserted — it causes wrong state to stick to the wrong row. Use a
stable id from the data.

### Controlled forms

In a **controlled** input, React state is the single source of truth: the input's
`value` comes from state and `onChange` updates it. This lets you validate,
format, or disable in real time.

```jsx
function LoginForm() {
  const [email, setEmail] = useState("");

  return (
    <input
      type="email"
      value={email}
      onChange={(e) => setEmail(e.target.value)}
    />
  );
}
```

**Why it matters:** an input with `value` but no `onChange` is read-only and warns
in the console. For several fields, keep an object in state and update by key with
a spread: `setForm({ ...form, [e.target.name]: e.target.value })`.

### Conditional rendering

Show different UI based on state using plain JavaScript: a ternary, `&&`, or an
early `return`. There is no special template syntax.

```jsx
function Status({ user }) {
  return (
    <div>
      {user ? <span>Hi {user.name}</span> : <a href="/login">Log in</a>}
      {user?.isAdmin && <button>Admin panel</button>}
    </div>
  );
}
```

**Gotcha:** with `&&`, a falsy left side that is `0` renders the literal `0`. Guard
with a real boolean (`count > 0 && ...`) rather than `count && ...`.

### Hooks vs class components

React used to require class components (with `this.state`, `setState`, and
lifecycle methods like `componentDidMount`) for anything stateful. Since React
16.8, **hooks** let function components do everything classes did, with less
boilerplate and easier logic reuse via custom hooks. As of 2026, function
components with hooks are the standard; write new code this way and reserve
classes for legacy code or error boundaries.

```jsx
// Modern: function + hooks (preferred)
function Timer() {
  const [n, setN] = useState(0);
  useEffect(() => {
    const id = setInterval(() => setN((x) => x + 1), 1000);
    return () => clearInterval(id);
  }, []);
  return <p>{n}s</p>;
}
```

**Why it matters:** hooks can only be called at the top level of a component (not
inside loops, conditions, or nested functions) and only from React functions.
That "rules of hooks" constraint is what keeps their order stable across renders.

## Cheatsheet

| Task | Syntax / API |
|---|---|
| Hash password | `await bcrypt.hash(pw, 12)` |
| Check password | `await bcrypt.compare(pw, hash)` |
| Sign JWT | `jwt.sign(payload, secret, {expiresIn})` |
| Verify JWT | `jwt.verify(token, secret)` |
| Load env vars | `import "dotenv/config"` |
| Passport local | `new LocalStrategy(opts, verifyCb)` |
| Save to session | `passport.serializeUser(cb)` |
| Protect route | `req.isAuthenticated()` |
| Local state | `const [v, setV] = useState(init)` |
| Update from prev | `setV(prev => prev + 1)` |
| Side effect | `useEffect(fn, [deps])` |
| Effect cleanup | `return () => {...}` inside effect |
| Handle click | `onClick={handler}` |
| Prevent reload | `e.preventDefault()` |
| Render list | `arr.map(x => <li key={x.id}>...)` |
| Controlled input | `value={v} onChange={...}` |
| Conditional | `{cond ? <A/> : <B/>}` or `{cond && <A/>}` |
| Fragment | `<>...</>` |

## Common mistakes

- Storing plaintext or reversible passwords instead of a bcrypt hash.
- Trusting a JWT payload without verifying its signature, or putting secrets in it.
- Committing a `.env` file, then thinking `git rm` erases it from history.
- Forgetting `passport.session()` after the session middleware, so login doesn't
  persist.
- Handling the OAuth code exchange or client secret in the browser instead of the
  server.
- Mutating React state directly (`arr.push(...)`, `count++`) instead of using the
  setter.
- Leaving out the `useEffect` dependency array, causing an effect to run on every
  render.
- Calling a handler during render: `onClick={doThing()}` instead of
  `onClick={doThing}`.
- Using the array index as a `key` in a list that reorders or filters.
- A controlled input with `value` but no `onChange` (read-only warning).
- Calling a hook inside a condition or loop, breaking the rules of hooks.

## Quick self-check

1. Why can't you "decrypt" a bcrypt hash to check a password?
2. What is the main trade-off between server sessions and JWTs?
3. In Passport's local strategy, what do you pass to `done` on a wrong password?
4. What does `serializeUser` decide?
5. If a secret was committed and pushed, is deleting the line enough?
6. Why is `className` used in JSX instead of `class`?
7. What does the `useState` setter do besides changing the value?
8. What does an empty dependency array `[]` mean in `useEffect`?
9. Why should a list `key` be stable rather than the array index?
10. Name one constraint from the rules of hooks.

### Answers

1. bcrypt is one-way; there is no decrypt. `bcrypt.compare` re-hashes the input
   with the stored salt and compares the results.
2. Sessions keep state on the server (easy to revoke, needs storage); JWTs are
   stateless (scale well, hard to revoke before expiry).
3. `done(null, false)` — no error, but no authenticated user (optionally a
   message object as the third argument).
4. What gets stored in the session — keep it minimal, usually just the user's id.
5. No. It stays in git history; you must rotate (change) the secret.
6. `class` is a reserved word in JavaScript, so JSX uses `className`.
7. It triggers a re-render of the component with the new state.
8. Run the effect once after the first render (on mount), and never again.
9. A stable key ties state to the right item when the list reorders or filters;
   an index shifts and attaches state to the wrong row.
10. Only call hooks at the top level of a React function, never inside loops,
    conditions, or nested functions.
