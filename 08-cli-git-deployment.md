# Chapter 8: Command Line, Git, GitHub and Deployment

## What this covers

This chapter maps to the tooling sections of the bootcamp: driving your machine
from a Unix-style shell, tracking your work with Git, collaborating through
GitHub, and getting projects onto the public web. It covers bash navigation and
file commands, the Git commit workflow and branching, the GitHub remote model
(clone, push, pull, fork, pull requests), and deployment of both static sites
(GitHub Pages) and dynamic Node/Express apps (a host such as Render or Railway),
plus environment variables in production and the idea of CI. Version assumptions
(as of 2026): Git 2.40+ (so `git switch`/`git restore` and `git init -b` exist),
a POSIX shell (bash or zsh; on Windows use Git Bash or WSL), and Node.js 20+ LTS.

## Key concepts

### The shell, the prompt, and paths

A shell is a text program that reads commands and runs them. The prompt usually
ends in `$` and shows your current directory. Paths are either absolute (start
at the root `/`, e.g. `/home/riz/site`) or relative to where you are now. Three
shorthands appear everywhere: `.` is the current directory, `..` is the parent,
and `~` is your home directory.

```bash
pwd            # print working directory (where am I?)
cd ~/projects  # go to projects inside home
cd ..          # go up one level
cd -           # jump back to the previous directory
```

**Why it matters:** almost every command acts on "where you are now". If a file
is not found, check `pwd` first before assuming the command is broken.

### Listing and inspecting directories

`ls` lists what is in a directory. Flags stack: `-l` for a long listing with
permissions and sizes, `-a` to include dotfiles (hidden files starting with
`.`), and `-h` for human-readable sizes. Add a path to list somewhere else
without moving there.

```bash
ls              # names only
ls -la          # long listing, including hidden files like .git and .env
ls -lh ~/logs   # long, human sizes, in another folder
```

**Gotcha:** files starting with a dot (`.gitignore`, `.env`) are hidden from a
plain `ls`. You must pass `-a` to see them, which is exactly where config lives.

### Creating files and folders

