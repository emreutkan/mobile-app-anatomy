# Completion Gates

The analysis is complete only when every mandatory gate passes.

## Gate A — Repository census

Pass conditions:

- every repository path is inventoried or excluded with reason
- every relevant text line belongs to a shard
- current hashes match the analyzed commit/worktree
- no unexplained source extension or app target remains

## Gate B — Source coverage

Pass conditions:

- every non-excluded shard is `tracked_fully`
- every file-synthesis unit is `tracked_fully`
- every report path exists
- every relevant source file has a complete symbol inventory
- changed files have been reprocessed after refresh

## Gate C — Mobile surface coverage

Pass conditions:

- every launcher/background/deep-link/notification/extension entry is documented
- every route/screen/modal/sheet/dialog is an entity
- every navigation call resolves to a documented destination or an explicit dead/invalid edge
- every screen has incoming and outgoing edges, or is explicitly classified as root/terminal/dead
- nested and context-dependent navigators are modeled

## Gate D — Feature coverage

Pass conditions:

- every discovered feature is documented end-to-end
- every UI action has a handler and effect
- every state store/service/API/native module belongs to one or more features
- every permission, notification, purchase, deep link, background task, analytics event, flag, and experiment is owned by documentation
- onboarding inputs are traced to every downstream consumer

## Gate E — State and failure coverage

Pass conditions:

- loading, empty, error, offline, stale, retry, cancellation, and interruption behavior are documented where applicable
- persistence and restoration behavior are mapped
- success and failure terminal states are explicit
- contradictions are resolved or retained as named unresolved contradictions

## Gate F — Runtime coverage

When runtime is required and available:

- required state matrix is executed
- principal screens/actions are observed
- platform-specific branches are tested
- static/runtime disagreements are resolved or documented

When runtime is unavailable:

- exact blockers are documented
- runtime coverage is not represented as complete
- static completion may pass, but overall result must say `static complete; runtime incomplete`

## Gate G — Evidence integrity

Pass conditions:

- evidence paths exist
- line references are within current file bounds
- claims have source or runtime support
- no fabricated rationale
- no “probably,” “likely,” or “appears” presented as fact
- unknowns and exclusions are visible

## Gate H — Deliverables

Pass conditions:

- all required modular directories exist
- screen, feature, flow, state, and code indexes exist
- `COVERAGE.md`, `UNKNOWNS.md`, `CONTRADICTIONS.md`, and `DISCOVERY_JOURNAL.md` exist
- `GOD_README.md` compiles successfully
- machine ledger validates

## Command

```bash
python scripts/anatomy.py validate --out <output>
```

The command must exit 0.

## Forbidden completion language

Do not say:

- “I reviewed the important files”
- “The major flows are covered”
- “The rest appears repetitive”
- “This should be complete”
- “All relevant behavior is documented” when exclusions/unknowns are hidden

Use:

```text
Static validation: PASS/FAIL
Runtime validation: PASS/FAIL/BLOCKED
Remaining not_tracked units:
Remaining tracking units:
Open unknowns:
Open contradictions:
Excluded paths:
```
