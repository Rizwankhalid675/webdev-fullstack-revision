# Chapter 6: Web3, the Internet Computer and DApps

## What this covers

This chapter revises the final block of the bootcamp (course Sections 37-41): what
Web3 and a decentralised app (DApp) are, the Internet Computer Protocol (ICP) and its
canister smart contracts, the DFINITY SDK and the `dfx` command-line tool, the basics
of the Motoko language, building a first DeFi DApp in the style of the course "DBANK"
(a canister that stores a balance, tops up, withdraws, and pays compound interest on a
timer), deploying to the ICP mainnet at a high level (cycles, wallet, identity), wiring
a React frontend to a canister with the generated actor and `@dfinity/agent`, and
creating a simple crypto token canister. The tooling moves fast, so every command and
syntax note here is checked against the official docs at internetcomputer.org and marked
"as of 2026" where it has changed since the course was recorded.

Important framing before you start: the course was recorded on an older `dfx` and older
Motoko. Several things changed. The three big ones are (1) Motoko actors are now
"persistent" by default with enhanced orthogonal persistence, (2) the old
`system func heartbeat` is superseded by the Timer library, and (3) the old cycles
wallet is being replaced by the cycles ledger and the `dfx cycles` command. Each is
flagged in place below so your revision matches current reality, not the 2021 videos.

## Key concepts

### Web3 in one paragraph

Web1 was read-only pages, Web2 is read-write apps owned by companies (your data and
logic live on their servers), and Web3 is read-write-own: application logic and state
run on a public, decentralised network rather than one company's cloud. In Web3 there is
no single server you rent; code is deployed to many independent nodes that reach
consensus, and users interact with cryptographic identities instead of email-and-password
accounts. The Internet Computer is one such network. Why it matters: the same JavaScript
frontend skills transfer, but the "backend" is now a smart contract you cannot silently
change or take down.

### What a DApp is

A DApp (decentralised application) is an app whose backend logic and data live in smart
contracts on a blockchain, usually with a normal web frontend on top. The frontend can
also be served from the chain, so the whole thing runs without a traditional server.

```text
Browser (React)  ->  Agent (JS)  ->  Canister smart contract (on ICP)
   UI / state        signs calls       logic + persisted state
```

Contrast with a Web2 app: instead of `fetch('/api/balance')` hitting your Express
server, the frontend calls a canister method directly over the IC's protocol. Gotcha:
"decentralised" does not mean "no rules" - you still design an API, you just cannot
patch it as casually, and every state-changing call costs resources (cycles).

### The Internet Computer Protocol (ICP) and canisters

