import re
from pathlib import Path

latest_path = Path("handover/ai-direct/LATEST.md")
content = latest_path.read_text()

# Update Last Updated Date
content = re.sub(
    r"Last Updated:\*\* .*$",
    "Last Updated:** 2026-02-27 03:25:00 +0800",
    content,
    flags=re.MULTILINE
)

# Update the Global Status section
new_status = """## 1. Global Status

- **Stage 1 (Lakehouse Extraction):** COMPLETE on both hosts.
- **Stage 2 (Physics Engine V62):** **RUNNING (OPTIMIZED & RELAUNCHED)**
  - Linux `linux1-lx`: OOM and stalled query plans resolved via early materialization. Boundary leakage mathematically fixed. Running 345 pending files at ~90s per chunk.
  - Windows `windows1-w1`: `ParseIntError` Rust panics resolved via safe float casting. Pathological symbols dynamically dropped. Running isolated batch resume safely.
- **Stage 3 (Parquet Merge & Feature Matrix):** PENDING."""

content = re.sub(
    r"## 1\. Global Status.*?## 2\.",
    new_status + "\n\n## 2.",
    content,
    flags=re.DOTALL
)

# Update Next Action section
new_actions = """## 5. Next Immediate Action for AI Operator

1. **Monitor Stage 2 Runs:** Let `linux1-lx` and `windows1-w1` complete their newly launched `perf/stage2-speedup-v62` batch queues.
2. **Review Failures:** If specific single files fail again, they will be registered in `audit/stage2_targeted_failed_*.txt`. Address only those specifically without global stalls.
3. **Advance to Stage 3:** Upon dual-host Stage 2 completion, execute downstream Parquet validation and Base Matrix creation."""

content = re.sub(
    r"## 5\. Next Immediate Action for AI Operator.*?## 6\.",
    new_actions + "\n\n## 6.",
    content,
    flags=re.DOTALL
)

latest_path.write_text(content)
print("LATEST.md updated")
