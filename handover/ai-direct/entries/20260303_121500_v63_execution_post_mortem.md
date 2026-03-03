# Entry: 2026-03-03 12:15 +0800 (Post-Mortem: V63 Stage 2 & AI Context Loss)

## Root Cause Analysis
1. **The V62 / V63 Context Confusion**:
   - The AI agent failed to properly consult `audit/v63_architect_directive.md` and the existing `LATEST.md` before making assumptions.
   - The file `tools/stage2_physics_compute.py` still contained `v62` in its docstrings (`v62 Stage 2 Physics Compute Agent`) and `--help` output. Because the AI did not cross-reference this with the Architect's directive, it briefly hallucinated that the system was running older code, creating confusion for the user.

2. **The Missing Manifolds (Topology Bug)**:
   - During the V62 -> V63 refactor, the loop generating `out_manifolds` was accidentally stripped out of `kernel.py`. 
   - While the Architect's directive (`audit/v63_architect_directive.md`) provided explicit instructions to inject the new causal routing (`srl_is_active`) and the deterministic fastmath fix, it completely omitted the manifold mapping loop in its provided copy-paste block (ACTION 3). 
   - A previous AI blindly copy-pasted the Architect's block without reconciling it against the project's config requirement (`FEATURE_COLS`), causing silent data loss in Stage 2 that only exploded during Stage 3 training validation.

3. **Parallel Execution Thrashing**:
   - The AI attempted to launch 16 concurrent workers processing 4GB Parquet files simultaneously without checking the physical limits of `linux1-lx` (120GB RAM). This caused severe Swap thrashing and execution hang.
   - The AI then wasted time cycling through `supervisor` implementations before finally realizing that safe isolation via `shards` and multiple `targeted_resume` processes was the optimal stable path.

## Standard Operating Procedures for Future Agents
- **READ THE DOCS FIRST**: You MUST read `/handover/ai-direct/LATEST.md` before executing any workflow commands. Do not guess the state. 
- **TRUST BUT VERIFY DIRECTIVES**: When an Architect Directive provides a code block, you must reconcile it against the existing codebase. Do not blindly overwrite code if it drops required dependencies (like `FEATURE_COLS` matching).
- **MEMORY & COMPUTE PROFILING**: Never launch >1 worker on `linux1-lx` for Stage 2 without running `free -g` and `top` first. Base_L1 files are huge; running out of memory causes silent hanging that mimics code deadlocks. Use the `shard` based isolated workers pattern (`launch_stage2_sharded.sh`) for safe multi-core execution.
## Algorithmic Complexity Note for V63 Stage 2
Future agents must **NOT** interpret the extreme slowness of V63 Stage 2 (`stage2_physics_compute.py`) as a "bug" or "hang" requiring optimization or code dropping. 
The V63 Architect Directive mandated strict IEEE-754 compliance (removing `fastmath=True`) and mathematically exact polygon closure (`Shoelace/Green's Theorem`) on 120-million-row subsets. 

Because `config.py` demands 3 separate manifold projections (`topo_micro`, `topo_classic`, `topo_trend`), the core sliding-window integration (`calc_topology_area_rolling`) is executed multiple times per row. 
- **Expected Throughput**: ~30 to 50 minutes per single 4GB `Base_L1` file on a modern high-clock core.
- **Do not optimize this away.** If you attempt to skip the manifold generation loop to speed up the process (as happened previously), the resulting dataset will lack critical features required by the `FEATURE_COLS` signature, causing catastrophic failure in Vertex AI XGBoost training.
- Use `tools/launch_stage2_sharded.sh` to safely scale this compute-bound task across available memory without triggering OOM Swap thrashing.

## Windows 1 Execution & Environment Hazards
When utilizing `windows1-w1` to process its partition of the L1 dataset, agents must observe the following constraints:
- **Code Synchronization**: Windows cannot natively sync from GitHub due to firewall limitations (GFW). You MUST push to the local IP mirror (`192.168.3.93`) or manually `scp` updated Python scripts (like `kernel.py`) from the Linux controller before running pipelines.
- **Environment Rot**: The Python virtual environment (`.venv`) on Windows can become corrupted (e.g., losing the `pip` module or missing binaries) when manually tampered with. If processes crash with `RC=2` instantly, rebuild the venv using `python.exe -m venv .venv --clear` and reinstall dependencies.
- **Process Orphan Tracking (WinError 32)**: Windows enforces strict file locks. If a previous run crashes, it may leave a background Python process holding the lock on a `.tmp` file. Attempting to overwrite it via `unlink()` will throw `PermissionError: [WinError 32]`. Use PowerShell (`Stop-Process -Name python -Force`) to cleanly release locks before restarting the targeted supervisor.
- **Detached Execution**: Standard backgrounding techniques like `Start-Process` or `& ... &` fail across SSH sessions on Windows. You MUST use Scheduled Tasks (`Register-ScheduledTask`) running as `System` to properly detach a long-running supervisor daemon from the SSH lifecycle.
