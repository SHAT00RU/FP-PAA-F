"""
demo.py
-------
End-to-end CLI demo (satisfies I3: "an application/demo that actually solves
the stated problem"). Generates a synthetic campus, designates evacuation
exits, then reports -- for any room the user picks -- the fastest evacuation
route and its time, computed with BOTH algorithms side by side.

Usage:
    python demo.py --n 1000 --exits 5 --start 17 --seed 42
    python demo.py --n 200 --exits 3 --start 0 --algo bellman_ford
"""

import argparse
import time

from graph import generate_campus_graph
from dijkstra import dijkstra_nearest_exit, reconstruct_route
from bellman_ford import bellman_ford_nearest_exit


def main():
    parser = argparse.ArgumentParser(
        description="Campus Evacuation Route Planner -- DAA Final Exam demo")
    parser.add_argument("--n", type=int, default=1000, help="number of rooms/vertices")
    parser.add_argument("--exits", type=int, default=5, help="number of evacuation exits")
    parser.add_argument("--start", type=int, default=0, help="room to evacuate from")
    parser.add_argument("--seed", type=int, default=42, help="random seed")
    parser.add_argument("--avg-degree", type=int, default=5, help="avg corridor connections per room")
    args = parser.parse_args()

    print(f"Generating synthetic campus graph: n={args.n}, avg_degree={args.avg_degree}, seed={args.seed}")
    g = generate_campus_graph(args.n, avg_degree=args.avg_degree, seed=args.seed)
    exits = list(range(args.exits))
    print(f"Designated evacuation exits (vertex ids): {exits}")
    print(f"Graph built: {g.n} vertices, {g.edge_count} directed adjacency entries\n")

    if args.start >= args.n:
        print(f"Error: --start {args.start} is out of range for n={args.n}")
        return

    # --- Algorithm A: Dijkstra ---
    t0 = time.perf_counter()
    d_dist, d_parent, d_nearest = dijkstra_nearest_exit(g, exits)
    t_dijkstra = time.perf_counter() - t0
    d_route = reconstruct_route(d_parent, args.start, d_nearest)

    # --- Algorithm B: Bellman-Ford ---
    t0 = time.perf_counter()
    b_dist, b_parent, b_nearest, neg_cycle = bellman_ford_nearest_exit(g, exits)
    t_bf = time.perf_counter() - t0
    b_route = reconstruct_route(b_parent, args.start, b_nearest)

    print(f"=== Evacuation plan for room {args.start} ===")
    print(f"[Dijkstra]      time to nearest exit = {d_dist[args.start]:.2f} min "
          f"(exit {d_nearest[args.start]}), runtime = {t_dijkstra*1000:.3f} ms")
    print(f"                route: {' -> '.join(map(str, d_route))}")
    print(f"[Bellman-Ford]  time to nearest exit = {b_dist[args.start]:.2f} min "
          f"(exit {b_nearest[args.start]}), runtime = {t_bf*1000:.3f} ms")
    print(f"                route: {' -> '.join(map(str, b_route))}")
    print(f"                negative-cycle check: {'CYCLE DETECTED' if neg_cycle else 'none (expected)'}")

    agree = abs(d_dist[args.start] - b_dist[args.start]) < 1e-6
    print(f"\nCross-check: distances {'MATCH ✓' if agree else 'DO NOT MATCH ✗'}")
    speedup = t_bf / t_dijkstra if t_dijkstra > 0 else float('inf')
    print(f"Speedup (Bellman-Ford / Dijkstra): {speedup:.1f}x")


if __name__ == "__main__":
    main()
