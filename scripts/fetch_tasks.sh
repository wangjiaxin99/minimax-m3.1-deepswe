#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
commit=0b9fabbb63b9104d678fe965e1632f2dd9eaa2ea
if [[ ! -d vendor/deep-swe/.git ]]; then
  mkdir -p vendor
  git init vendor/deep-swe
  git -C vendor/deep-swe remote add origin https://github.com/datacurve-ai/deep-swe.git
  git -C vendor/deep-swe fetch --depth 1 origin "$commit"
  git -C vendor/deep-swe checkout --detach FETCH_HEAD
fi
test "$(git -C vendor/deep-swe rev-parse HEAD)" = "$commit"
test -z "$(git -C vendor/deep-swe status --porcelain)"
python3 - <<'PY'
from pathlib import Path
tasks = list(Path('vendor/deep-swe/tasks').glob('*/task.toml'))
assert len(tasks) == 113, len(tasks)
print('Verified pinned DeepSWE tasks:', len(tasks))
PY
