# Full-Stack Web Development — Revision Guide

A concise, original revision companion covering the full stack: HTML/CSS/Bootstrap, JavaScript/DOM, Node/Express/EJS, databases (SQL + MongoDB), authentication, React, Web3/Internet Computer DApps, web design theory, and the command-line/Git/deployment toolchain.

> Prepared with AI assistance (Claude) as a personal revision aid. Explanations and code examples are original — this is **not** a copy of any course's material. Written to revise concepts fast, not to reproduce lectures.

## Contents

| Chapter | Topics |
|---|---|
| 1 | HTML, CSS, Flexbox/Grid, responsive design, Bootstrap 5 |
| 2 | JavaScript (ES6+), the DOM, events, jQuery |
| 3 | Node.js, Express routing/middleware, EJS, consuming REST APIs |
| 4 | SQL & PostgreSQL, MongoDB & Mongoose, designing a REST API |
| 5 | Auth (bcrypt, sessions, JWT, Passport, OAuth), React |
| 6 | Web3, Internet Computer, canisters, Motoko, DApps |
| 7 | Web design theory: colour, typography, UI/UX |
| 8 | Command line, Git & GitHub, deployment |
| 9 | Projects & challenges recap |

The full guide is compiled to [`webdev-bootcamp-revision-guide.pdf`](webdev-bootcamp-revision-guide.pdf) (66 pages).

## How it's organised

Each chapter follows the same shape: **What this covers → Key concepts** (short explanation + small original code block each) **→ Cheatsheet** (compact tables) **→ Common mistakes → Quick self-check** (Q&A). Read the cheatsheets alone for a fast pre-interview refresh.

## Rebuild the PDF

```
pip install reportlab
python build_pdf.py
```

The builder reads the `0*.md` chapter files and writes `webdev-bootcamp-revision-guide.pdf`.

## Disclaimer

Study aid only, provided as-is. Not affiliated with or endorsed by any course provider. Written to teach concepts in the author's own words for personal revision.
