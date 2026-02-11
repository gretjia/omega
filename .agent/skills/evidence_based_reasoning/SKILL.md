---
name: evidence_based_reasoning
description: A protocol for validating claims and making decisions based strictly on local project artifacts (Logs, Code, Results) to minimize hallucination and external reliance.
---

# Evidence-Based Reasoning (Contextual Forensics)

## Core Philosophy
**"The Project state is the only Truth."**

AI agents must prioritize *observed reality* (logs, results) over *intended reality* (code, docs) or *general knowledge* (training data). When debating a design choice or justifying a decision, you must cite **Local Evidence**.

## The "Local Truth" Hierarchy

When verifying a fact, prioritize sources in this order:

1.  **Runtime Artifacts (The "What Happened")**
    *   **Files**: `*.log`, `*_results.csv`, `_audit_state.jsonl`, `*.parquet`
    *   **Value**: Irrefutable proof of system behavior.
    *   *Example*: "Training completed 242 archives because `_audit_state.jsonl` has 242 entries."

2.  **Source Code (The "How It Works")**
    *   **Files**: `*.py`, `config.py`, `omega_v3_core/kernel.py`
    *   **Value**: Defines the logic and computation.
    *   *Example*: "The feature uses Z-score because `omega_v3_core/kernel.py` line 150 calls `zscore()`."

3.  **Documentation & Plans (The "Why It Exists")**
    *   **Files**: `OMEGA_CONSTITUTION.md`, `audit/*.md`, `README.md`
    *   **Value**: Provides intent, principles, and strategic context.
    *   *Example*: "Dynamic thresholds are required per `OMEGA_CONSTITUTION.md` Article II."

4.  **External Knowledge (The "General Theory")**
    *   **Source**: Training data, web search.
    *   **Value**: Weakest evidence. Use only when internal artifacts are missing.
    *   *Example*: "Square-Root Law is a known market impact model." (Use sparingly)

## The Verification Workflow

### 1. The Challenge
User asks: *"Why did you make this decision?"* or *"Are you sure this works?"*

### 2. The Artifact Hunt
Do **NOT** answer from memory. Use tools to find physical evidence:
*   `grep_search`: Find where the concept appears in the codebase.
*   `find_by_name`: Locate relevant log files or result CSVs.
*   `view_file`: Read the actual content.

### 3. The Citation
Construct your argument using **Direct Citations**:
*   "In `omega_v3_core/kernel.py` at line 100..."
*   "According to `_audit_state.jsonl`, 242 files were processed..."
*   "Per `OMEGA_CONSTITUTION.md` Article II..."

### 4. The Synthesis
Combine multiple data points to form a solid conclusion.
*   *Pattern*: "Code Intention (Code) + Execution Proof (Log) + Principle (Constitution) = Validated Fact."

## Example: Justifying a Design Decision

**Context**: User asks why dynamic thresholds are used instead of fixed values.

**AI Response Structure**:
1.  **Constitution Principle**:
    *   *Evidence*: `OMEGA_CONSTITUTION.md` Article II states "There are NO static parameters."
    *   *Conclusion*: "Fixed thresholds violate Constitution."

2.  **Code Implementation**:
    *   *Evidence*: `omega_v3_core/kernel.py` computes `threshold = quantile(history, 0.95)`.
    *   *Conclusion*: "Implementation follows Constitution."

3.  **Runtime Verification**:
    *   *Evidence*: Log shows threshold adapting from 1.1 to 1.4 over time.
    *   *Conclusion*: "Dynamic behavior confirmed in production."

## Checklist for AI Agents

- [ ] Did I search the `audit/` or `data/` directory before answering?
- [ ] Can I point to a specific line of code or log entry?
- [ ] Did I cite `OMEGA_CONSTITUTION.md` for principle-based claims?
- [ ] Did I rely on the file system rather than my "intuition"?
- [ ] If guessing, did I explicitly state "INFERENCE: ..."?
