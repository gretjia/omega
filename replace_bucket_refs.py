import os
import glob

files = [
    "orchestrator.py",
    "smoke_test_payload.py",
    "tools/mac_gateway_sync.py",
    "tools/v60_multi_agent_tick.py",
    "tools/v60_autopilot.py",
    "tools/run_v60_micro_dryrun.py",
    "tools/submit_vertex_sweep.py",
    "tools/harvest_swarm_logs.py",
    "tools/run_vertex_smoke.py",
    "tools/v60_swarm_xgb.py",
    "tools/ai_incident_watchdog.py",
    "tools/audit_gcs_file_distribution.py",
    "audit/runtime/v52/uplink_loop_aa8abb7.sh"
]

for filepath in files:
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            content = f.read()
        
        # Replace avoiding double-central
        new_content = content.replace("gs://omega_v52/", "gs://omega_v52_central/")
        new_content = new_content.replace('gs://omega_v52"', 'gs://omega_v52_central"')
        new_content = new_content.replace("gs://omega_v52'", "gs://omega_v52_central'")
        new_content = new_content.replace("gs://omega_v52 ", "gs://omega_v52_central ")
        
        # Deduplicate if we accidentally created gs://omega_v52_central_central
        new_content = new_content.replace("omega_v52_central_central", "omega_v52_central")
        
        if new_content != content:
            print(f"Updated {filepath}")
            with open(filepath, 'w') as f:
                f.write(new_content)
