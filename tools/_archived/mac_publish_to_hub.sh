#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage:
  mac_publish_to_hub.sh [--repo PATH] [--remote NAME] [--branch NAME] [--tag TAG] [--push-all-tags] [--allow-dirty]

Defaults:
  --repo         current working directory
  --remote       hub
  --branch       current checked-out branch

Examples:
  ./tools/git_sync/mac_publish_to_hub.sh --remote hub --branch main
  ./tools/git_sync/mac_publish_to_hub.sh --remote hub --branch main --tag v2026.02.12-r1
USAGE
}

REPO_PATH="$(pwd)"
REMOTE_NAME="hub"
BRANCH_NAME=""
TAG_NAME=""
PUSH_ALL_TAGS=0
ALLOW_DIRTY=0

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
    --push-all-tags)
      PUSH_ALL_TAGS=1
      shift
      ;;
    --allow-dirty)
      ALLOW_DIRTY=1
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

if [[ "$ALLOW_DIRTY" -eq 0 ]]; then
  git diff --quiet --exit-code || {
    echo "Unstaged changes detected. Commit/stash first, or pass --allow-dirty." >&2
    exit 1
  }
  git diff --cached --quiet --exit-code || {
    echo "Staged but uncommitted changes detected. Commit first, or pass --allow-dirty." >&2
    exit 1
  }
fi

git remote get-url "$REMOTE_NAME" >/dev/null

echo "[Publish] Fetching '$REMOTE_NAME'..."
git fetch "$REMOTE_NAME" --prune

echo "[Publish] Pushing branch '$BRANCH_NAME' to '$REMOTE_NAME'..."
git push "$REMOTE_NAME" "$BRANCH_NAME"

if [[ -n "$TAG_NAME" ]]; then
  if git rev-parse -q --verify "refs/tags/$TAG_NAME" >/dev/null; then
    echo "Tag already exists: $TAG_NAME" >&2
    exit 1
  fi
  git tag -a "$TAG_NAME" -m "Release $TAG_NAME"
  git push "$REMOTE_NAME" "$TAG_NAME"
  echo "[Publish] Created and pushed tag '$TAG_NAME'."
fi

if [[ "$PUSH_ALL_TAGS" -eq 1 ]]; then
  git push "$REMOTE_NAME" --tags
  echo "[Publish] Pushed all local tags."
fi

HEAD_SHA="$(git rev-parse --short HEAD)"
echo "[Done] Published $BRANCH_NAME @ $HEAD_SHA"
