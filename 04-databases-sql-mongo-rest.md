# Chapter 4: Databases (SQL and MongoDB) and REST

## What this covers

This chapter maps to the course sections on SQL and relational
databases, PostgreSQL with the `node-postgres` (`pg`) client, NoSQL
with MongoDB, the Mongoose ODM, and REST API design. The goal is to be
able to model data in both a relational and a document store, run CRUD
from Node, and expose that data through a clean REST API in Express.
Version assumptions (as of 2026): PostgreSQL 16/17, `pg` 8.x,
MongoDB 7/8, Mongoose 8.x, Express 5 (the default on `npm install
express`), Node 20+.

## Key concepts

### Relational model: tables, rows, keys

A relational database stores data as tables (relations). Each row is a
record, each column has a fixed type. A **primary key** uniquely
identifies a row; a **foreign key** in one table points at the primary
key of another, which is how relationships are enforced. The schema is
fixed up front, and the database rejects data that breaks it.

```sql
CREATE TABLE authors (
  id    SERIAL PRIMARY KEY,
  name  VARCHAR(100) NOT NULL,
  email VARCHAR(255) UNIQUE
);

CREATE TABLE books (
  id         SERIAL PRIMARY KEY,
  title      VARCHAR(200) NOT NULL,
  author_id  INTEGER REFERENCES authors(id),
  published  DATE
);
```

Why it matters: constraints (`NOT NULL`, `UNIQUE`, `REFERENCES`) push
data-integrity rules into the database, so bad data cannot be written
even if the app has a bug.

### SQL CRUD

Four statements cover create, read, update, delete. Always filter
`UPDATE` and `DELETE` with a `WHERE` clause or you change every row.

```sql
INSERT INTO authors (name, email)
VALUES ('Ada Byron', 'ada@example.com');

SELECT id, name FROM authors WHERE name LIKE 'A%';

UPDATE authors SET email = 'ada@calc.org' WHERE id = 1;

DELETE FROM authors WHERE id = 1;
```

Gotcha: `SELECT *` returns whatever the schema currently has and pulls
extra bytes over the wire. Name the columns you actually need.

### Filtering, sorting, aggregating

Beyond plain selects, SQL shapes result sets with `WHERE`, `ORDER BY`,
`LIMIT`, and aggregate functions grouped by `GROUP BY`. `HAVING`
filters on an aggregate (you cannot use `WHERE` for that).

```sql
SELECT author_id, COUNT(*) AS book_count
FROM books
GROUP BY author_id
HAVING COUNT(*) > 2
ORDER BY book_count DESC
LIMIT 10;
```

Why it matters: pushing aggregation into SQL is far faster than
pulling every row into Node and counting there.

### Joins

A join combines rows from two tables on a matching condition, usually
a foreign key. An **INNER JOIN** keeps only rows that match on both
sides. A **LEFT JOIN** keeps every row from the left table and fills
NULL where the right side has no match (useful to find records with no
related rows).

```sql
SELECT b.title, a.name AS author
FROM books b
INNER JOIN authors a ON a.id = b.author_id;

-- authors with zero books:
SELECT a.name
FROM authors a
LEFT JOIN books b ON b.author_id = a.id
WHERE b.id IS NULL;
```

Gotcha: forgetting the `ON` condition produces a cross join (every row
paired with every other), which explodes the result size.

### PostgreSQL with node-postgres (pg)

`pg` is the standard PostgreSQL driver for Node. In production use a
**connection Pool**, not a single client: the pool reuses a set of TCP
connections instead of opening one per request. Pass values as a
parameter array (`$1`, `$2`) so `pg` escapes them — never build SQL by
string concatenation.

```js
import pg from "pg";

const pool = new pg.Pool({
  host: "localhost",
  port: 5432,
  database: "library",
  user: "app",
  password: process.env.PGPASSWORD,
});

async function getBooksByAuthor(authorId) {
  const sql = "SELECT title FROM books WHERE author_id = $1";
  const result = await pool.query(sql, [authorId]);
  return result.rows; // array of row objects
}
```

Why it matters: parameterised queries are the primary defence against
SQL injection. The `$1` placeholder keeps user input as data, never as
executable SQL.

### Transactions in pg

When several statements must all succeed or all fail together (for
example, transfer a book and log the move), run them on one client
inside `BEGIN` / `COMMIT`, and `ROLLBACK` on error. A pooled
`pool.query` may use a different connection each call, so check a
single client out of the pool.

