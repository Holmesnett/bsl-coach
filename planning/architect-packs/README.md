# Architect Packs

Save Architect Pack files in this folder.

Recommended file name pattern:

`architect-pack-###-{sprint-name}.md`

From the project root, dry-run a pack before applying it:

`node scripts/apply-architect-pack.js planning/architect-packs/architect-pack-###-{sprint-name}.md --dry-run`

After reviewing the dry-run output, apply the pack:

`node scripts/apply-architect-pack.js planning/architect-packs/architect-pack-###-{sprint-name}.md`

Do not store secrets, API keys, passwords, tokens, or private credentials in Architect Packs.

After a pack is applied, Builders should implement from the generated sprint files under `planning/sprints/`, not from the Architect Pack itself.

Historical root-level Architect Pack files are still valid, but `planning/architect-packs/` is the preferred location going forward.
