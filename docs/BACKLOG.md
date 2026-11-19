# AutoQ — v1 Backlog (DRAFT, awaiting approval)

Tracer-bullet tickets for the v1 spine. Each is a vertical slice, demoable on its own. Order lists blockers first. Tickets are published to GitHub Issues only after approval (to-tickets). Every ticket must cite the user stories (SPEC.md) and decisions it serves.

| # | Ticket | Blocked by |
|---|---|---|
| 1 | Walking skeleton: compose (api, web, Postgres), ask a question, see it in a tree, scenario-test harness (API seam) | none |
| 2 | ADRs 001–010 (short) | none |
| 3 | Tiny world model + ECC-style sim behind the Connector interface, with Answer Key | none |
| 4 | S/4 on-prem and S/4 Cloud sims, planted price driver, the three "spend" definitions, supporting data | 3 |
| 5 | LLM gateway (BYO key, any model), cassettes, handoff records and trace, ledger, spend caps, kill switch | 1 |
| 6 | Question cascade with Question Governance acceptance, local roles and delegates | 1, 5 |
| 7 | Contract, catalogue, lineage graph and OpenLineage emission; Lake Adapter (DuckDB/Parquet) with snapshots | 1, 2 |
| 8 | Mission contract, approval policy, LangGraph runner, thin Frame (Need Spec) and Discover with source profile reuse | 4, 6, 7 |
| 9 | Meaning mission: Clarify detects "spend" conflict, Meaning Authority workbench ratifies, assertion committed and reused | 2, 8 |
| 10 | Evidence and Verify thin agents: resolve-before-create, minimal landing, facts with contract, reconciliation against Answer Key | 9 |
| 11 | Claim graph, domain-routed review, counter-claim accept/reject, release only when all claims have dispositions | 10 |
| 12 | Answer step: immutable versioned answer per asker level, follow-up routing stub, decision record | 11 |
| 13 | Builder spine: retrospective over handoffs, skill/check change, hypothesis record, Dev/Promotion evals, baseline v0, gate, promote, rollback | 12 |
| 14 | Metrics page (four compounding metrics vs baseline) and compounding scenario | 13 |
| 15 | Operator views: storage space and cost, lineage view for any graph | 7, 12 |
| 16 | (ready-for-human) Install Docker locally; choose cloud provider and account | none |
| 17 | Ship: clean-machine compose check, docs, cloud VM deploy, live instance | 14, 15, 16 |

Parallel start: 1, 2, 3, 16.