`mkdir` makes a directory; add `-p` to create nested parents in one go. `touch`
creates an empty file (or updates a file's timestamp if it already exists), handy
for stubbing out files before you edit them.

```bash
mkdir my-app
mkdir -p my-app/src/components   # makes every missing level
touch my-app/index.html my-app/app.js
```

**Why it matters:** without `-p`, `mkdir a/b/c` fails if `a` or `b` does not yet
exist. `-p` also stays silent if the folder is already there, which is safe in
scripts.

### Copying, moving, and renaming

`cp` copies, `mv` moves. There is no separate "rename" command: moving a file to
a new name in the same folder is a rename. Copying a folder needs `-r`
(recursive). Both overwrite the destination silently unless you add `-i` to be
prompted.

```bash
cp index.html backup.html        # copy a file
cp -r src src-old                # copy a whole folder
mv draft.md notes.md             # rename (same folder)
mv notes.md docs/                # move into docs/
```

**Gotcha:** `mv a b` where `b` already exists overwrites `b` with no warning.
Use `mv -i` (interactive) when the target might exist and you care about it.

### Deleting files (carefully)

`rm` deletes a file; `rm -r` deletes a folder and everything in it. There is no
recycle bin: deletion is immediate and permanent. `rmdir` removes only an empty
directory, which is a safer way to clear out folders you expect to be empty.

```bash
rm old.log                # delete one file
rm -r build/              # delete a folder and its contents
rmdir empty-folder        # only works if it is truly empty
```

**Why it matters:** `rm -rf` forces deletion without prompts and is the classic
foot-gun. Double-check the path, and never run it against `/` or `~` in anger.

### Viewing file contents

`cat` dumps a whole file to the screen, good for short files or feeding into a
pipe. `less` opens a scrollable pager for long files (arrow keys or space to
page; `q` to quit; `/word` to search). `head` and `tail` show the first or last
lines, and `tail -f` follows a file live, which is how you watch logs.

```bash
cat package.json          # print the whole file
less server.log           # scroll a long file, press q to exit
head -n 20 data.csv       # first 20 lines
tail -f server.log        # follow new log lines as they arrive
```

**Gotcha:** `cat` on a huge file floods your terminal. Reach for `less` when you
are not sure how big the file is.

### Pipes and redirection

Every command has a standard output (stdout) and can take standard input
(stdin). A pipe `|` feeds one command's output into the next. Redirection sends
output to a file instead of the screen: `>` overwrites, `>>` appends, and `<`
reads input from a file. These compose small tools into bigger ones.

```bash
ls -la | grep ".js"          # list, keep only lines mentioning .js
cat access.log | wc -l       # count the lines in the file
echo "PORT=3000" > .env      # write (overwrites the file)
echo "KEY=abc" >> .env       # append a second line
```

**Why it matters:** `>` clobbers the file silently, so a typo can wipe a file's
contents. Use `>>` when you mean to add to what is already there.

### What Git is and initialising a repo

Git is a distributed version control system: it records snapshots of your project
over time so you can review history, undo changes, and collaborate. `git init`
turns a folder into a repository by creating a hidden `.git` directory. Set your
name and email once so commits are attributed to you.

```bash
git config --global user.name "Rizwan Khalid"
git config --global user.email "you@example.com"

cd my-app
git init -b main    # initialise with the default branch named main
```

**Gotcha:** `.git` holds the entire history. Deleting it (or copying a folder
without it) discards all version history and leaves a plain directory.

### The three areas and the commit workflow

Git has three states: the working directory (your files), the staging area (the
index, what will go into the next commit), and the repository (committed
history). `git add` stages changes; `git commit` records the staged snapshot with
a message. `git status` shows what is staged, modified, or untracked.

```bash
git status               # what changed and what is staged
git add index.html       # stage one file
git add .                # stage everything in the current folder
git commit -m "Add landing page markup"
```

**Why it matters:** staging lets you craft a commit from only some of your
changes. A commit should be one logical unit of work with a clear message, not a
dump of everything you touched all day.

### Viewing and reading history

`git log` lists commits newest first, each with a hash, author, date, and
message. It is verbose by default; `--oneline` compresses each commit to one
line, and `--graph` draws the branch structure. Every commit has a unique hash
you can use to refer back to it.

```bash
git log                      # full history
git log --oneline --graph    # compact, with branch lines
git show <hash>              # see the full diff of one commit
git diff                     # unstaged changes vs the last commit
```

**Gotcha:** `git diff` shows only unstaged changes. Once you `git add`, use
`git diff --staged` to review what is actually about to be committed.

### .gitignore

Some files should never be committed: secrets (`.env`), dependencies
(`node_modules`), build output, and OS/editor cruft. List them in a `.gitignore`
file and Git will not track them. Patterns match names and paths; a trailing
slash means a directory.

```gitignore
node_modules/
.env
dist/
*.log
.DS_Store
```

**Why it matters:** `.gitignore` only stops Git from tracking *new* files. If a
file is already committed, you must `git rm --cached <file>` to stop tracking it,
then commit that removal. This is the usual fix for an accidentally committed
`.env`.

### Branches

A branch is a movable pointer to a line of development. You work on a feature
branch so `main` stays stable, then merge when the work is done. `git branch`
lists or creates branches; modern Git uses `git switch` to move between them
(`checkout` still works and does more besides).

```bash
git branch                       # list branches (* marks the current one)
git switch -c feature/login      # create and switch to a new branch
git switch main                  # go back to main
git branch -d feature/login      # delete a merged branch
```

**Gotcha:** `git switch -c` both creates and switches. Plain `git branch name`
creates a branch but leaves you where you are, which surprises people.

### Merging

Merging brings the commits from one branch into another. Switch to the branch you
want to merge *into* (usually `main`), then `git merge` the feature branch. If the
two branches changed the same lines, Git reports a conflict you must resolve by
hand, then commit.

```bash
git switch main
git merge feature/login          # bring the feature into main
# on conflict: edit the marked files, then:
git add <resolved-file>
git commit                       # completes the merge
```

**Why it matters:** conflict markers (`<<<<<<<`, `=======`, `>>>>>>>`) mark the
competing versions. Delete the markers, keep the right content, and only then
add and commit. Never commit the markers themselves.

### checkout vs switch vs restore

Older tutorials use `git checkout` for everything: changing branches, creating
them, and discarding file changes. Git 2.23 split this into two clearer commands:
`git switch` for branches and `git restore` for files. Knowing both helps when
reading old bootcamp material.

```bash
git switch main                  # (old: git checkout main)
git switch -c new-branch         # (old: git checkout -b new-branch)
git restore app.js               # discard unstaged edits to a file
git restore --staged app.js      # unstage but keep the edits
```

**Gotcha:** `git restore <file>` throws away your uncommitted edits with no undo.
Make sure you really want to discard them before running it.

### Remotes: connecting to GitHub

GitHub hosts a copy of your repo on a server so you can back it up and share it. A
"remote" is a named URL for that copy; the default name is `origin`. You link a
local repo to a GitHub repo you created (empty) with `git remote add`, then push.

```bash
git remote add origin https://github.com/you/my-app.git
git remote -v                    # show configured remotes
git push -u origin main          # first push, sets upstream tracking
```

**Why it matters:** the `-u` (upstream) flag on the first push links your local
`main` to `origin/main`, so afterwards a bare `git push` or `git pull` knows
where to go.

### Cloning, pushing, and pulling

`git clone <url>` downloads an existing remote repo (with full history) and wires
up `origin` for you. `git push` uploads your new commits; `git pull` downloads and
merges commits others have pushed. Pull before you start work and before you push
to avoid diverging.

```bash
git clone https://github.com/you/my-app.git
cd my-app
# ...make commits...
git pull                         # get others' changes first
git push                         # send yours up
```

**Gotcha:** if `git push` is rejected because the remote has commits you lack,
run `git pull` (which merges), resolve any conflict, then push again. Never force
push (`--force`) to a shared branch to "fix" this.

### HTTPS vs SSH and authentication

GitHub no longer accepts your account password on the command line. Over HTTPS
you authenticate with a Personal Access Token (PAT) in place of a password, often
cached by a credential helper. Over SSH you generate a key pair and add the
public key to GitHub, then use the `git@github.com:...` URL form.

```bash
# SSH: generate a key, then add ~/.ssh/id_ed25519.pub to GitHub settings
ssh-keygen -t ed25519 -C "you@example.com"
git remote set-url origin git@github.com:you/my-app.git
```

**Why it matters:** a "Support for password authentication was removed" error
means you are using a password where a token or SSH key is required. Generate a
PAT or set up SSH once and it stops.

### Fork and pull request

To contribute to a repo you do not own, you *fork* it: GitHub makes your own copy
under your account. You clone your fork, branch, commit, and push, then open a
*pull request* (PR) asking the original project to merge your branch. Maintainers
review, comment, and merge. This is the standard open-source flow.

```bash
# after forking on github.com and cloning YOUR fork:
git switch -c fix/typo
# ...edit, commit...
git push -u origin fix/typo
# then open a Pull Request on github.com from fix/typo -> upstream main
```

**Gotcha:** keep your fork's `main` in sync by adding the original repo as a
second remote (conventionally `upstream`) and pulling from it, or your PRs will
be based on stale history.

### Deploying a static site with GitHub Pages

GitHub Pages serves static files (HTML, CSS, JS, images) straight from a repo for
free, ideal for portfolios and simple front-ends. Push your site to GitHub, then
in the repo's Settings enable Pages and choose a branch (commonly `main`) and
folder (root or `/docs`). Your site appears at
`https://<user>.github.io/<repo>/`.

```bash
git add index.html style.css
git commit -m "Portfolio site"
git push
# then: repo Settings -> Pages -> Source: main / root
```

**Why it matters:** Pages only serves static assets; there is no server, so it
cannot run Node, Express, or a database. Because the site lives in a subpath,
prefer relative links (`./style.css`, not `/style.css`) so they resolve.

### Deploying a Node/Express app to a host

Dynamic apps need a real server process, so they go to a platform like Render or
Railway (Heroku-style hosts). You connect your GitHub repo; the host installs
dependencies with `npm install`, runs your start script, and gives you a public
URL. Two things your code must do: define a `start` script and read the port from
the environment.

```json
{
  "scripts": { "start": "node server.js" },
  "engines": { "node": "20.x" }
}
```

```js
// server.js — the host assigns a port via an env variable
const port = process.env.PORT || 3000;
app.listen(port, () => console.log(`Listening on ${port}`));
```

**Gotcha:** hard-coding `app.listen(3000)` breaks in production because the host
picks the port for you. Always read `process.env.PORT` with a local fallback.

### Environment variables in production

Secrets (API keys, database URLs, session secrets) must not live in your repo. In
development you keep them in an uncommitted `.env` file loaded by the `dotenv`
package. In production you never upload `.env`; instead you set the same variables
in the host's dashboard (Render/Railway "Environment" settings), and your code
reads them through `process.env` exactly as before.

```js
require("dotenv").config();      // no-op if there is no .env (fine in prod)

const dbUrl = process.env.DATABASE_URL;
const secret = process.env.SESSION_SECRET;
```

**Why it matters:** the same `process.env.X` code works in both places; only the
*source* of the values changes (local file vs host config). Committing `.env`
leaks live credentials, so keep it in `.gitignore` and rotate any key that slips
out.

### Continuous Integration (CI)

CI means automatically running checks (tests, linting, a build) every time you
push or open a PR, so problems are caught before merging. On GitHub this is
GitHub Actions: a YAML file in `.github/workflows/` describes jobs that run on a
fresh machine. A green check on a PR means the pipeline passed; a red X blocks a
careless merge.

```yaml
# .github/workflows/ci.yml
name: CI
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 20 }
      - run: npm install
      - run: npm test
```

**Gotcha:** CI runs on a clean checkout, so anything that only works because of an
untracked local file (like a committed-nowhere `.env` or a stray global package)
will fail in CI even though it "works on my machine". That is the point.

## Cheatsheet

| Task | Command |
|---|---|
| Where am I | `pwd` |
| Change directory | `cd path` (`..` up, `~` home, `-` back) |
| List all + long | `ls -la` |
| Make folder(s) | `mkdir -p a/b/c` |
| Make empty file | `touch file.txt` |
| Copy file / folder | `cp a b` / `cp -r a b` |
| Move or rename | `mv old new` |
| Delete file / folder | `rm f` / `rm -r dir` |
| Print a file | `cat file` |
| Page a long file | `less file` (q to quit) |
| First / last lines | `head -n 20 f` / `tail -n 20 f` |
| Follow a log | `tail -f file` |
| Pipe output | `cmd1 \| cmd2` |
| Redirect / append | `cmd > file` / `cmd >> file` |
| Configure identity | `git config --global user.name "..."` |
| Start a repo | `git init -b main` |
| Status | `git status` |
| Stage | `git add .` |
| Commit | `git commit -m "msg"` |
| History (compact) | `git log --oneline --graph` |
| Diff (staged) | `git diff --staged` |
| New branch + switch | `git switch -c name` |
| Change branch | `git switch main` |
| Merge into current | `git merge feature` |
| Discard file edits | `git restore file` |
| Add remote | `git remote add origin URL` |
| First push | `git push -u origin main` |
| Clone | `git clone URL` |
| Get / send commits | `git pull` / `git push` |
| Stop tracking a file | `git rm --cached file` |

## Common mistakes

- Running a command in the wrong directory; always check `pwd` when a file is
  "missing".
- Forgetting `-a` on `ls`, so hidden files like `.env` and `.gitignore` seem gone.
- `rm -rf` on the wrong path; there is no undo and no recycle bin.
- Using `>` when you meant `>>`, overwriting a file instead of appending.
- Committing `node_modules` or `.env` because no `.gitignore` was added first.
- Thinking `.gitignore` untracks already-committed files; use `git rm --cached`.
- Writing vague commit messages ("fix", "stuff") that say nothing months later.
- Force-pushing a shared branch to resolve a rejected push instead of pulling.
- Deploying static-only GitHub Pages and expecting Express or a database to run.
- Hard-coding `app.listen(3000)` so the app fails on a host that sets `PORT`.
- Uploading `.env` to production instead of setting variables in the host panel.
- Assuming code works in CI because it works locally, ignoring untracked deps.

## Quick self-check

1. What is the difference between an absolute path and a relative path, and what
   do `.`, `..`, and `~` mean?
2. Which `ls` flag reveals hidden dotfiles, and why does it matter for web
   projects?
3. What does `mkdir -p a/b/c` do that plain `mkdir` cannot?
4. What is the difference between `>` and `>>`?
5. Name Git's three areas and the command that moves a change from the first to
   the second.
6. A file you already committed now needs to be ignored. What two steps fix it?
7. You are on `feature`; what sequence merges it into `main`?
8. Why does `git push` sometimes get rejected, and what is the correct fix?
9. What must an Express app do to its port to run on Render or Railway?
10. Where do secrets live in development versus production, and what stays the
    same in the code?

### Answers

1. An absolute path starts at the root `/`; a relative path is resolved from the
   current directory. `.` is the current directory, `..` its parent, and `~` your
   home directory.
2. `-a` (as in `ls -la`) shows dotfiles; config like `.env`, `.gitignore`, and
   `.git` is hidden without it.
3. `-p` creates every missing parent directory in the path and does not error if
   the directory already exists.
4. `>` redirects output to a file, overwriting its contents; `>>` appends to the
   end of the file instead.
5. Working directory, staging area (index), and repository; `git add` moves a
   change from the working directory into staging.
6. Add the file to `.gitignore`, then run `git rm --cached <file>` and commit the
   removal so Git stops tracking it.
7. `git switch main` then `git merge feature`; resolve any conflicts, then
   `git add` and `git commit`.
8. The remote has commits you do not have locally; run `git pull` to merge them
   (resolving conflicts), then `git push` again. Do not force push.
9. Read the port from `process.env.PORT` (with a local fallback) instead of
   hard-coding it, because the host assigns the port.
10. In development they live in an uncommitted `.env` file; in production they are
    set in the host's environment settings. The code reads `process.env.X` the
    same way in both.