The Internet Computer is a blockchain network run by independent node providers, organised
into subnets, that hosts code and data directly (see internetcomputer.org). Its unit of
deployment is the canister: a smart contract that bundles a WebAssembly (Wasm) module with
its own persistent memory. A canister is like a tiny always-on server with a Candid
interface (its typed API), except it runs on-chain, keeps its state across upgrades, and
is metered in cycles. You can write canisters in Motoko (ICP's native language), Rust, or
any language that compiles to Wasm; the course uses Motoko.

Key properties to remember:

- Canisters communicate by messages; a call is either an update (changes state, goes
  through consensus, slower) or a query (read-only, fast, not consensus-verified).
- Each canister has a principal (its on-chain identity/address).
- Canisters are paid for by cycles, not gas paid by the caller - this is the "reverse
  gas" model, so end users can call your DApp for free.

### The DFINITY SDK and the `dfx` tool

`dfx` is the command-line tool for building, deploying, and managing canisters. As of
2026 you install the IC SDK with the official one-line script from internetcomputer.org
(the older `sh -ci "$(curl ...install.sh)"` DFINITY install command), then `dfx --version`
to confirm; current releases are in the 0.28+ range with Motoko compiler 0.15+.

Core loop: create a project, start a local replica, deploy, then call methods.

```bash
dfx new dbank              # scaffold a project (prompts: language + frontend)
cd dbank
dfx start --background     # run a local replica in the background
dfx deploy                 # create + build + install all canisters locally
dfx canister call dbank topUp   # call a method on the dbank canister
dfx stop                   # shut the local replica down
```

As of 2026 note: `dfx new` now prompts you to choose a backend language (Motoko/Rust)
and a frontend (React, Svelte, Vue, plain JS, or none). `dfx start` uses PocketIC as the
local execution environment (you may see or pass `--pocketic`); older courses show a
different local replica but the commands you type are the same. `dfx deploy` is still the
one command that runs create, build, and install together.

### Candid and `dfx generate`

Candid is the IC's interface description language: it describes a canister's methods and
types in a language-neutral way (a `.did` file) so any client - a Rust canister, a JS
frontend, the `dfx canister call` CLI - can talk to it. From your Motoko actor, `dfx`
produces the Candid automatically. `dfx generate` then produces JavaScript/TypeScript
"declarations" (an `idlFactory` plus a `createActor` helper) that the frontend imports.
Why it matters: you rarely hand-write the wire format; you write Motoko types and the
tooling generates the typed client for you.

### Motoko basics: actors

A Motoko program that becomes a canister is written as an actor. An actor encapsulates
private state and exposes public async methods; only one message runs at a time, so you
do not manage locks. As of 2026 you declare it `persistent actor`, which turns on
enhanced orthogonal persistence: the actor's variables keep their values across upgrades
by default, so you no longer have to mark everything `stable` by hand.

```motoko
import Debug "mo:base/Debug";

persistent actor Counter {
  var count : Nat = 0;        // persists across upgrades (persistent actor)

  public func increment() : async Nat {
    count += 1;
    count
  };

  public query func get() : async Nat {
    count
  };
}
```

As of 2026 change: in the course you will see a plain `actor { ... }` with
`stable var currentValue`. That still compiles, but the modern idiom is
`persistent actor`, where ordinary `var` bindings are already persistent and the
`flexible` keyword (its opposite) has been removed along with the old "classical"
persistence. See internetcomputer.org data-persistence docs.

### Public, query, and update functions

Public functions form the canister's API and must return `async T`. A plain public
function is an update call: it can change state and its result is agreed by consensus. A
`public query func` is read-only and fast, but its result is not consensus-verified, so
never trust a query for anything security-critical (like confirming a payment).

```motoko
public func deposit(amount : Nat) : async () { balance += amount };  // update
public query func balanceOf() : async Nat { balance };              // query
```

Gotcha: a `query` cannot call an update method or perform inter-canister update calls,
and its state changes are discarded when it returns. Use update for writes, query for
cheap reads.

### Motoko types and stable variables

Motoko is strongly, statically typed. Common types: `Nat` (unbounded non-negative int),
`Int`, `Float`, `Bool`, `Text`, `Char`, tuples, `Blob`, `Principal`, plus records
`{ name : Text }`, variants `{ #ok; #err }`, arrays `[Nat]`, and `Option` `?T`. A
"stable variable" is one whose value survives a canister upgrade (new code, same state).

As of 2026: with `persistent actor` every `var` is stable-by-default, so you mostly do
not write the `stable` keyword. You still care about "stable compatibility" on upgrade:
if a variable's type changes incompatibly the upgrade traps. The tooling warns you, and
Motoko supports explicit data migration when you need to reshape state (see the
compatibility docs on internetcomputer.org).

```motoko
persistent actor Store {
  var owner : Text = "rizwan";     // kept across upgrades automatically
  transient var cache : Nat = 0;   // 'transient' = reset on upgrade (opt out)
}
```

### The base vs core standard library

The course imports from `mo:base` (for example `mo:base/Debug`, `mo:base/Float`). As of
2026 there is a new standard library, `mo:core`, that is replacing `base`; new projects
are encouraged to use it (needs dfx 0.28+/moc 0.15+, added via the Mops package manager).
The APIs are similar but not identical - notably `range()` functions in `core` are
exclusive of the upper bound where the old `Iter.range` was inclusive. For revision,
recognise both: examples here use `mo:base` to match the course, but if you start fresh
today prefer `mo:core` and check the "base to core migration guide" on internetcomputer.org.

### Building the DeFi DApp (DBANK style)

The course's DBANK is a canister that holds a balance, lets you top up and withdraw, and
periodically pays compound interest. Here is an original, minimal version using modern
syntax. It stores a single account balance as a `Float`.

```motoko
import Debug "mo:base/Debug";
import Float "mo:base/Float";
import Timer "mo:base/Timer";

persistent actor DBank {
  var balance : Float = 300.0;
  let rate : Float = 0.01;   // 1% interest per period

  public func topUp(amount : Float) : async () {
    balance += amount;
    Debug.print("Topped up. Balance = " # Float.toText(balance));
  };

  public func withdraw(amount : Float) : async () {
    if (amount <= balance) {
      balance -= amount;
    } else {
      Debug.print("Insufficient funds");
    };
  };

  public query func checkBalance() : async Float {
    balance
  };

  // Pay compound interest once per period.
  func payInterest() : async () {
    balance += balance * rate;
  };
}
```

Why `Float`: the course uses it for simplicity so you can see decimals. In real DeFi you
use integer base units (like `Nat`, in the smallest denomination) to avoid rounding
errors - floats are fine for learning, not for money.

### Timers instead of heartbeat

The course schedules interest with `system func heartbeat`, which the runtime called on
a fixed, non-adjustable interval. As of 2026 the recommended mechanism is the Timer
library: `Timer.setTimer` for a one-off and `Timer.recurringTimer` for a repeating job,
each returning a `TimerId` you can `cancelTimer`. Heartbeat still exists but timers are
cheaper and let you pick the interval (see the periodic-tasks docs on internetcomputer.org).

```motoko
import Timer "mo:base/Timer";

persistent actor DBank {
  var balance : Float = 300.0;

  func payInterest() : async () { balance += balance * 0.01 };

  // Start a recurring timer when the canister is first installed.
  ignore Timer.recurringTimer<system>(
    #seconds 3600,        // every hour
    payInterest
  );
}
```

Gotcha: a timer set at the top level of the actor body starts on install; after an
upgrade you typically re-arm timers in a post-upgrade hook, because pending timers do not
automatically survive a code upgrade. Keep the interval realistic - every call burns
cycles, so "every second" on mainnet is expensive.

### Deploying to the ICP mainnet (high level)

Local deploys are free; mainnet costs cycles, and cycles come from ICP tokens. As of 2026
the workflow is:

1. Create an identity: `dfx identity new me` then `dfx identity use me`. Your identity is
   a keypair with a principal - the on-chain "who" for your deploys.
2. Get ICP into the account for that identity (buy on an exchange, send to your ledger
   account: `dfx ledger account-id`).
3. Convert ICP to cycles on the cycles ledger: `dfx cycles convert --amount 2 --network ic`.
   Cycles are the "fuel" (stable in value, unlike a volatile gas token).
4. Deploy: `dfx deploy --network ic`. New canisters are funded from your cycles balance.
5. Top up a running canister later with `dfx cycles top-up <amount> <canister> --network ic`.

As of 2026 change: the course uses a cycles wallet (a helper canister that held your
cycles, created via `dfx ledger create-canister` + `dfx identity deploy-wallet`). That
still works, but the cycles ledger (default since dfx 0.22) replaces it, and the cycles
wallet is slated for removal - so learn `dfx cycles ...`. If a wallet is configured dfx
uses it, otherwise it uses the cycles ledger. Also watch the "freezing threshold": a
canister that runs out of cycles is uninstalled and its state is lost, so keep it topped
up.

### Wiring a React frontend to a canister

After `dfx deploy` (or `dfx generate`) you get generated declarations under
`src/declarations/<canister>`. The frontend imports the ready-made `createActor` and the
`canisterId`, and calls canister methods like async functions. Install `@dfinity/agent`
(the low-level agent that encodes/decodes calls) if you construct the actor by hand.

```javascript
// Simple path: use the generated helpers.
import { dbank } from "../declarations/dbank";

async function refresh() {
  const balance = await dbank.checkBalance();  // a query call
  document.getElementById("bal").innerText = balance;
}

async function topUp(amount) {
  await dbank.topUp(Number(amount));           // an update call
  await refresh();
}
```

If you need to control the agent (for example to point at the local replica or attach an
identity) you build the actor yourself:

```javascript
import { Actor, HttpAgent } from "@dfinity/agent";
import { idlFactory } from "../declarations/dbank";

const agent = await HttpAgent.create({ host: "http://127.0.0.1:4943" });
// Local only: trust the replica's root key. Never do this against mainnet.
await agent.fetchRootKey();

const dbank = Actor.createActor(idlFactory, {
  agent,
  canisterId: process.env.CANISTER_ID_DBANK,
});
```

Gotchas: (1) values cross the boundary as Candid, so a Motoko `Nat` may arrive as a
JavaScript `BigInt` - convert before doing math or rendering. (2) `fetchRootKey()` is for
local development only; calling it against mainnet is a security hole. (3) In React,
create the agent/actor inside `useEffect` (or a lazy import) so it does not run during
server-side rendering.

### Creating a simple crypto token canister

A token is just a canister that maps owners to balances and exposes transfer and balance
methods. Here is a stripped-down educational token (not a full standard):

```motoko
import Principal "mo:base/Principal";
import Map "mo:base/OrderedMap";

persistent actor Token {
  let ops = Map.Make<Principal>(Principal.compare);
  var balances = ops.empty<Nat>();
  let owner = Principal.fromText("aaaaa-aa");  // set to your principal

  public shared (msg) func transfer(to : Principal, amt : Nat) : async Bool {
    let from = msg.caller;
    let bal = switch (ops.get(balances, from)) { case null 0; case (?b) b };
    if (bal < amt) return false;
    balances := ops.put(balances, from, bal - amt);
    let toBal = switch (ops.get(balances, to)) { case null 0; case (?b) b };
    balances := ops.put(balances, to, toBal + amt);
    true
  };

  public query func balanceOf(p : Principal) : async Nat {
    switch (ops.get(balances, p)) { case null 0; case (?b) b }
  };
}
```

Note `shared (msg)`: it exposes the caller's principal via `msg.caller`, which is how the
canister knows who is spending. As of 2026, for anything real you should implement the
ICRC-1 standard (the IC's fungible-token standard: transfer, balance, and metadata
methods, with accounts as principal + subaccount), rather than a bespoke interface, so
wallets and exchanges can talk to your token. The course's custom token is a great
teaching model; ICRC-1 is what you ship. See the digital-asset-standards docs on
internetcomputer.org.

## Cheatsheet

| Command / syntax | What it does |
|---|---|
| `dfx new <name>` | Scaffold a project (pick lang + frontend) |
| `dfx start --background` | Run local replica (PocketIC) in background |
| `dfx stop` | Stop the local replica |
| `dfx deploy` | Create + build + install all canisters (local) |
| `dfx deploy --network ic` | Deploy to mainnet |
| `dfx canister call <c> <m>` | Call method `m` on canister `c` |
| `dfx generate` | Emit JS/TS declarations for frontends |
| `dfx identity new/use <id>` | Create / switch identity (keypair) |
| `dfx cycles convert --amount N` | Turn ICP into cycles (cycles ledger) |
| `dfx cycles top-up N <canister>` | Add cycles to a running canister |
| `dfx ledger account-id` | Show your ICP ledger account |
| `persistent actor { ... }` | Canister with persist-by-default state |
| `var x : Nat = 0;` | Persistent field (in persistent actor) |
| `transient var x` | Field reset on upgrade (opt out) |
| `public func f() : async T` | Update method (writes, consensus) |
| `public query func f() : async T` | Read-only fast method |
| `shared (msg) func f()` | Exposes `msg.caller` (Principal) |
| `Timer.recurringTimer<system>(d, job)` | Repeating scheduled task |
| `Timer.setTimer<system>(d, job)` | One-off scheduled task |
| `mo:base/...` / `mo:core/...` | Old / new standard library imports |

| Concept | One-liner |
|---|---|
| Canister | Wasm module + persistent memory = smart contract |
| Principal | On-chain identity/address of caller or canister |
| Cycles | Fuel a canister spends; from converting ICP |
| Reverse gas | Canister pays, so end users call for free |
| Candid (.did) | Language-neutral interface description |
| Update call | Changes state, consensus-verified, slower |
| Query call | Read-only, fast, not consensus-verified |
| ICRC-1 | Standard fungible-token interface on ICP |

## Common mistakes

- Trusting a `query` result for anything security-sensitive - queries are not
  consensus-verified; use an update call to confirm payments or balances.
- Calling `agent.fetchRootKey()` against mainnet. It is local-development only and
  disabling that check on mainnet is a serious security hole.
- Forgetting a `Nat`/`Int` arrives in JavaScript as `BigInt`; doing math or template
  rendering without converting throws or shows the wrong value.
- Using `Float` for real money. It is fine for the DBANK demo but real tokens use integer
  base units to avoid rounding drift.
- Expecting `system func heartbeat` to be the modern way - as of 2026 prefer the Timer
  library, and re-arm timers after an upgrade because pending timers do not survive it.
- Assuming state is safe when cycles run out. A canister below its freezing threshold is
  uninstalled and loses state; keep it topped up.
- Copying old course syntax blindly: `flexible` is removed, actors are `persistent` by
  default, and the cycles wallet is being replaced by the cycles ledger (`dfx cycles`).
- Changing a stable variable's type incompatibly across an upgrade - the upgrade traps
  unless you provide a proper migration.
- Importing generated declarations from the `.dfx` folder in a React app. Import from the
  generated `src/declarations/...` path instead, and build the actor inside `useEffect`.

## Quick self-check

1. What is the difference between an update call and a query call on a canister?
2. What are cycles, and how do you get them?
3. In modern Motoko, what does `persistent actor` change compared to the course's plain
   `actor` with `stable var`?
4. Why should you not use `Float` for a production token balance?
5. What does `shared (msg)` give you inside a public function, and why is it needed for a
   token transfer?
6. Which command turns your Motoko interface into a JS/TS client for the frontend?
7. What replaced `system func heartbeat` for scheduling periodic work, as of 2026?
8. What is `agent.fetchRootKey()` for, and when must you never call it?
9. What is Candid, and what file represents it?
10. What standard should a real fungible token implement on ICP, and why?

### Answers

1. An update call can change state and is agreed by consensus (slower, verifiable); a
   query is read-only, fast, and not consensus-verified, so its result is not trustworthy
   for security-critical decisions.
2. Cycles are the resource a canister spends to run and store data ("fuel"). You get them
   by converting ICP tokens to cycles on the cycles ledger, for example
   `dfx cycles convert --amount 2 --network ic`.
3. With `persistent actor`, enhanced orthogonal persistence is on by default, so ordinary
   `var` fields persist across upgrades without the `stable` keyword; the opposite keyword
   `flexible` has been removed and you use `transient` to opt a field out.
4. Floating-point arithmetic introduces rounding errors; money should be tracked in
   integer base units (smallest denomination) so balances stay exact.
5. `shared (msg)` exposes `msg.caller`, the Principal of whoever called the method. A
   transfer needs to know who is sending so it can debit the correct account.
6. `dfx generate` (it produces the declarations with `idlFactory` and `createActor`;
   `dfx deploy` also generates them).
7. The Timer library: `Timer.setTimer` for one-off and `Timer.recurringTimer` for
   repeating jobs, each returning a cancellable `TimerId`.
8. It fetches the local replica's root key so the agent can verify responses during local
   development. Never call it against mainnet - it disables a real signature check.
9. Candid is the IC's language-neutral interface description language; a canister's
   interface is described in a `.did` file, generated from your Motoko types.
10. ICRC-1 (the IC fungible-token standard). Implementing it lets wallets, exchanges, and
    other canisters interact with your token through a known, common interface.
