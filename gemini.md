# The "Hassle-Free" AI-Ops Deployment Protocol (V-Next)

> **CRITICAL ARCHITECT DIRECTIVE:** The user is experiencing extreme operational fatigue due to repeated, low-level execution errors during multi-machine deployment.
> ANY AI Agent reading this codebase MUST STRICTLY follow this 3-Step Protocol whenever the Architect provides a new `audit/vXX.md` blueprint.

## The 3 Fatal Sins of Past AI Deployments (BANNED BEHAVIORS)

1. **Semantic Desyncs (Fake Starts):** Running an execution script (e.g., `v61_framing.py`) *before* the actual mathematical code (`kernel.py` / `omega_etl.py`) is fully upgraded to match the `vXX.md` constraints.
2. **SCP Hot-Patching (Git Bypass):** Sneaking code onto remote nodes using `scp`. This destroys version control (`git hash` mismatch) and creates "ghost states". **SCP is strictly banned for code updates.**
3. **Silent Island Network Ignorance:** Blindly sending `git pull` or outbound Github requests to Windows/Linux worker nodes without realizing they sit on isolated LANs and lack direct SSH/GitHub access, causing permanent terminal timeouts.

---

## The "Hassle-Free" 3-Step Execution Standard

When the Architect provides a new blueprint (`audit/vXX.md`), execute EXACTLY this sequence:

### STEP 1: Code & Local Immutable Commit (Mac Workspace)

All code modifications MUST be done locally on the Mac environment first.

- Read the blueprint thoroughly.
- Apply the changes to the Python modules (e.g., `kernel.py`, `trainer.py`).
- Run a minimal local syntax check / dry-run to ensure no immediate compile errors.
- **MANDATORY GITOPS GATE:** You MUST stage, commit, and push the code locally before touching any remote node:

  ```bash
  git add .
  git commit -m "feat(vXX): Full implementation of vXX blueprint"
  git push origin HEAD
  ```

### STEP 2: The LAN-Native Cluster Sync ("One-Pulse" Push)

Because remote nodes (Linux `192.168.3.113` / Windows `192.168.3.112`) are heavily restricted, do NOT use `git pull origin` from their native shells.
Instead, use the Mac to securely **push** the Git state down into the nodes across the LAN, or use heavily curated SSH-Agent Forwarding.
*(e.g., `git push zepher@192.168.3.113:~/work/Omega_vNext HEAD:v60-incoming` -> `git reset --hard v60-incoming`)*

### STEP 3: Safe Launch & Mandatory "Tailing" Verification

Do not blindly launch processes and assume success.

- Launch the specific pipeline logic (e.g., `vXX_linux_framing.py`).
- **MANDATORY HOLD:** You must `tail -f` the worker log or monitor `top -n 1` for exactly **2 minutes**.
- Verify memory (`RSS`) isn't exploding unconditionally (Watch out for ZFS deadlocks).
- Assert that at least *one* operational cycle completes successfully with output generated.
- Only then may you return control to the User.
