# v60 Multi-Agent Research Basis (OpenAI + Community)

- timestamp_utc: 2026-02-19T00:00:00Z
- scope: governed multi-agent flow for v60 execution (`research -> smoke -> dual-audit -> execute`)
- constitution_pre_read: `/Users/zephryj/work/Omega_vNext/audit/constitution_v2.md`

## OpenAI Official Findings (Primary)
1. OpenAI recommends starting with one agent and only splitting into multi-agent when complexity/latency/tool fan-out truly requires it; over-splitting early adds unnecessary coordination complexity.
2. Agent workflows should be evaluation-driven; system behavior must be measured with explicit eval sets and thresholds before scaling autonomy.
3. Responses API background mode is suitable for long-running asynchronous jobs with polling/webhooks, reducing blocking and improving resilience.
4. OpenAI Agents SDK has built-in tracing primitives (`trace`, `span`, `generation_span`) for end-to-end observability and debugging.
5. OpenAI Codex docs include parallel sub-agents patterns, but recommend controlled decomposition with explicit task boundaries.

## Community Best Practices (Primary)
1. LangGraph multi-agent guidance: choose multi-agent only when single-agent context/tool load is too large; each sub-agent should own a clear sub-problem.
2. LangGraph persistence/checkpointing: keep short-term state, long-term memory, and interruption/resume (`interrupt`) for human-in-the-loop safety gates.
3. AutoGen architecture: explicit orchestrator/worker (AgentTool handoffs) enables safer decomposition and tool-scoped execution.
4. Community consensus across these frameworks: reliability requires idempotent steps, explicit state/checkpoints, and observability before adding autonomy.

## Mapping to Omega v60
1. Keep orchestration centralized (Codex orchestrator) with role-isolated ticks (`windows-monitor`, `linux-bootstrap`, `linux-monitor`, `autopilot-gate`).
2. Keep durable shared state/event logs (`multi_agents_<hash>.state.json`, `multi_agents_<hash>.events.log`) as checkpoint backbone.
3. Use autonomous debug assistant only as bounded helper (incident report generation), not as merge authority.
4. Enforce gate order:
   - `deploy_and_check --repair` + dry-run role ticks (smoke)
   - Independent dual recursive audits (`04A`, `04B`)
   - Execute only if both audits return `VERDICT: PASS`
5. Preserve constitution hard constraints: no time slicing (`chunk-days`), no float downcast as OOM workaround, no cloud ETL bloat in base-matrix stage.

## Implementation Hook
- rollout gate script:
  - `/Users/zephryj/work/Omega_vNext/tools/v60_multi_agent_governed_rollout.py`
- run command:
  - `python3 /Users/zephryj/work/Omega_vNext/tools/v60_multi_agent_governed_rollout.py --hash aa8abb7 --execute`

## Source Links
- OpenAI Building agents guide: <https://platform.openai.com/docs/guides/agents>
- OpenAI Evaluating agents guide: <https://platform.openai.com/docs/guides/evals-for-agents>
- OpenAI Responses background mode guide: <https://platform.openai.com/docs/guides/background>
- OpenAI Agents SDK tracing: <https://openai.github.io/openai-agents-python/tracing/>
- OpenAI Codex multi-agents docs: <https://developers.openai.com/codex/multi-agents>
- LangGraph multi-agent concepts: <https://langchain-ai.github.io/langgraph/concepts/multi_agent/>
- LangGraph persistence concepts: <https://langchain-ai.github.io/langgraph/concepts/persistence/>
- LangGraph human-in-the-loop concepts: <https://langchain-ai.github.io/langgraph/concepts/human_in_the_loop/>
- AutoGen multi-agent framework docs: <https://microsoft.github.io/autogen/dev/user-guide/core-user-guide/design-patterns/multi-agent-debate.html>
- AutoGen handoffs/AgentTool docs: <https://microsoft.github.io/autogen/stable/user-guide/core-user-guide/framework/agent-and-agent-runtime.html>
