import os, subprocess, re, sys
raw_root = r"E:\data\level2"
found = None
for root, dirs, files in os.walk(raw_root):
    for f in files:
        if "20230210.7z" in f:
            found = os.path.join(root, f)
            break
    if found: break

if not found:
    print("Archive 20230210.7z not found.")
    sys.exit(1)

print(f"Found: {found}")
result = subprocess.run([r"C:\Program Files\7-Zip\7z.exe", "l", found], capture_output=True, text=True)
csv_files = re.findall(r"([A-Za-z0-9_\.]+\.csv)", result.stdout)
if not csv_files:
    print("No CSVs found.")
    sys.exit(1)
target_csv = csv_files[0]
print(f"Target: {target_csv}")
try:
    cmd = f'""C:\\Program Files\\7-Zip\\7z.exe"" e -so {found} {target_csv}'
    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    out = []
    for _ in range(3):
        out.append(proc.stdout.readline().strip())
    proc.terminate()
    print("--- HEADER ---")
    print("\n".join(out))
except Exception as e:
    print(f"Error: {e}")
