"""
bellman_ford.py
----------------
Algorithm B (comparison baseline): Bellman-Ford single-source shortest path,
implemented from scratch.

Used here for two purposes mandated by the brief:
  1. As a SLOWER baseline that must agree exactly with Dijkstra's distances
     on every instance (our correctness cross-check, criterion A5).
  2. As the algorithm that would remain correct even if some corridor
     weights were negative (e.g. a corridor whose effective traversal time
     is reduced once an emergency door is forced open) -- a case where
     Dijkstra's greedy assumption breaks but Bellman-Ford's relaxation
     approach still works, which is the qualitative contrast we report
     in the Analysis section (A3).

Same multi-source trick as dijkstra.py: a virtual super-source with
zero-weight edges to every exit collapses "distance to nearest of several
exits" into a single-source shortest path problem.
"""

from graph import Graph

INF = float('inf')


def bellman_ford_nearest_exit(g: Graph, exits: list[int]):
    """
    Compute, for every vertex, the shortest walking time to the nearest
    evacuation exit using Bellman-Ford relaxation (no priority queue).

    Returns the same (dist, parent, nearest_exit) shape as
    dijkstra.dijkstra_nearest_exit so the two are directly comparable.

    Complexity: O(V * E) worst case -- V-1 full relaxation passes over all
    E edges, since in the worst case information propagates one hop per
    pass. We also run ONE extra pass to detect negative-weight cycles
    (none expected in this problem, but it is a correctness requirement of
    Bellman-Ford as a general algorithm and is reported as part of A1/A2).
    """
    n = g.n
    dist = {v: INF for v in range(n)}
    parent = {v: None for v in range(n)}
    nearest_exit = {v: None for v in range(n)}

    for e in exits:
        dist[e] = 0.0
        nearest_exit[e] = e

    # Materialize the edge list once (Bellman-Ford relaxes by edge, not by
    # popping a frontier vertex like Dijkstra does).
    edge_list = list(g.edges())

    # V-1 relaxation passes.
    for _ in range(n - 1):
        changed = False
        for u, v, w in edge_list:
            if dist[u] == INF:
                continue
            nd = dist[u] + w
            if nd < dist[v]:
                dist[v] = nd
                parent[v] = u
                nearest_exit[v] = nearest_exit[u]
                changed = True
        if not changed:
            break  # early exit once no edge relaxes further (common in practice)

    # Extra pass: detect a negative-weight cycle (general-purpose correctness
    # check; our generated graphs have non-negative weights so this should
    # never trigger, but we report it honestly per A1).
    has_negative_cycle = False
    for u, v, w in edge_list:
        if dist[u] != INF and dist[u] + w < dist[v]:
            has_negative_cycle = True
            break

    return dist, parent, nearest_exit, has_negative_cycle