```js
const client = await pool.connect();
try {
  await client.query("BEGIN");
  await client.query("UPDATE books SET author_id=$1 WHERE id=$2",
    [2, 10]);
  await client.query("INSERT INTO moves(book_id) VALUES($1)", [10]);
  await client.query("COMMIT");
} catch (err) {
  await client.query("ROLLBACK");
  throw err;
} finally {
  client.release(); // always return it to the pool
}
```

Gotcha: forgetting `client.release()` leaks connections until the pool
is exhausted and every later query hangs.

### MongoDB: documents and collections

MongoDB is a document database. A **document** is a BSON (binary JSON)
object; documents live in **collections** (the loose equivalent of
tables). There is no enforced schema by default, so two documents in
one collection can have different fields. Each document gets an
`_id` (an `ObjectId`) automatically.

```js
// a single document
{
  _id: ObjectId("..."),
  title: "Notes on Computing",
  tags: ["history", "math"],
  author: { name: "Ada Byron", email: "ada@example.com" }
}
```

Why it matters: related data can be **embedded** inside one document
(the author object above), so a common read needs no join. The trade
is duplication if that author appears in many books.

### MongoDB CRUD (native driver)

The core methods are `insertOne`/`insertMany`, `find`/`findOne`,
`updateOne`/`updateMany` (with update operators like `$set`), and
`deleteOne`/`deleteMany`. `find` returns a cursor you turn into an
array.

```js
const books = db.collection("books");

await books.insertOne({ title: "Notes", tags: ["math"] });

const list = await books.find({ tags: "math" }).toArray();

await books.updateOne(
  { title: "Notes" },
  { $set: { published: 1843 } }
);

await books.deleteOne({ title: "Notes" });
```

Gotcha: `updateOne` without an operator like `$set` **replaces** the
whole document with what you pass. Always use `$set` to change a field.

### Mongoose: schemas and models

Mongoose is an ODM (object-document mapper) that adds a schema layer on
top of MongoDB. A **Schema** defines fields, types, defaults, and
validation; a **Model** is the constructor compiled from a schema and
is your handle for querying a collection. Mongoose pluralises and
lowercases the model name for the collection (`Book` -> `books`).

```js
import mongoose from "mongoose";

const bookSchema = new mongoose.Schema({
  title:     { type: String, required: true, trim: true },
  pages:     { type: Number, min: 1 },
  published: { type: Date, default: Date.now },
});

const Book = mongoose.model("Book", bookSchema);

await mongoose.connect("mongodb://127.0.0.1:27017/library");
const b = await Book.create({ title: "Notes", pages: 200 });
```

Why it matters: the schema gives you validation and predictable shapes
in an otherwise schemaless store, so the app can trust its documents.

### Mongoose CRUD and queries

Model methods mirror CRUD: `create`, `find`/`findById`/`findOne`,
`findByIdAndUpdate`, `findByIdAndDelete`. Queries are chainable and
run when awaited.

```js
const recent = await Book
  .find({ pages: { $gte: 100 } })
  .sort({ published: -1 })
  .limit(5);

await Book.findByIdAndUpdate(id, { pages: 250 },
  { new: true, runValidators: true });

await Book.findByIdAndDelete(id);
```

Gotcha: `findByIdAndUpdate` returns the **old** document by default.
Pass `{ new: true }` to get the updated one, and `runValidators: true`
because schema validation does not run on updates otherwise.

### Mongoose relationships with refs

To model relationships across collections, store the related
document's `_id` and mark it with `ref`. Then `populate` swaps the id
for the full document at read time — Mongoose's join-like feature.

```js
const bookSchema = new mongoose.Schema({
  title:  String,
  author: { type: mongoose.Schema.Types.ObjectId, ref: "Author" },
});

const withAuthor = await Book.findById(id).populate("author");
// withAuthor.author is now the full Author document
```

Why it matters: refs + populate keep data normalised (one source of
truth for each author) at the cost of an extra query. Embedding is
faster to read but duplicates data. Choose per access pattern.

### REST: resources, verbs, status codes

REST models an API as **resources** addressed by URLs, acted on with
HTTP verbs. Nouns go in the path, actions come from the method. Use
plural resource names and put ids in the path, not the query string.

```text
GET    /books        list books
POST   /books        create a book
GET    /books/42     read one book
PUT    /books/42     replace book 42
PATCH  /books/42     update part of book 42
DELETE /books/42     delete book 42
```

Status codes signal the outcome: 200 OK, 201 Created (with a
`Location` header), 204 No Content (empty success, e.g. delete),
400 Bad Request, 401 Unauthorized, 403 Forbidden, 404 Not Found,
500 Server Error. Why it matters: correct codes let clients react
without parsing the body.

### Building a REST API in Express

