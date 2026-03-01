#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage:
  mac_publish_and_rollout.sh [--repo PATH] [--remote NAME] [--branch NAME]
                             [--tag TAG] [--hosts H1,H2] [--windows-repo-path PATH]
                             [--allow-dirty] [--skip-publish]

Defaults:
  --repo               current working directory
  --remote             hub
  --branch             current checked-out branch
  --hosts              windows1-w1,windows2-w2
  --windows-repo-path  C:\Omega_vNext

Examples:
  ./tools/git_sync/mac_publish_and_rollout.sh --remote hub --branch main
  ./tools/git_sync/mac_publish_and_rollout.sh --remote hub --branch main --tag v2026.02.12-r2
USAGE
}

REPO_PATH="$(pwd)"
REMOTE_NAME="hub"
BRANCH_NAME=""
TAG_NAME=""
HOSTS_CSV="windows1-w1,windows2-w2"
WINDOWS_REPO_PATH='C:\Omega_vNext'
ALLOW_DIRTY=0
SKIP_PUBLISH=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --repo)
      REPO_PATH="$2"
      shift 2
      ;;
    --remote)
      REMOTE_NAME="$2"
      shift 2
      ;;
    --branch)
      BRANCH_NAME="$2"
      shift 2
      ;;
    --tag)
      TAG_NAME="$2"
      shift 2
      ;;
    --hosts)
      HOSTS_CSV="$2"
      shift 2
      ;;
    --windows-repo-path)
      WINDOWS_REPO_PATH="$2"
      shift 2
      ;;
    --allow-dirty)
      ALLOW_DIRTY=1
      shift
      ;;
    --skip-publish)
      SKIP_PUBLISH=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      usage >&2
      exit 1
      ;;
  esac
done

if ! command -v git >/dev/null 2>&1; then
  echo "git command not found." >&2
  exit 1
fi

if ! command -v ssh >/dev/null 2>&1; then
  echo "ssh command not found." >&2
  exit 1
fi

if [[ ! -d "$REPO_PATH/.git" ]]; then
  echo "Not a git repository: $REPO_PATH" >&2
  exit 1
fi

cd "$REPO_PATH"

if [[ -z "$BRANCH_NAME" ]]; then
  BRANCH_NAME="$(git rev-parse --abbrev-ref HEAD)"
fi

if [[ "$BRANCH_NAME" == "HEAD" ]]; then
  echo "Detached HEAD is not supported. Switch to a branch first." >&2
  exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PUBLISH_SCRIPT="$SCRIPT_DIR/mac_publish_to_hub.sh"

if [[ ! -x "$PUBLISH_SCRIPT" ]]; then
  echo "Required script not found or not executable: $PUBLISH_SCRIPT" >&2
  exit 1
fi

if [[ "$SKIP_PUBLISH" -eq 0 ]]; then
  publish_args=(--repo "$REPO_PATH" --remote "$REMOTE_NAME" --branch "$BRANCH_NAME")
  if [[ -n "$TAG_NAME" ]]; then
    publish_args+=(--tag "$TAG_NAME")
  fi
  if [[ "$ALLOW_DIRTY" -eq 1 ]]; then
    publish_args+=(--allow-dirty)
  fi
  "$PUBLISH_SCRIPT" "${publish_args[@]}"
else
  echo "[Rollout] Skipping publish as requested (--skip-publish)."
fi

IFS=',' read -r -a HOSTS <<< "$HOSTS_CSV"
if [[ "${#HOSTS[@]}" -eq 0 ]]; then
  echo "No hosts provided. Use --hosts H1,H2." >&2
  exit 1
fi

REMOTE_SCRIPT_PATH="${WINDOWS_REPO_PATH}\\tools\\git_sync\\windows_update_from_hub.ps1"

for raw_host in "${HOSTS[@]}"; do
  host="$(echo "$raw_host" | xargs)"
  if [[ -z "$host" ]]; then
    continue
  fi

  echo "[Rollout] Updating $host ..."
  ps_payload=$(cat <<EOF
\$repoPath = '$WINDOWS_REPO_PATH'
\$remoteName = '$REMOTE_NAME'
\$branchName = '$BRANCH_NAME'
\$syncScript = '$REMOTE_SCRIPT_PATH'

if (Test-Path \$syncScript) {
    & \$syncScript -RepoPath \$repoPath -RemoteName \$remoteName -Branch \$branchName
    exit \$LASTEXITCODE
}

git -C \$repoPath fetch \$remoteName --prune --tags
if (\$LASTEXITCODE -ne 0) { exit \$LASTEXITCODE }
git -C \$repoPath switch \$branchName
if (\$LASTEXITCODE -ne 0) { exit \$LASTEXITCODE }
git -C \$repoPath pull --ff-only \$remoteName \$branchName
exit \$LASTEXITCODE
EOF
)
  remote_cmd="powershell -NoProfile -ExecutionPolicy Bypass -EncodedCommand $(printf '%s' "$ps_payload" | iconv -f UTF-8 -t UTF-16LE | base64 | tr -d '\n')"
  ssh "$host" "$remote_cmd"
done

echo "[Done] Rollout completed for hosts: $HOSTS_CSV"
