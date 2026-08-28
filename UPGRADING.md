# Upgrading

## TL;DR

- This repo has moved from Bitbucket to GitHub. Bitbucket is no longer maintained, so any
  `external-checks-git` reference still pointing at `bitbucket.org` should be treated as stale -
  migrate it to `github.com` as part of this upgrade.
- `CKV_CUSTOM_DYNAMODB_DELETION_PROTECTION` is now stricter: it additionally requires
  `Properties.DeletionProtectionEnabled: true` on every DynamoDB table. This may newly fail
  pipelines that previously passed.
- `CKV_CUSTOM_API_GATEWAY_SUBSCRIPTION_FILTER` was fixed to stop producing false failures on
  configs that use `${param:...}` variables. If you were skipping this check, you can remove
  the skip.
- We recommend all consumers **pin to a specific released version** (see below) rather than
  tracking the default branch.

## Pin to a version (recommended policy)

Always reference a specific tag with `?ref=<version>` rather than tracking the default branch:

```yaml
external-checks-git:
  - https://github.com/yotoplay/yoto-checkov.git//serverless?ref=v1.5.0
```

Avoid:

```yaml
external-checks-git:
  - https://github.com/yotoplay/yoto-checkov.git//serverless # no ref - tracks the default branch
```

Why this matters:

- **Stability.** It lets us add or tighten checks in this repo without breaking every consumer's
  pipeline on their next CI run. Upgrades become a deliberate, reviewable change (bump the `ref`
  when you're ready) instead of a surprise failure.
- **Supply-chain risk.** `external-checks-git` clones and executes Python code from this repo at
  CI time, across many of our services. Tracking a moving branch means any push here runs
  immediately everywhere. Pinning to an immutable tag limits blast radius and makes what's
  actually running auditable and reproducible, even though this is our own repo.

Bump the pinned `ref` deliberately when you want to adopt new checks - check the
[CHANGELOG](./CHANGELOG.md) and this file for anything relevant to your configuration first.

## Required: migrate the source URL

Update `checkov.yml`:

```yaml
# before
external-checks-git:
  - https://bitbucket.org/yotoplay/yoto-checkov.git//serverless

# after - pick one, but pin a version either way
external-checks-git:
  - https://github.com/yotoplay/yoto-checkov.git//serverless?ref=v1.5.0 # adopt the new checks
  - https://github.com/yotoplay/yoto-checkov.git//serverless?ref=v1.4.1 # defer, keep current behaviour
```

## Handling the stricter DynamoDB check

`CKV_CUSTOM_DYNAMODB_DELETION_PROTECTION` now requires all of:

- `Properties.DeletionProtectionEnabled: true`
- `DeletionPolicy: Retain` (or an unresolved serverless variable, e.g. a per-stage `${self:...}`
  value that checkov can't statically resolve)
- `UpdateReplacePolicy: Retain` (same tolerance as above)

Previously only the last two were checked, and `DeletionProtectionEnabled` was ignored entirely.

Options, in order of preference:

1. **Fix it (recommended)** - add the property to each table. This is the actual intent of the
   check (prevent accidental data loss):

   ```yaml
   MyTable:
     Type: AWS::DynamoDB::Table
     Properties:
       DeletionProtectionEnabled: true
       # ...
   ```

2. **Skip repo-wide**, in `checkov.yml`:

   ```yaml
   skip-check:
     - CKV_CUSTOM_DYNAMODB_DELETION_PROTECTION
   ```

3. **Skip a specific resource**, inline in `serverless.yml` above the table:

   ```yaml
   # checkov:skip=CKV_CUSTOM_DYNAMODB_DELETION_PROTECTION: <reason>
   MyTable:
     Type: AWS::DynamoDB::Table
   ```

## API Gateway subscription filter

If your `checkov.yml` currently skips `CKV_CUSTOM_API_GATEWAY_SUBSCRIPTION_FILTER` (e.g. because
`DestinationArn` uses `${param:...}` indirection), you can remove that skip after upgrading - the
false failure is fixed.

## Known impact by repo (at time of writing)

Repos with DynamoDB tables that do **not** yet set `DeletionProtectionEnabled` and will need
action (fix or skip) before adopting `v1.5.0`:

- `yoto-club-api` (7 tables)
- `yoto-auth-api`
- `yoto-kustomer`

Repos already compliant (no action needed for this check):

- `yoto-card-api`
- `yoto-content-access-api`
- `yoto-wishlist-api`

All other consumers have no DynamoDB tables affected by this change; only the source URL
migration applies to them.
