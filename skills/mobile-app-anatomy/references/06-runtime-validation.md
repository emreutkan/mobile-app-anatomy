# Runtime Validation

## Tool preference

Use whatever is installed and appropriate:

- cross-platform semantic mobile control
- iOS Simulator/Xcode tooling
- Android Emulator/ADB/UIAutomator
- Maestro
- Appium
- framework integration tests
- manual simulator interaction with screenshots and logs

Do not pretend a tool is available. Record exact commands and versions.

## Runtime protocol

For each test state:

1. Define preconditions and seed data.
2. Capture starting state.
3. Execute one user action at a time.
4. Record visible result, logs, network activity, persistence, and analytics when observable.
5. Compare with static prediction.
6. Record discrepancies.
7. Restore or document resulting state.
8. Link evidence to the corresponding screen, feature, and flow documents.

## State matrix

Build `08-runtime/STATE_MATRIX.md` with rows for:

- install/account/profile/entitlement/data/permission/lifecycle/platform/device
- entry method
- expected initial route
- observed initial route
- actions tested
- terminal state
- evidence
- pass/fail/blocked

## Required destructive and interruption scenarios

Where safe and possible:

- kill during onboarding
- background during form entry
- lose network during mutation/upload
- token expires during active use
- permission denied then enabled in Settings
- subscription changes outside the app
- notification opens when logged out
- deep link targets unavailable/guarded screen
- stale local schema after app update
- partial persisted state
- duplicate tap/retry
- back gesture during transaction
- rotation/resizing where supported

## Visual and accessibility checks

Record:

- touch target behavior
- focus order
- screen-reader labels
- dynamic type/font scaling
- contrast where determinable
- keyboard avoidance
- safe areas/insets
- smallest and largest target screens
- dark/light mode
- localization expansion and RTL if supported

## Runtime completion

A screen is runtime-verified only when:

- it was reached in a declared state
- its principal interactions were exercised
- at least one alternate/error state was tested when applicable
- resulting navigation/state changes were observed
- evidence is stored

Static-only documentation must be labeled `static_only`.

## Runtime mode contract

Initialize the ledger with one of:

- `--runtime-mode on` — runtime evidence is mandatory; validation requires a populated `08-runtime/STATE_MATRIX.md` and at least one file under `evidence/runtime/`.
- `--runtime-mode off` — runtime is deliberately out of scope; validation requires a populated `08-runtime/BLOCKER.md` explaining the exact limitation and its effect on confidence.
- `--runtime-mode auto` — the agent must either execute runtime validation or write the blocker. It may not silently omit both.
