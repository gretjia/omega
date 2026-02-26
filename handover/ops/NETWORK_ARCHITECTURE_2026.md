# OMEGA Network Architecture (2026 Update)

## 1. The "Hub-and-Spoke" Hybrid Tunnel

To achieve maximum stability and bypass global network throttling, the network architecture has been upgraded to a hybrid tunnel model. We no longer rely on Tailscale's automatic peer routing for cross-border traffic.

### 1.1 Architecture Design
- **The Local Spoke (Shenzhen)**: Local devices (Mac, Windows1, Linux1) run Tailscale and are in the `100.64.0.0/10` subnet.
- **The Hub (Hong Kong)**: A Tencent Cloud Ubuntu node (`vm-0-7-ubuntu`) acts as the central router. It runs Tailscale and has IP Forwarding + Subnet Routing enabled.
- **The Remote Spoke (US)**: The GCP node (`omega-vm`) **does not run the Tailscale client**.
- **The Backbone (HK <-> US)**: A dedicated, raw WireGuard UDP tunnel connects the Hub (HK) and the Remote Spoke (US) on subnet `10.88.0.0/24`.

### 1.2 IP Addressing
| Node | Role | Tailscale IP | WireGuard IP | Public IP |
|---|---|---|---|---|
| local-mac | Developer Client | `100.72.87.94` | N/A | Local Network |
| linux1-lx | Compute Worker | `100.64.97.113` | N/A | Local Network |
| windows1-w1 | Compute Worker | `100.123.90.25` | N/A | Local Network |
| hk-hub | Router / Subnet Gateway | `100.81.234.55` | `10.88.0.2` | `43.161.252.57` |
| omega-vm | Controller / Main | N/A (Client Disabled) | `10.88.0.1` | `34.27.27.164` |

---

## 2. Traffic Flow (How it works)

### 2.1 Shenzhen -> US (`ssh omega-vm`)
1. Local Mac/Linux/Windows is configured to connect to `10.88.0.1`.
2. Tailscale on the local machine intercepts traffic to `10.88.0.0/24` and routes it to the HK Hub (because HK advertised this subnet route).
3. The HK Hub receives the packets, and its Linux kernel `ip_forward` pushes them into the `wg0` WireGuard interface.
4. Packets travel over the dedicated UDP tunnel to `omega-vm` at `10.88.0.1`.

### 2.2 US -> Shenzhen (`ssh linux1-lx`)
1. `omega-vm` attempts to connect to `100.64.97.113`.
2. The `wg0` WireGuard config on `omega-vm` is configured with `AllowedIPs = 10.88.0.2/32, 100.64.0.0/10`. Therefore, `omega-vm` forces this traffic down the WireGuard tunnel to HK (`10.88.0.2`).
3. The HK Hub receives the packets. Seeing the destination is a Tailscale IP, it routes them into the `tailscale0` interface.
4. Packets arrive smoothly at the local machine.

---

## 3. The "Ultimate SSH Config"

All local and remote machines have been configured with a unified SSH alias structure. **Never hardcode IPs in scripts.** Always use the aliases.

### 3.1 Local Machines (`~/.ssh/config`)
Mac, `linux1-lx`, and `windows1-w1` use the following pattern:
```ssh-config
Host omega-vm
  HostName 10.88.0.1
  User zephryj
  IdentityFile ~/.ssh/omega_vmgw_termius  # Or corresponding local key
  IdentitiesOnly yes
  StrictHostKeyChecking accept-new
```

### 3.2 US Controller (`omega-vm ~/.ssh/config`)
`omega-vm` uses the native Tailscale IPs for the local workers, relying on the backbone to route them back:
```ssh-config
Host windows1-w1
    HostName 100.123.90.25
    User jiazi
    IdentityFile ~/.ssh/id_ed25519_omega_workers

Host linux1-lx
    HostName 100.64.97.113
    User zepher
    IdentityFile ~/.ssh/id_ed25519_omega_workers
```

---

## 4. Maintenance and Troubleshooting

### 4.1 Checking the Backbone (WireGuard)
The backbone is maintained by standard `systemd` WireGuard services on both `omega-vm` and the HK node.
```bash
# On omega-vm or HK node
sudo wg show
# Look for "latest handshake" (should be within 2 minutes)
```
- **Port:** Both sides communicate on UDP `51820`. Ensure GCP and Tencent Cloud firewalls have this port open for ingress.

### 4.2 Checking the Hub (Tailscale Subnet Router)
The HK node is the lynchpin. It must advertise the route and forward packets.
```bash
# On HK Node
tailscale debug prefs | jq -r .AdvertiseRoutes
# Expected: ["10.88.0.0/24"]

sysctl net.ipv4.ip_forward
# Expected: net.ipv4.ip_forward = 1
```

### 4.3 Why not use Tailscale Exit Nodes?
Previous attempts to force a multi-hop (Shenzhen -> HK -> US) by blocking direct UDP ports resulted in Tailscale falling back to global DERP relays (TCP), which introduced severe latency and instability. The explicit WireGuard tunnel guarantees 100% path control and avoids Tailscale's unpredictable P2P mesh logic over the GFW.

### 4.4 Co-existence with Commercial VPNs
This architecture operates at the network routing layer (via `tun`/`tap` interfaces). It is designed to be completely independent of application-layer commercial VPNs (e.g., Clash).
- **Rule of Thumb:** Use this dedicated network for SSH and development pipelines. Let commercial VPNs handle default `0.0.0.0/0` web traffic. Do not configure this network as a default exit node for local clients.