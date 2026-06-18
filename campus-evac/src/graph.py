"""
graph.py
--------
Minimal weighted-graph representation used by both shortest-path algorithms.

The graph is stored as an adjacency list: a dict mapping each vertex id (int)
to a list of (neighbor, weight) tuples. This is the standard representation
for sparse graphs (our campus graphs have E = O(V), so an adjacency list is
the right choice over an adjacency matrix which would cost O(V^2) memory).

This module contains NO algorithmic logic (no shortest-path code) -- it is
purely a data container plus a synthetic campus-graph generator used for
benchmarking at scale. Dijkstra and Bellman-Ford live in their own files.
"""

import random


class Graph:
    """Weighted, directed graph stored as an adjacency list.

    Undirected graphs are represented by inserting both (u, v) and (v, u),
    which is how the campus generator below builds corridors (a corridor
    can be walked in either direction).
    """

    def __init__(self, n_vertices: int):
        self.n = n_vertices
        self.adj = {v: [] for v in range(n_vertices)}
        self.edge_count = 0

    def add_edge(self, u: int, v: int, weight: float, directed: bool = False):
        self.adj[u].append((v, weight))
        self.edge_count += 1
        if not directed:
            self.adj[v].append((u, weight))
            self.edge_count += 1

    def edges(self):
        """Yield every directed edge (u, v, w) exactly as stored."""
        for u, neighbors in self.adj.items():
            for v, w in neighbors:
                yield u, v, w

    def __len__(self):
        return self.n


def generate_campus_graph(n_vertices: int, avg_degree: int = 5, seed: int = 42,
                           min_weight: float = 0.5, max_weight: float = 12.0) -> Graph:
    """
    Generate a synthetic 'campus corridor network' graph for benchmarking.

    Why this generator and not a pure Erdos-Renyi random graph:
    Real campuses are laid out somewhat like a planar mesh (buildings connect
    mostly to nearby buildings, plus a few long corridors/shortcuts), so we
    build a connected backbone (a random spanning structure) first to
    guarantee reachability, then add extra random edges up to the target
    average degree to create realistic redundancy (multiple evacuation
    routes), which is exactly the property an evacuation planner cares about.

    Parameters
    ----------
    n_vertices : number of rooms/junctions/buildings (graph size n)
    avg_degree : target average out-degree (controls edge density E ~ avg_degree * n)
    seed       : RNG seed for reproducibility (REQUIRED by the assignment)
    min_weight, max_weight : edge weight range, representing walking time in
                              minutes along a corridor segment

    Returns
    -------
    Graph with n_vertices vertices, guaranteed connected.
    """
    rng = random.Random(seed)
    g = Graph(n_vertices)

    # Step 1: guarantee connectivity with a random spanning tree.
    # We connect each new vertex i (for i = 1..n-1) to a uniformly random
    # earlier vertex. This is the standard "random recursive tree" trick for
    # producing a connected backbone in O(n).
    for i in range(1, n_vertices):
        parent = rng.randint(0, i - 1)
        w = round(rng.uniform(min_weight, max_weight), 2)
        g.add_edge(i, parent, w)

    # Step 2: add extra random edges until we hit the target average degree.
    # Real corridors are local, so we bias extra edges toward nearby vertex
    # ids (a crude proxy for spatial locality on a campus map) but still
    # allow some long-range shortcuts (e.g. a tunnel or skybridge).
    target_edges = (avg_degree * n_vertices) // 2  # undirected edge count
    existing_tree_edges = n_vertices - 1
    extra_needed = max(0, target_edges - existing_tree_edges)

    added = 0
    attempts = 0
    max_attempts = extra_needed * 20 + 100
    seen_pairs = set()

    while added < extra_needed and attempts < max_attempts:
        attempts += 1
        u = rng.randint(0, n_vertices - 1)
        # 70% local edge (within a window of 50 ids), 30% long-range shortcut
        if rng.random() < 0.7:
            span = min(50, n_vertices - 1)
            offset = rng.randint(1, span) if span > 0 else 1
            v = (u + offset) % n_vertices
        else:
            v = rng.randint(0, n_vertices - 1)

        if u == v:
            continue
        key = (min(u, v), max(u, v))
        if key in seen_pairs:
            continue
        seen_pairs.add(key)

        w = round(rng.uniform(min_weight, max_weight), 2)
        g.add_edge(u, v, w)
        added += 1

    return g
