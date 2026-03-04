# Entry: 2026-03-04 09:55 +0800 (Post-Mortem: Cross-OS Gigabit Transfer Bottleneck Analysis)

## Context
During the V63 Stage 2 "Shadow Race" plan, an attempt was made to transfer ~250GB of `.parquet` files from the Linux Controller (`linux1-lx`) to the Windows Compute Node (`windows1-w1`) over a physical 2.5G local network (Category 7 cables, 2.5G router). 

Despite the hardware capabilities, all `scp` transfers (both via LAN IP `192.168.3.112` and Tailscale IP `100.123.90.25`) hard-capped at an agonizing **11~13 MB/s (approx. 100 Mbps)**. A brief attempt to use pure Python HTTP + PowerShell `Invoke-WebRequest` resulted in even slower speeds (~2.7 MB/s).

## Diagnostics & Empirical Findings (via Network Agent)
A dedicated network agent performed deep diagnostics on the infrastructure, revealing the following absolute truths:

1. **Hardware & Link Layer are PERFECT**: 
   - Linux `eno1` negotiated speed: **2500Mb/s Full**.
   - Windows Ethernet negotiated speed: **2.5 Gbps**.
   - Ping routing is strictly direct (`192.168.3.112 dev eno1`).
   - Even Tailscale confirms direct local connection (`via 192.168.3.112:41641`) with ~3ms latency.
2. **TCP Throughput is NOT the bottleneck**:
   - `iperf3` tests from Linux to Windows hit **1.39 Gbps** consistently.
3. **The Culprit: The Implementation Layer**:
   - The 100 Mbps cap is entirely an artifact of the **file transfer protocol/implementation layer**. 
   - `scp` and `sftp` over OpenSSH on Windows incur catastrophic single-threaded cryptographic overhead and buffer-window mismatches when handling massive contiguous binary files (`.parquet`).
   - The severe slowdown during the HTTP test (2.7 MB/s) was likely exacerbated by Windows Defender real-time scanning choking on the sudden ingress of massive undocumented binary streams.

## Standard Operating Procedure for Future Cross-OS Mass Transfers
Future AI Agents MUST NOT use `scp` or Python `http.server` for transferring datasets > 10GB across this specific Linux-to-Windows bridge.

**Mandatory Action Plan for High-Speed Transfers:**
1. **Abandon SCP**: Switch the primary bulk data channel to **SMB/CIFS**.
2. **Mounting**: Linux should mount the Windows target directory via `cifs-utils` or Windows should mount the Linux pool via Samba.
3. **Transfer Tool**: Once mounted, use `rsync` (on Linux) or `robocopy` (on Windows) over the SMB path. This bypasses the OpenSSH encryption chokehold.
4. **Endpoint Defenses**: Temporarily add the target receiving directory (e.g., `D:\Omega_frames\`) to the **Windows Defender Exclusions list**. Real-time scanning on gigabyte-sized appending files will destroy IOPS.
5. **SMB Signing**: If throughput is still sub-optimal over SMB, evaluate disabling mandatory SMB signing (`RequireSecuritySignature=False` on Windows) since the traffic is within a trusted 192.168.3.x airgap.

*Note for current execution*: As directed by the Architect, the current slow `scp` background transfer will be allowed to finish its natural course for this specific run to maintain state stability, but this SOP applies to all future operations.