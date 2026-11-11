#!/usr/bin/env bash
set -euo pipefail
source /opt/pier-venv/bin/activate
: "${REPO_DIR:?}" "${RUN_REL:?}" "${MODEL_FORMAT:?}"
run_dir="$REPO_DIR/$RUN_REL"
# Require a fresh run; never overwrite prior trials or interrupted jobs.
if [[ -e "$run_dir/manifest.json" || -e "$run_dir/logs/deepswe" ]]; then
  echo "Run already exists: $run_dir. Set a fresh RUN_REL." >&2
  exit 2
fi
mkdir -p "$run_dir/scripts" "$run_dir/logs/deepswe"
cp "$REPO_DIR/scripts/eval_deepswe.sh" "$REPO_DIR/scripts/run_eval.sh" "$run_dir/scripts/"
printf '{"format":"%s","tasks_per_round":113,"attempts_per_job":3,"jobs":["logs/deepswe/mini_%s_attempts3"]}\n' \
  "$MODEL_FORMAT" "$MODEL_FORMAT" > "$run_dir/manifest.json"
python "$REPO_DIR/scripts/capture_environment.py" --output "$run_dir/environment.json"
echo "Starting ${MODEL_FORMAT}, n-attempts=3, at $(date -u +%FT%TZ)"
bash "$run_dir/scripts/eval_deepswe.sh" > "$run_dir/logs/eval_deepswe.log" 2>&1
python "$REPO_DIR/scripts/summarize.py" --manifest "$run_dir/manifest.json" --output "$run_dir/summary.json"