Express maps method + path to handlers. Add `express.json()` to parse
JSON request bodies. Read path params from `req.params`, query filters
from `req.query`, and the parsed body from `req.body`. Send JSON with
`res.status(code).json(...)`.

```js
import express from "express";
const app = express();
app.use(express.json());

app.get("/books", async (req, res) => {
  const books = await Book.find();
  res.json(books);
});

app.post("/books", async (req, res) => {
  const book = await Book.create(req.body);
  res.status(201).location(`/books/${book.id}`).json(book);
});

app.get("/books/:id", async (req, res) => {
  const book = await Book.findById(req.params.id);
  if (!book) return res.status(404).json({ error: "not found" });
  res.json(book);
});

app.listen(3000);
```

Gotcha (Express 5, current as of 2026): a rejected promise in an
`async` handler is now forwarded to error middleware automatically, so
`await` failures no longer crash silently — but you should still add an
error handler `app.use((err, req, res, next) => ...)` to return a clean
500 instead of a stack trace.

## Cheatsheet

| Task | SQL / pg | MongoDB / Mongoose |
|---|---|---|
| Create | `INSERT INTO t ...` | `Model.create({...})` |
| Read all | `SELECT * FROM t` | `Model.find()` |
| Read one | `... WHERE id=$1` | `Model.findById(id)` |
| Update | `UPDATE t SET ...` | `findByIdAndUpdate` |
| Delete | `DELETE FROM t ...` | `findByIdAndDelete` |
| Relate | `FOREIGN KEY` + JOIN | `ref` + `populate` |
| Run query | `pool.query(sql, [])` | `await Model.query` |

| HTTP verb | Purpose | Success code |
|---|---|---|
| GET | read | 200 |
| POST | create | 201 |
| PUT | replace | 200 |
| PATCH | partial update | 200 |
| DELETE | remove | 204 |

| pg / Mongoose bit | Meaning |
|---|---|
| `$1, $2` | pg parameter placeholders |
| `pool.connect()` | check out client (transactions) |
| `{ new: true }` | return updated doc |
| `runValidators: true` | validate on update |
| `$set` | change fields, not replace doc |
| `$gte / $lte / $in` | Mongo comparison operators |

## Common mistakes

- Building SQL by concatenating strings instead of using `$1`
  placeholders — this opens SQL injection.
- `UPDATE` or `DELETE` with no `WHERE`, changing every row.
- Using `pool.query` for a multi-statement transaction; each call may
  land on a different connection. Use a checked-out client.
- Forgetting `client.release()`, leaking pooled connections.
- Mongoose `updateOne`/replace without `$set`, wiping other fields.
- Expecting `findByIdAndUpdate` to return the new doc without
  `{ new: true }`, and to validate without `runValidators: true`.
- Putting verbs in REST paths (`/getBooks`) instead of using the HTTP
  method on a noun (`GET /books`).
- Returning 200 for everything; clients cannot tell created from found
  from failed.
- Forgetting `express.json()`, so `req.body` is `undefined`.

## Quick self-check

1. What is the difference between a primary key and a foreign key?
2. Which join returns authors that have no books, and how?
3. Why pass query values as `[value]` with `$1` instead of inline?
4. When must you use a checked-out client instead of `pool.query`?
5. In MongoDB, what does `updateOne` do if you omit `$set`?
6. What does Mongoose `populate` do, and what is its cost?
7. Which two options does `findByIdAndUpdate` usually need, and why?
8. Which HTTP verb and status code fit "create a new book"?
9. When is 204 the right status code?
10. What middleware makes `req.body` available for JSON requests?

### Answers

1. A primary key uniquely identifies a row in its own table; a foreign
   key stores another table's primary key to link the two.
2. A `LEFT JOIN` from authors to books with `WHERE books.id IS NULL` —
   authors kept, unmatched book side is NULL.
3. The placeholder keeps input as data, so `pg` escapes it and SQL
   injection is prevented; concatenation runs user input as SQL.
4. For a transaction (`BEGIN`/`COMMIT`/`ROLLBACK`), because all
   statements must run on the same connection.
5. It replaces the entire document with what you pass, dropping any
   fields not included.
6. It replaces stored `ObjectId` refs with the full referenced
   documents; the cost is one extra query per populated path.
7. `{ new: true }` to return the updated document and
   `runValidators: true` so schema rules run on the update.
8. `POST /books` returning 201 Created (ideally with a `Location`
   header pointing at the new resource).
9. On a successful request with no body to return, such as a
   `DELETE` or an update that sends nothing back.
10. `express.json()`, registered with `app.use()` before the routes.
