#!/bin/bash
# bench_grid.sh <outdir>
#
# Runs the measurement grid through the installed CLI only (`veizik run`) and writes one log per
# run. Nothing else is called: no Python, no engine binary, no private entry point.
#
#   VZ_WEIGHTS_ROOT=/data/models  bash bench_grid.sh ./raw_rtx4090
#
# VZ_WEIGHTS_ROOT is a folder that holds the checkpoint folders by name (Qwen3.5-0.8B/, Qwen3.5-2B/,
# Qwen3.5-4B/, Qwen3.5-9B/, Qwen3.6-35B-A3B/). Models whose folder is absent are skipped.
# MODELS, MODES and LONGFORM_TOKENS can be overridden from the environment.
#
# Per cell: two runs (r1, r2) of the same command at --seed 42, 128 generated tokens. A third kind of
# run, "longform", generates 1024 tokens from the same prompt in balanced mode.
# Log names: functional.<model>.<mode>.r<k>.log|rc|ids.txt and longform.<model>.balanced.log|rc|ids.txt
set -u
OUT=${1:?usage: bench_grid.sh <outdir>}
WROOT=${VZ_WEIGHTS_ROOT:?set VZ_WEIGHTS_ROOT to the folder that holds the checkpoint folders}
KIT=$(cd "$(dirname "$0")/.." && pwd)

# 0. the harness refuses to run if the pinned prompt differs
( cd "$KIT/prompts" && sha256sum -c ../SHA256SUMS ) >/dev/null 2>&1 \
  || { echo "bench_grid: prompt file does not match SHA256SUMS; refusing to run" >&2; exit 1; }
PROMPT=$(cat "$KIT/prompts/fact_chatml.txt")   # command substitution drops any trailing newline

MODELS=${MODELS:-"qwen35_0p8b:Qwen3.5-0.8B qwen35_2b:Qwen3.5-2B qwen35_4b:Qwen3.5-4B qwen35_9b:Qwen3.5-9B qwen36_35b_a3b:Qwen3.6-35B-A3B"}
MODES=${MODES:-"balanced quality fast"}
LONGFORM_TOKENS=${LONGFORM_TOKENS:-1024}
SEED=42

mkdir -p "$OUT" || exit 1
nvidia-smi --query-gpu=name,driver_version --format=csv,noheader 2>/dev/null | head -1 > "$OUT/_gpu.txt"

run1() {   # run1 <model> <weights> <mode> <tokens> <tag>
  local key=$1 w=$2 mode=$3 tok=$4 tag=$5
  local od="$OUT/out.$tag"; rm -rf "$od"
  VZ_WEIGHTS="$w" veizik run "$key" "$PROMPT" --mode "$mode" --tokens "$tok" --seed "$SEED" --out "$od" \
      > "$OUT/$tag.log" 2>&1
  echo $? > "$OUT/$tag.rc"
  [ -f "$od/gen.txt" ] && cp "$od/gen.txt" "$OUT/$tag.ids.txt"
  echo "  $tag rc=$(cat "$OUT/$tag.rc")"
}

for pair in $MODELS; do
  key=${pair%%:*}; ckpt=${pair#*:}; w="$WROOT/$ckpt"
  [ -d "$w" ] || { echo "skip $key (no $w)"; continue; }
  for mode in $MODES; do
    run1 "$key" "$w" "$mode" 128 "functional.$key.$mode.r1"
    run1 "$key" "$w" "$mode" 128 "functional.$key.$mode.r2"
  done
  run1 "$key" "$w" balanced "$LONGFORM_TOKENS" "longform.$key.balanced"
done
echo "done: $OUT"
