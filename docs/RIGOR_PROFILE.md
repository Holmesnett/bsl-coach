# Rigor Profile

**Tier:** Micro app

Just me or a couple of trusted people; low stakes. Bias to the smallest thing that works.

---

## Access / Auth

Single user or a tiny trusted group. Auth optional or the simplest thing that works (a single login, a shared secret, or none if local-only). Do not build accounts, roles, or invites.

## Multi-user / Tenancy

None. Single-tenant, single-user assumptions are fine.

## Data Sensitivity

Assume no third-party PII. Local or simple storage is acceptable.

## Security

Standard hygiene only — no secrets in code, validate the obvious inputs. Skip threat modeling, rate limiting, and abuse prevention.

## Validation & Tests

Cover the happy path and the one or two failure modes that would lose the user's data. Do not over-test.

## Scale

Assume tiny. No caching, queues, or horizontal-scale design.

## Plan For

Speed to a working tool. Bias to the smallest thing that works.

---

This profile is generated from the "Who will use this app?" intake answer (`audience_tier`). It is planning guidance for the Architect — it does not add code or runtime behavior to your project.
