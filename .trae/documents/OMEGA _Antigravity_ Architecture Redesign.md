# OMEGA Universal Antigravity Architecture Plan

This plan implements a **"Write Once, Run Everywhere"** Agent-Native architecture. We will establish a **Single Source of Truth (The Constitution)** and create **Platform Adapters** for Trae, Antigravity, Gemini CLI, and Codex CLI to ensure seamless, automatic recognition across all environments.

## 1. Core Layer: The OMEGA Constitution (Single Source of Truth)
We define the absolute laws of the project. All agents, regardless of platform, must obey these.

*   **Create** **`OMEGA_CONSTITUTION.md`**:
    *   **The Trinity**: TDA (Geometry), SRL (Physics), Epiplexity (Information).
    *   **The Methodology**: Recursive Calibration (No hardcoding), Physics First (Realizability > Rules).
    *   **The Prime Directive**: "The Agent is the Orchestrator; verify all code against Math/Physics."

## 2. Universal Skill Library (`.agent/skills/`)
A shared library of capabilities usable by all platforms.

*   **Refactor** **`SKILL.md`** **into Modular Capabilities**:
    *   `math_core/`: TDA, Entropy, SRL calculations.
    *   `physics/`: Boundary checks, Volume Clock, Impact modeling.
    *   `engineering/`: RQAdapter, Python, Docker.
    *   `ops/`: Git, Audit, Backtest.

## 3. Platform Adapters (The "Polyglot" Layer)
We will create specific configuration files for each IDE/CLI to "hook" them into the Constitution automatically.

### A. Trae IDE (`.trae/`)
*   **Action**: Create/Update `.trae/instruction.md` (or `.trae/system_prompt.md`).
*   **Content**: "You are the OMEGA Trae Agent. YOUR PRIME DIRECTIVE is to follow `OMEGA_CONSTITUTION.md`. Use skills in `.agent/skills/`."

### B. Antigravity IDE (`.antigravity/` & `.agent/`)
*   **Action**: Create `.antigravity/config.yaml` and ensure `.agent/` structure complies with Antigravity standards (Manager View support).
*   **Content**: Define the "Manager Agent" profile that orchestrates sub-agents (Editor, Terminal, Browser) based on `OMEGA_CONSTITUTION.md`.

### C. Gemini CLI (`.gemini/`)
*   **Action**: Create `.gemini/context.md` (and `.gemini/prompt`).
*   **Content**: Optimized system prompt for Gemini's long-context window, loading the entire `OMEGA_CONSTITUTION.md` and `audit/Bible_AUDIT.MD` into context immediately.

### D. Codex CLI (`.codex/` & `.cursorrules`)
*   **Action**: Create `.codex/rules.md` and a root `.cursorrules` (standard for Codex-based editors like Cursor).
*   **Content**: Compact, code-focused rules extracted from the Constitution (e.g., "NEVER use T+1 hardcoding; ALWAYS check `is_limit_up`").

## 4. The "Universal Router" (`README.md`)
*   **Update** **`README.md`**:
    *   Add a **"For AI Agents"** section at the very top.
    *   Explicit instructions: "If you are an AI Agent (Trae, Gemini, Codex, Antigravity), **READ `OMEGA_CONSTITUTION.md` FIRST**."
    *   This ensures that even if a specific config is missed, any agent reading the root file will be redirected to the core logic.

## 5. Implementation Sequence
1.  **Draft** `OMEGA_CONSTITUTION.md` (Synthesizing `Bible.md` & `Bible_AUDIT.MD`).
2.  **Build** `.agent/skills/` hierarchy.
3.  **Deploy** Platform Adapters (`.trae/`, `.antigravity/`, `.gemini/`, `.codex/`).
4.  **Update** Root `README.md`.
5.  **Verify**: Check that the `SKILL.md` content is correctly distributed and no "hardcoded T+1" rules remain.
