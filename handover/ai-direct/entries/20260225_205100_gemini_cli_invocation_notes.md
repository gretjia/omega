# Gemini CLI Invocation Notes (v62 Stage2 Audit)

Date: 2026-02-25

## 1) Commands that work

Use direct binary to avoid local wrapper side effects:

```bash
/Users/zephryj/.npm-global/bin/gemini -y -m gemini-3.1-pro-preview -o text -p "..."
```

For large context:

```bash
{ nl -ba audit/v62.md; nl -ba tools/stage2_physics_compute.py; } \
  | env -u HTTP_PROXY -u HTTPS_PROXY -u ALL_PROXY -u http_proxy -u https_proxy -u all_proxy -u NO_PROXY -u no_proxy \
    /Users/zephryj/.npm-global/bin/gemini -y -m gemini-3.1-pro-preview -o text -p "..."
```

## 2) Key behavior/constraints observed

- `-y` cannot be combined with `--approval-mode` in the same invocation.
- In non-interactive mode, cached OAuth credentials can be used directly if auth mode is `oauth-personal` and network path is healthy.
- `gemini-3.1-pro-preview` did not resolve via Vertex model endpoint in this project (ModelNotFound), but worked via OAuth personal path.

## 3) Root cause of previous auth failures

- `/Users/zephryj/.local/bin/gemini` is a wrapper that sources proxy env from `~/.config/proxy-launch/env.sh`.
- Proxy injection caused repeated TLS reset during token refresh/auth handshake.
- Bypassing wrapper and unsetting proxy env for the call resolved the issue.

## 4) Recommended default for this repository

- Keep auth type in `~/.gemini/settings.json` as `oauth-personal`.
- For production scripts in this repo, call direct binary (`~/.npm-global/bin/gemini`) rather than wrapper (`~/.local/bin/gemini`).
- Explicitly unset proxy env for Gemini runs unless proxy is known-good.

## 5) Stage2 audit artifact

- Independent Gemini 3.1 Pro audit output:
  - `handover/ai-direct/entries/20260225_204617_gemini31_stage2_speed_audit.md`
