# Handover Best Practices (Web Research -> Omega Design)

This note captures the external standards used to design the handover folder as an AI-agent entry gateway.

## 1. Sources Used

- Diataxis documentation framework: <https://diataxis.fr/>
- GitLab on-call handover guide: <https://docs.gitlab.com/development/oncall/handover/>
- 12-Factor App config guidance: <https://12factor.net/config>
- OWASP Secrets Management Cheat Sheet: <https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html>
- Microsoft incident playbook guidance (checklists, roles, execution workflow): <https://learn.microsoft.com/en-us/security/operations/incident-response-playbook-prepare>
- NIST incident response standard (SP 800-61 Rev.3 landing): <https://csrc.nist.gov/pubs/sp/800/61/r3/final>

## 2. Design Principles Derived

1. Single current-truth board.
   - Applied as: `handover/ai-direct/LATEST.md`.
   - Why: handover must expose current state and immediate next action without deep history scanning.

2. Structured handover checklist and explicit role context.
   - Applied as: `handover/ai-direct/HANDOVER_TEMPLATE.md` with required fields.
   - Why: consistent records reduce context loss during agent switches.

3. Clear separation between current state, history, and references.
   - Applied as:
     - current: `LATEST.md`
     - history: `entries/*.md`
     - references/runbooks: `handover/ops/*.md`
   - Why: aligns with Diataxis-style separation and avoids mixed-purpose documents.

4. Secrets must never live in repo handover docs.
   - Applied as:
     - policy in `handover/ops/ACCESS_BOOTSTRAP.md`
     - non-secret metadata in `handover/ops/HOSTS_REGISTRY.yaml`
   - Why: matches 12-factor config separation and OWASP secret lifecycle guidance.

5. Incident/run supervision needs explicit checklists and escalation conditions.
   - Applied as:
     - `handover/README.md` unified startup checklist
     - `handover/ops/PIPELINE_LOGS.md` monitoring checklist
     - `handover/ops/ACTIVE_PROJECTS.md` status + risk + next check
   - Why: incident operations frameworks emphasize role clarity, checklists, and operational readiness.

6. Multi-agent systems need stable permanent governance separated from task-specific execution.
   - Applied as:
     - permanent governance: `handover/ops/MULTI_AGENT_OPERATING_SYSTEM.md`
     - task-specific governance: active charter under `handover/ops/`
   - Why: permanent team rules and one-off mission specs should not contaminate each other.

## 3. Resulting Folder Contract

- Unified entry: `handover/README.md`
- Compatibility shim: `handover/ENTRYPOINT.md`
- Permanent multi-agent governance: `handover/ops/MULTI_AGENT_OPERATING_SYSTEM.md`
- Active mission charter: `handover/ops/ACTIVE_MISSION_CHARTER.md`
- Current state: `handover/ai-direct/LATEST.md`
- Session records: `handover/ai-direct/entries/*.md`
- Runtime contract bus: `handover/ai-direct/live/01..05_*.md`
- Topology/tool/credential/project references: `handover/ops/*.md`

## 4. Maintenance Rule

After every material operation session:

1. write one `entries/*.md` record,
2. update `LATEST.md`,
3. update `ACTIVE_PROJECTS.md` if status changed,
4. update ops docs if paths/tools/credentials changed.
