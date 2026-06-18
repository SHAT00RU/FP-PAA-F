"""
benchmark.py
------------
ONE-COMMAND reproducible benchmark harness (satisfies the "Reproducibility"
technical constraint and criterion A4/I5).

For each input size n in SIZES (>= 5 sizes, spanning >= 2 orders of
magnitude, as required), this script:
  1. Generates a campus graph with a FIXED seed (reproducible).
  2. Times Dijkstra and Bellman-Ford computing nearest-exit distances for
     ALL vertices (averaged over REPEATS runs to reduce noise).
  3. Cross-checks that both algorithms agree on every distance.
  4. Writes results to bench/results.csv.
  5. Produces two plots: bench/runtime_vs_n.png (log-log) and
     bench/runtime_vs_n_linear.png, saved to the bench/ folder.

Run with:
    python bench/benchmark.py
(run from the repo root; it adds ../src to sys.path automatically)
"""

import csv
import os
import sys
import time
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from graph import generate_campus_graph
from dijkstra import dijkstra_nearest_exit
from bellman_ford import bellman_ford_nearest_exit

# --- Benchmark configuration ---
SIZES = [100, 300, 1000, 3000, 10000, 30000]  # spans 100 -> 30,000 = 2.5 orders of magnitude
N_EXITS = 5
AVG_DEGREE = 5
SEED = 42          # fixed seed, reported per the reproducibility requirement
REPEATS = 3         # average of 3 runs per algorithm per size, to reduce timing noise

OUT_DIR = os.path.dirname(__file__)
CSV_PATH = os.path.join(OUT_DIR, "results.csv")


def time_call(fn, *args, repeats=REPEATS):
    best = float('inf')
    total = 0.0
    result = None
    for _ in range(repeats):
        t0 = time.perf_counter()
        result = fn(*args)
        dt = time.perf_counter() - t0
        total += dt
        best = min(best, dt)
    return result, best, total / repeats


def main():
    rows = []
    print(f"{'n':>8} {'E':>8} {'Dijkstra(ms)':>14} {'BellmanFord(ms)':>16} {'AgreeAll':>9}")
    print("-" * 62)

    for n in SIZES:
        g = generate_campus_graph(n, avg_degree=AVG_DEGREE, seed=SEED)
        exits = list(range(N_EXITS))

        (d_dist, _, _), d_best, d_avg = time_call(dijkstra_nearest_exit, g, exits)
        (b_dist, _, _, neg), b_best, b_avg = time_call(bellman_ford_nearest_exit, g, exits)

        agree = all(
            (d_dist[v] == float('inf') and b_dist[v] == float('inf'))
            or abs(d_dist[v] - b_dist[v]) < 1e-6
            for v in range(n)
        )

        rows.append({
            "n_vertices": n,
            "n_edges": g.edge_count // 2,  # undirected edge count
            "n_exits": N_EXITS,
            "seed": SEED,
            "dijkstra_best_ms": d_best * 1000,
            "dijkstra_avg_ms": d_avg * 1000,
            "bellman_ford_best_ms": b_best * 1000,
            "bellman_ford_avg_ms": b_avg * 1000,
            "distances_agree": agree,
            "negative_cycle_detected": neg,
        })

        print(f"{n:>8} {g.edge_count//2:>8} {d_best*1000:>14.3f} {b_best*1000:>16.3f} {str(agree):>9}")

    # Write CSV
    with open(CSV_PATH, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    print(f"\nResults written to {CSV_PATH}")

    # Plots
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        ns = [r["n_vertices"] for r in rows]
        dj = [r["dijkstra_best_ms"] for r in rows]
        bf = [r["bellman_ford_best_ms"] for r in rows]

        # Log-log plot (for empirical growth-exponent estimation, criterion A5)
        fig, ax = plt.subplots(figsize=(7, 5))
        ax.loglog(ns, dj, marker="o", label="Dijkstra (binary heap)")
        ax.loglog(ns, bf, marker="s", label="Bellman-Ford")
        ax.set_xlabel("Number of vertices (n)")
        ax.set_ylabel("Runtime (ms, best of {} runs)".format(REPEATS))
        ax.set_title("Runtime vs. input size (log-log)")
        ax.legend()
        ax.grid(True, which="both", linestyle="--", alpha=0.5)
        fig.tight_layout()
        loglog_path = os.path.join(OUT_DIR, "runtime_vs_n_loglog.png")
        fig.savefig(loglog_path, dpi=150)
        print(f"Log-log plot saved to {loglog_path}")

        # Linear plot (more intuitive view of the gap between the two)
        fig2, ax2 = plt.subplots(figsize=(7, 5))
        ax2.plot(ns, dj, marker="o", label="Dijkstra (binary heap)")
        ax2.plot(ns, bf, marker="s", label="Bellman-Ford")
        ax2.set_xlabel("Number of vertices (n)")
        ax2.set_ylabel("Runtime (ms)")
        ax2.set_title("Runtime vs. input size (linear)")
        ax2.legend()
        ax2.grid(True, linestyle="--", alpha=0.5)
        fig2.tight_layout()
        linear_path = os.path.join(OUT_DIR, "runtime_vs_n_linear.png")
        fig2.savefig(linear_path, dpi=150)
        print(f"Linear plot saved to {linear_path}")

        # Estimate empirical growth exponent via log-log slope between
        # consecutive points (used in the report's theory-vs-practice section, A5)
        print("\nEmpirical growth exponent (slope of log(time) vs log(n) between consecutive sizes):")
        print(f"{'n_i -> n_j':>16} {'Dijkstra slope':>16} {'BellmanFord slope':>18}")
        for i in range(1, len(ns)):
            ln_ratio = math.log(ns[i] / ns[i-1])
            dj_slope = math.log(dj[i] / dj[i-1]) / ln_ratio if dj[i-1] > 0 else float('nan')
            bf_slope = math.log(bf[i] / bf[i-1]) / ln_ratio if bf[i-1] > 0 else float('nan')
            print(f"{ns[i-1]:>7} -> {ns[i]:<6} {dj_slope:>16.2f} {bf_slope:>18.2f}")

    except ImportError:
        print("matplotlib not available -- skipping plots (CSV is still complete).")


if __name__ == "__main__":
    main()
