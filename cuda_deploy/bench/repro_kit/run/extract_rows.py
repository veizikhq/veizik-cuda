#!/usr/bin/env python3
"""extract_rows.py -- turn the logs written by bench_grid.sh into a neutral measurement file and
board rows.

  python3 -I extract_rows.py --raw ./raw_rtx4090 --gpu "RTX 4090" --arch sm_89 \
      --measured-at "2026-10-21 | veizik-cuda 1.0.0, previous build" \
      --prov "previous-version (measured on the previous build; not re-measured for 04f865f5)" \
      --bench-txt RTX4090_bench.txt --rows-json RTX4090_rows.json

Reads, per run, only the timing and memory figures the engine prints at the end of a run (decode
steps / milliseconds / tok/s, prompt tokens / milliseconds, device memory used) plus the exit code
and a short hash of the generated token ids. Everything else in a log is ignored and is not copied
into the outputs.

Definitions
  decode tok/s    = the engine's own figure: (generated tokens - 1) decoded steps divided by the
                    decode time. The first of the N generated tokens comes from the prompt pass,
                    so a 128-token run times 127 decode steps.
  resident memory = device memory in use after the weights and the decode graph are loaded
                    (GiB = 2^30 bytes, i.e. the nvidia-smi MiB figure / 1024). It is not the
                    transient peak during decode.
  value (row)     = median of the completed runs of the cell; per_run lists every run.
"""
import argparse, glob, hashlib, json, os, re, statistics, sys


def rd(p):
    try:
        with open(p, errors="replace") as f:
            return f.read()
    except OSError:
        return ""


def num(pat, s, cast=float):
    m = re.findall(pat, s)
    return cast(m[-1]) if m else None


def run_record(base):
    log = rd(base + ".log")
    rc = rd(base + ".rc").strip()
    ids = rd(base + ".ids.txt")
    rec = {
        "rc": int(rc) if rc.lstrip("-").isdigit() else None,
        "tok_s": num(r"tok/s=\s*([\d.]+)", log),
        "decode_steps": num(r"DECODE steps=\s*(\d+)", log, int),
        "decode_ms": num(r"DECODE steps=\s*\d+\s+ms=\s*([\d.]+)", log),
        "prompt_tokens": num(r"PROMPT tokens=\s*(\d+)", log, int),
        "prompt_ms": num(r"PROMPT tokens=\s*\d+\s+ms=\s*([\d.]+)", log),
        "used_mib_after_graph": num(r"after_graph\s+free_MiB=\s*\d+\s+total_MiB=\s*\d+\s+used_MiB=\s*(\d+)", log, int),
        "used_mib_after_weights": num(r"after_weights\s+free_MiB=\s*\d+\s+total_MiB=\s*\d+\s+used_MiB=\s*(\d+)", log, int),
        "total_mib": num(r"after_weights\s+free_MiB=\s*\d+\s+total_MiB=\s*(\d+)", log, int),
        "gen_tokens": len(ids.split()) if ids.strip() else None,
        "gen_sha": hashlib.sha256(ids.encode()).hexdigest()[:16] if ids.strip() else None,
    }
    rec["ok"] = rec["rc"] == 0 and rec["tok_s"] is not None
    return rec


