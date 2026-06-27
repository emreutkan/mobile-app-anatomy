# Mobile Feature Taxonomy

Use this taxonomy as a negative-space checklist. A category with no implementation should be recorded as absent after search, not silently omitted.

## Application lifecycle

- native process startup
- dependency injection/provider initialization
- splash and boot blocking
- migrations
- app state/background/foreground
- process death and restoration
- crash/error boundaries
- update/version gating
- maintenance mode

## Identity

- anonymous mode
- email/password
- Apple OAuth
- Google OAuth
- other OAuth
- registration
- verification
- password reset
- session refresh
- account linking
- logout
- account deletion
- profile editing
- multi-account behavior

## Onboarding and personalization

- onboarding steps
- skip/back/resume
- validation
- derived profile values
- recommendation inputs
- experiments
- completion state
- destination branching
- later editing and downstream recalculation

## Navigation and UI composition

- root navigator
- nested stacks
- tabs, drawers, headers
- context-sensitive navigation
- multiple app modes/workspaces
- modals, sheets, dialogs, overlays
- search and filtering
- forms and keyboards
- gestures and animations
- responsive layout
- theme and appearance
- accessibility
- localization

## Data and state

- local component state
- global/domain state
- server-state caches
- persistence
- secure storage
- databases
- migrations
- cache invalidation
- optimistic updates
- offline queue
- conflict resolution
- synchronization
- derived/computed state

## Networking

- base URLs and environments
- authentication headers
- refresh/retry
- request construction
- serialization
- response normalization
- pagination
- uploads/downloads
- websocket/realtime
- cancellation
- timeouts
- error mapping
- observability

## Device and platform

- permissions
- camera/photos/files
- microphone
- location
- health/fitness APIs
- Bluetooth
- sensors
- haptics
- biometrics
- contacts/calendar
- background execution
- notifications
- deep links/universal links/app links
- widgets/extensions/watch apps
- share extensions
- native bridges

## Monetization

- products/plans
- paywalls
- trials
- purchases
- receipt/transaction validation
- restore purchases
- entitlement calculation
- grace/billing retry
- expiration
- promotional offers
- subscription management links
- analytics and experiments around paywalls

## Trust, privacy, and compliance

- consent
- privacy disclosures
- tracking authorization
- data export/deletion
- secrets and token storage
- logs containing personal data
- platform privacy manifests
- terms and policy presentation
- age gating
- user-facing explanations of calculations

## Growth and measurement

- analytics providers
- event taxonomy
- user properties
- attribution
- experiments
- remote config
- review prompts
- referrals
- sharing
- UGC/creator hooks
- App Store/Play Store metadata that affects behavior

## Quality evidence

- unit tests
- component/widget tests
- integration tests
- E2E tests
- snapshot/golden tests
- accessibility tests
- performance tests
- release checks
- crash reporting
- logging

For each category, document presence, absence, or unknown with search evidence.
