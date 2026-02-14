import json
from datetime import datetime
from pathlib import Path

ROOT = Path("C:/Omega_vNext")
RUNTIME = ROOT / "audit" / "v51_runtime" / "windows" / "full_autopilot"
OUT_MD = ROOT / "audit" / "v51_deep_audit.md"


def load_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def fmt(v):
    if v is None:
        return "N/A"
    return str(v)


def main():
    summary = load_json(RUNTIME / "autopilot_summary.json")
    status = load_json(RUNTIME / "autopilot_status.json")
    train_status = load_json(RUNTIME / "train" / "train_status.json")
    back_status = load_json(RUNTIME / "backtest" / "backtest_status.json")

    manifests = summary.get("manifests", {})
    train = summary.get("train", {})
    back = summary.get("backtest", {})

    now = datetime.now().strftime("%Y-%m-%d")
    now_ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    lines = []
    lines.append("# OMEGA v5.1 鍏ㄩ噺璁粌+鍥炴祴娣卞害瀹¤锛圓utopilot No-Resume锛?)
    lines.append(f"**瀹¤鏃ユ湡**: {now}")
    lines.append("**鑼冨洿**: windows1 鑷姩娴佺▼锛坒rame->train->backtest锛?)
    lines.append("")

    lines.append("## 1. 瀹¤缁撹锛堝厛缁撹锛?)
    lines.append(f"- 褰撳墠娴佺▼鐘舵€? phase={fmt(status.get('phase'))}, state={fmt(status.get('state'))}")
    lines.append(f"- train files: {fmt(manifests.get('train_count'))}, years: {fmt(manifests.get('train_years'))}")
    lines.append(f"- backtest files: {fmt(manifests.get('backtest_count'))}, years: {fmt(manifests.get('backtest_years'))}")
    lines.append(f"- 鍥炴祴鏈€缁堝璁? {fmt(back.get('final_audit_status') or back_status.get('final_audit_status'))}")
    lines.append("")

    lines.append("## 2. 鍏抽敭鎸囨爣澶嶇洏")
    lines.append(f"- train total_rows: {fmt(train.get('total_rows') or train_status.get('total_rows'))}")
    lines.append(f"- backtest total_rows: {fmt(back.get('total_rows') or back_status.get('total_rows'))}")
    lines.append(f"- total_trades: {fmt(back.get('total_trades') or back_status.get('total_trades'))}")
    lines.append(f"- total_pnl: {fmt(back.get('total_pnl') or back_status.get('total_pnl'))}")
    lines.append(f"- avg_snr: {fmt(back.get('avg_snr') or back_status.get('avg_snr'))}")
    lines.append(f"- avg_orth: {fmt(back.get('avg_orth') or back_status.get('avg_orth'))}")
    lines.append(f"- avg_align: {fmt(back.get('avg_align') or back_status.get('avg_align'))}")
    lines.append("")

    lines.append("## 3. 璇佹嵁璺緞")
    lines.append(f"- autopilot_status: `{(RUNTIME / 'autopilot_status.json').as_posix()}`")
    lines.append(f"- autopilot_summary: `{(RUNTIME / 'autopilot_summary.json').as_posix()}`")
    lines.append(f"- train_status: `{(RUNTIME / 'train' / 'train_status.json').as_posix()}`")
    lines.append(f"- backtest_status: `{(RUNTIME / 'backtest' / 'backtest_status.json').as_posix()}`")
    lines.append(f"- v51 mandate: `{(ROOT / 'audit' / 'v51.md').as_posix()}`")
    lines.append("")

    lines.append("## 4. Alignment 鍒嗘瀽")
    lines.append("- 浠?Vector Alignment 鏄惁瓒呰繃 0.6 浣滀负鏍稿績鏀捐闂ㄦ銆?)
    lines.append("- 鑻ユ湭杩囩嚎锛屼笅涓€杞户缁洿缁曟柟鍚戣涔夊仛瀹氬悜淇ˉ銆?)
    lines.append("")
    lines.append(f"_Generated at: {now_ts}_")

    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print(str(OUT_MD))


if __name__ == "__main__":
    main()

