# AutoQ

Open-source altitude-5 harness for a data organisation. Spec: `docs/SPEC.md`. Backlog: `docs/BACKLOG.md`.

## Working on tickets

Build tickets are the issues under #1 (GitHub). Work them **fully autonomously**: do not stop to ask the owner for choices. Make the most sensible decision and record it as an ADR in `docs/adr/` (policy, format and index in `docs/adr/README.md`). Only stop for the owner's own accounts or credentials, spending money, irreversible actions outside the repo, and `ready-for-human` tickets. The shell may need `/Applications/Docker.app/Contents/Resources/bin` on PATH to find `docker`.

## Agent skills

### Issue tracker

Issues and specs live in GitHub Issues for `edsykes/AutoQ` (via the `gh` CLI). See `docs/agents/issue-tracker.md`.

### Triage labels

Default five-role vocabulary (`needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`). See `docs/agents/triage-labels.md`.

### Domain docs

Single-context: `GLOSSARY.md` and `docs/adr/` at the repo root. See `docs/agents/domain.md`.
