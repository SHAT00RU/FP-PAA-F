"""
test_correctness.py
--------------------
Quick correctness cross-check: runs Dijkstra and Bellman-Ford on the SAME
generated campus graphs and asserts that every vertex's distance-to-nearest-
exit matches exactly. This is the empirical correctness evidence cited in
the report's Analysis & Evaluation section (criterion A5).

Run with: python test_correctness.py
"""

import sys
from graph import generate_campus_graph
from dijkstra import dijkstra_nearest_exit
from bellman_ford import bellman_ford_nearest_exit


def run_check(n_vertices: int, n_exits: int, seed: int) -> bool:
    g = generate_campus_graph(n_vertices, avg_degree=5, seed=seed)
    exits = list(range(n_exits))  # designate first n_exits vertices as exits

    d_dist, _, _ = dijkstra_nearest_exit(g, exits)
    b_dist, _, _, has_neg_cycle = bellman_ford_nearest_exit(g, exits)

    assert not has_neg_cycle, "Unexpected negative cycle in a non-negative graph!"

    mismatches = []
    for v in range(n_vertices):
        dd = d_dist[v]
        bd = b_dist[v]
        if dd == float('inf') and bd == float('inf'):
            continue
        if abs(dd - bd) > 1e-6:
            mismatches.append((v, dd, bd))

    if mismatches:
        print(f"  MISMATCH for n={n_vertices}, seed={seed}: {mismatches[:5]}")
        return False
    print(f"  OK  n={n_vertices:6d} exits={n_exits:3d} seed={seed} "
          f"-> all {n_vertices} distances agree (max dist "
          f"{max(d for d in d_dist.values() if d != float('inf')):.2f})")
    return True


if __name__ == "__main__":
    print("Cross-checking Dijkstra vs Bellman-Ford on identical graph instances...")
    all_ok = True
    test_cases = [
        (50, 2, 1),
        (200, 3, 7),
        (1000, 5, 42),
        (2000, 5, 99),
    ]
    for n, k, s in test_cases:
        ok = run_check(n, k, s)
        all_ok = all_ok and ok

    if all_ok:
        print("\nAll cross-checks PASSED: Dijkstra and Bellman-Ford agree exactly.")
        sys.exit(0)
    else:
        print("\nSome cross-checks FAILED.")
        sys.exit(1)
