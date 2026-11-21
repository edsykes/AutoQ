# AutoQ — v1 Backlog (DRAFT, awaiting approval)

Tracer-bullet tickets for the v1 spine, matched to SPEC.md draft 4 (issue #1). Each is a vertical slice, demoable on its own. Order lists blockers first. Tickets are published to GitHub Issues only after approval (`/to-tickets 1`).

Each ticket lists the user stories (US) and acceptance scenarios (AS) from SPEC.md that it satisfies. Story and scenario numbers refer to the spec.

| # | Ticket | Blocked by | US | AS |
|---|---|---|---|---|
| 1 | Walking skeleton: compose (api, web, Postgres), ask a question, see it in a tree, scenario-test harness (API seam), public repo and CI | none | 1, 39 | 1 (harness) |
| 2 | ADRs 001–010 (short) | none | all (decisions) | none |
| 3 | Tiny world model with all four planted drivers + ECC-style sim behind the Connector interface, with Answer Key; sims as lossy views of the one world model | none | 34, 40 | 2 (partial), 5 (key) |
| 4 | S/4 on-prem and S/4 Cloud sims, org-politics definitions of "spend" (committed, invoiced, received), seeded default values and indicator data | 3 | 13, 20, 34 | 2, 4 (data) |
| 5 | LLM gateway (BYO key, any model; hosted instance session key only), cassettes, handoff records and trace, ledger, spend caps, kill switch, Operator-approved stable-core change path | 1 | 23, 24, 27a, 28 | 7, 9 |
| 6 | Question cascade with Question Governance acceptance, local roles; queue timeout: reminder at 24 and 72 hours then re-route to the operator; blocked missions spend no budget | 1, 5 | 1, 2, 7, 15, 16, 21 | 1, 9 |
| 7 | Contract, catalogue, lineage graph and OpenLineage emission; Lake Adapter (DuckDB/Parquet) with snapshots; replay of data, definitions and numbers | 1, 2 | 35, 36 | 3 |
| 8 | Mission contract, approval policy, LangGraph runner, thin Frame (Need Spec, plain Intent Record) and Discover with source profile reuse | 4, 6, 7 | 11, 12, 22, 34 | 1, 2, 3 |
| 9 | Meaning mission: Clarify detects "spend" conflict, Meaning Authority workbench ratifies, assertion committed and reused | 2, 8 | 13, 17, 18 | 4 |
| 10 | Evidence and Verify thin agents: resolve-before-create, minimal landing, facts with contract, reconciliation against Answer Key, detect and flag planted data artefacts (no remediation) | 9 | 11, 35 | 3, 5 |
| 11 | Claim graph with value links to seeded indicators, domain-routed review, hand-dispositioned counter-claims, release only when all claims have dispositions | 10 | 8, 9, 10, 20 | 6 |
| 12 | Answer step: immutable versioned answer per asker level, thin Follow-up Agent to the asker's own authority, decision record, "meaning changed since" annotation, human-triggered rebuild | 11 | 3, 4, 5, 38 | 5 |
| 13 | Builder spine: retrospective over handoffs, skill/check change, hypothesis record, Dev (10 cases, 3 seeds) and Promotion (10 hidden cases, 3 other seeds) evals, Baseline v0 frozen under a tag with one seeded deficiency, gate, promote, rollback | 12 | 29, 30, 31, 32, 33 | 8 |
| 14 | Metrics page (four compounding metrics vs Baseline v0) and compounding scenario: five related questions, each metric at least 20% better by the fifth | 13 | 6, 33 | 10 |
| 15 | Operator views: storage space and cost, lineage view for any graph | 7, 12 | 25, 26 | 11 |
| 16 | (ready-for-human) Install Docker locally; choose cloud provider and account | none | 27 | none |
| 17 | Ship: clean-machine compose check, docs, cloud VM deploy, live instance, scripted demo | 14, 15, 16 | 27, 39, 40 | 12 |

Parallel start: 1, 2, 3, 16.

Done for v1 means acceptance scenarios 1 to 12 pass, with scenario 12 run on the cloud VM (SPEC.md, Testing Decisions).

## Changes from the earlier 17-ticket draft
- Ticket 3 plants all four drivers and makes each sim a view of the one world model; ticket 4 carries the org-politics definitions and the seeded default values.
- Ticket 5 gains the Operator-approved stable-core change path and the hosted-instance key rule.
- Ticket 6 drops delegates (v1.2) and adds the reminder and re-route behaviour and the blocked-mission rule.
- Ticket 10 detects and flags data artefacts without remediation (remediation rules are v1.1).
- Ticket 11 uses hand-dispositioned counter-claims (agent triage is v1.1).
- Ticket 12 drops follow-up routing and dialogue (v1.2) for a thin Follow-up Agent.
- Ticket 13 drops the Sealed set (v2) and adds the frozen Baseline v0 with a seeded deficiency.

## Stories not covered by a v1 ticket (deferred)
14 (dialogue, v1.2), 19 (sensitivity check, v1.1), 37 (remediation rules, v1.1). Story 21's delegates and Story 4's multi-level routing are the v1.2 parts of otherwise v1 stories.
