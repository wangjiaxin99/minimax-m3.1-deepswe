#!/usr/bin/env bash
set -euo pipefail
: "${MODEL_PATH:?}"
export VLLM_ROCM_USE_AITER=1
export VLLM_ROCM_USE_AITER_FUSION_SHARED_EXPERTS=0
export VLLM_ROCM_USE_AITER_MOE=1
exec vllm serve "$MODEL_PATH" \
  --block-size 128 \
  --disable-hybrid-kv-cache-manager \
  --tensor-parallel-size 4 \
  --kv-cache-dtype nvfp4 \
  --attention-config '{"indexer_kv_dtype":"nvfp4","indexer_decode_cp":true}' \
  --moe-backend aiter \
  --tool-call-parser minimax_m3 \
  --enable-auto-tool-choice \
  --reasoning-parser minimax_m3 \
  --max-model-len 524288
