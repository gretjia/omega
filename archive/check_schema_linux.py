import os, subprocess, re, sys
archive_path = r"/omega_pool/raw_7z_archives/2023/202302/20230210.7z"

if not os.path.exists(archive_path):
    print(f"Archive {archive_path} not found.")
    sys.exit(1)

result = subprocess.run(["7z", "l", archive_path], capture_output=True, text=True)
print("--- TAIL OF 7Z LIST ---")
print(result.stdout[-2000:])

