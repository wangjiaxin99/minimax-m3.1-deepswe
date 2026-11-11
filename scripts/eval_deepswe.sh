#!/usr/bin/env bash
set -euo pipefail
: "${REPO_DIR:?}" "${RUN_REL:?}" "${MODEL_PATH:?}" "${MODEL_FORMAT:?}" "${OPENAI_BASE_URL:?}"
cd "$REPO_DIR/$RUN_REL"
exec pier run \
  -p "${TASKS_DIR:?}" \
  --agent mini-swe-agent \
  --model "openai/${MODEL_PATH}" \
  --env docker --no-delete \
  --n-concurrent 64 --n-attempts 3 --max-retries 2 \
  --agent-setup-timeout-multiplier 5 \
  --agent-timeout-multiplier 1 --verifier-timeout-multiplier 1 \
  --ak version=2.4.5 \
  --ak 'extra_python_packages=["litellm[mcp]==1.108.3","mcp==2.3.0"]' \
  --ak model_class=litellm_response \
  --ak cost_limit=0 \
  --ak reasoning_effort=max \
  --ak "$(python -c 'import json,os; print("model_kwargs="+json.dumps({"api_base":os.environ["OPENAI_BASE_URL"],"api_key":"EMPTY","temperature":1.0,"top_p":0.95,"max_output_tokens":65536,"drop_params":False}))')" \
  --ae "OPENAI_BASE_URL=$OPENAI_BASE_URL" \
  --ae OPENAI_API_KEY=EMPTY \
  --jobs-dir logs/deepswe --job-name "mini_${MODEL_FORMAT}_attempts3"