def gib(mib):
    return round(mib / 1024, 2)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", required=True)
    ap.add_argument("--gpu", required=True)
    ap.add_argument("--arch", required=True)
    ap.add_argument("--measured-at", required=True)
    ap.add_argument("--prov", required=True)
    ap.add_argument("--power", default="default board power (not recorded)")
    ap.add_argument("--driver", default=None, help="default: read from _gpu.txt")
    ap.add_argument("--bench-txt", required=True)
    ap.add_argument("--rows-json", required=True)
    a = ap.parse_args()

    gpu_line = rd(os.path.join(a.raw, "_gpu.txt")).strip()
    driver = a.driver or (gpu_line.split(",")[-1].strip() if "," in gpu_line else "unknown")

    cells = {}   # (model, mode) -> {run name: base path}
    for p in sorted(glob.glob(os.path.join(a.raw, "functional.*.log"))):
        m = re.match(r"functional\.(.+)\.(balanced|quality|fast|ultrafast|low-memory)\.(r\d+)\.log$", os.path.basename(p))
        if m:
            cells.setdefault(("functional", m.group(1), m.group(2)), {})[m.group(3)] = p[:-4]
    for p in sorted(glob.glob(os.path.join(a.raw, "longform.*.log"))):
        m = re.match(r"longform\.(.+)\.(balanced|quality|fast)\.log$", os.path.basename(p))
        if m:
            cells.setdefault(("longform", m.group(1), m.group(2)), {})["r1"] = p[:-4]

    order = {"qwen35_0p8b": 0, "qwen35_2b": 1, "qwen35_4b": 2, "qwen35_9b": 3, "qwen36_35b_a3b": 4}
    mode_order = {"balanced": 0, "quality": 1, "fast": 2}
    keys = sorted(cells, key=lambda k: (k[0] != "functional", order.get(k[1], 9), mode_order.get(k[2], 9)))

    lines = [
        "# neutral measurement lines -- one line per run; produced by extract_rows.py",
        f"# gpu={a.gpu} arch={a.arch} driver={driver} measured_at={a.measured_at}",
        "# columns: kind model mode run rc gen_tokens prompt_tokens prompt_ms decode_steps decode_ms tok_s "
        "mem_after_graph_MiB mem_total_MiB gen_sha",
    ]
    rows = []
    for kind, model, mode in keys:
        runs = cells[(kind, model, mode)]
        recs = {r: run_record(b) for r, b in sorted(runs.items())}
        for r, rec in recs.items():
            lines.append(" ".join(str(x) if x is not None else "-" for x in (
                kind, model, mode, r, rec["rc"], rec["gen_tokens"], rec["prompt_tokens"], rec["prompt_ms"],
                rec["decode_steps"], rec["decode_ms"], rec["tok_s"], rec["used_mib_after_graph"],
                rec["total_mib"], rec["gen_sha"])))
        done = [r for r in recs.values() if r["ok"]]
        base = {
            "model": model, "arch": a.arch, "gpu": a.gpu, "power": a.power,
            "measured_at": a.measured_at, "prov": a.prov, "mode": mode, "driver": driver,
        }
        if not done:
            first = next(iter(recs.values()))
            rows.append({**base, "axis": "decode", "value": None, "unit": "tok/s", "status": "not_completed",
                         "runs": len(recs), "exit_codes": [r["rc"] for r in recs.values()],
                         "resident_after_load_gib": gib(first["used_mib_after_graph"] or first["used_mib_after_weights"])
                         if (first["used_mib_after_graph"] or first["used_mib_after_weights"]) else None,
                         "device_total_gib": gib(first["total_mib"]) if first["total_mib"] else None})
            continue
        vals = [r["tok_s"] for r in done]
        med = statistics.median(vals)
        spread = (max(vals) - min(vals)) / med * 100 if len(vals) > 1 else None
        shas = {r["gen_sha"] for r in done}
        ref = done[0]
        rows.append({**base, "axis": "decode", "value": round(med, 1), "unit": "tok/s", "status": "ok",
                     "runs": len(done), "per_run": [round(v, 1) for v in vals],
                     "spread_pct": None if spread is None else round(spread, 2),
                     "gen_tokens": ref["gen_tokens"], "timed_decode_steps": ref["decode_steps"],
                     "prompt_tokens": ref["prompt_tokens"],
                     "deterministic": (len(shas) == 1) if len(done) > 1 else None,
                     "gen_sha": ref["gen_sha"] if len(shas) == 1 else sorted(shas)})
        if kind == "functional" and ref["used_mib_after_graph"]:
            rows.append({**base, "axis": "resident_memory", "value": gib(ref["used_mib_after_graph"]), "unit": "GiB",
                         "status": "ok", "runs": len(done), "device_total_gib": gib(ref["total_mib"]),
                         "note": "device memory in use after weights and decode graph are loaded; not the transient peak"})

    with open(a.bench_txt, "w") as f:
        f.write("\n".join(lines) + "\n")
    with open(a.rows_json, "w") as f:
        json.dump(rows, f, indent=1)
        f.write("\n")
    print(f"{len(lines) - 3} run lines, {len(rows)} rows -> {a.bench_txt}, {a.rows_json}")


if __name__ == "__main__":
    sys.exit(main())
