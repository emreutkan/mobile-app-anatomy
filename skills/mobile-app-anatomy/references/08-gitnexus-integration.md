# GitNexus Integration

## What GitNexus contributes

GitNexus provides a persistent local knowledge graph built from repository structure and Tree-sitter parsing. Use it to supplement—not replace—line-shard reading.

Useful capabilities:

- repository and symbol search
- callers/callees and imports
- functional clusters
- detected execution processes
- blast-radius analysis
- raw graph queries
- change detection
- repo-specific generated skills

## Installation and setup

From the repository root:

```bash
npm install -g gitnexus@latest
gitnexus setup -c cursor,codex
gitnexus analyze --force --embeddings --skills
```

Or use `npx gitnexus ...`.

For mobile repositories, do not set:

```text
GITNEXUS_SKIP_OPTIONAL_GRAMMARS=1
```

That setting skips Dart, Swift, and Kotlin grammars.

If the installed version supports it and the relevant code is TypeScript/JavaScript:

```bash
gitnexus analyze --force --embeddings --skills --pdg
```

Control/data-dependence analysis is version- and language-dependent. Record what was actually available.

## Required graph queries

At the start:

- read repository context
- list clusters
- list processes
- inspect schema

For every significant symbol:

- obtain context
- inspect callers/callees
- inspect process participation
- compare graph relationships with manual findings

For every feature:

- query by domain concepts and user-facing copy
- inspect relevant processes
- trace from UI handler toward state/service/persistence
- trace reverse consumers for state and services

## GitNexus is not completion proof

GitNexus can miss or under-resolve:

- dynamic route names
- reflection
- generated registration
- runtime dependency injection
- server-driven UI
- native platform configuration
- asset and localization semantics
- conditional compilation
- feature flags
- weakly resolved Swift imports/calls
- runtime-only state behavior

Therefore:

- never mark a file shard complete only because GitNexus indexed it
- never assume all execution flows were detected
- reconcile graph output with direct source reading
- document graph ambiguities and confidence
- use manual search and framework-aware inspection for negative space

## Large repository operational notes

- Index from repository root.
- Check index freshness before using graph claims.
- Re-index after source changes.
- If MCP serves stale data after rebuilding, restart the client/MCP process.
- Avoid parallel raw graph queries if the installed version is unstable under concurrent calls; serialize graph-heavy work while parallelizing file reading.
- Keep `.gitnexus/` as machine state, not human documentation.
