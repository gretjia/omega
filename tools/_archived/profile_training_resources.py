import psutil
import time
import json
import os
from pathlib import Path

def profile():
    # Overall System Stats
    cpu_count = psutil.cpu_count(logical=True)
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    
    # Python Process Stats
    python_procs = []
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_info', 'cmdline']):
        try:
            if 'python' in proc.info['name'].lower():
                cmdline = " ".join(proc.info['cmdline'] or [])
                # Record all python processes to see the cluster
                python_procs.append({
                    'pid': proc.info['pid'],
                    'cpu': proc.info['cpu_percent'],
                    'mem_mb': proc.info['memory_info'].rss / (1024 * 1024),
                    'cmd': cmdline[:100]
                })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    total_python_cpu = sum(p['cpu'] for p in python_procs)
    total_python_mem = sum(p['mem_mb'] for p in python_procs)

    report = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "system": {
            "logical_cpus": cpu_count,
            "total_cpu_percent": cpu_percent,
            "memory_total_gb": memory.total / (1024**3),
            "memory_used_percent": memory.percent,
            "memory_available_gb": memory.available / (1024**3)
        },
        "python_cluster": {
            "process_count": len(python_procs),
            "total_python_cpu_percent": total_python_cpu,
            "total_python_mem_mb": total_python_mem,
            "avg_cpu_per_proc": total_python_cpu / len(python_procs) if python_procs else 0,
            "avg_mem_per_proc_mb": total_python_mem / len(python_procs) if python_procs else 0
        }
    }
    
    print(json.dumps(report, indent=2))
    
    # Save to audit log
    audit_file = Path("audit/v40_performance_baseline.json")
    with open(audit_file, "a") as f:
        f.write(json.dumps(report) + "\n")

if __name__ == "__main__":
    profile()