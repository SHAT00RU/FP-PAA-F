"""
dijkstra.py
-----------
Algorithm A (the non-trivial, core algorithm): Dijkstra's single-source
shortest path, implemented from scratch with a binary min-heap.

We adapt it to the evacuation problem by running it from a SINGLE SUPER-SOURCE
that is connected with zero-weight edges to every designated evacuation
exit. This is the standard trick for turning a "nearest of several targets"
problem into a plain single-source shortest-path problem: the distance from
the super-source to any room v equals the distance from v to its nearest
exit (since all the super-source's edges have weight 0).

We do NOT call any library's heap-based shortest path routine (e.g.
networkx.dijkstra_path or scipy.sparse.csgraph.dijkstra). We only use
Python's `heapq` module as a generic priority-queue primitive (allowed by
the brief: "you may use a library for supporting structures (heaps, ...)").
All relaxation logic is ours.
"""

import heapq
from graph import Graph


INF = float('inf')


def dijkstra_nearest_exit(g: Graph, exits: list[int]):
    """
    Compute, for every vertex, the shortest walking time to the NEAREST
    evacuation exit, using a multi-source Dijkstra via a virtual super-source.

    Parameters
    ----------
    g     : Graph (must have non-negative edge weights; Dijkstra requires this)
    exits : list of vertex ids designated as evacuation exits

    Returns
    -------
    dist   : dict {vertex: shortest_time_to_nearest_exit}
    parent : dict {vertex: predecessor on the shortest path toward an exit}
             (parent[v] = the next hop FROM v TOWARD the exit it was reached
              from, used to reconstruct an evacuation route for any room)
    nearest_exit : dict {vertex: which exit vertex it is closest to}

    Complexity: O((V + E) log V) with a binary heap, since each vertex is
    popped at most once and each edge can trigger at most one push.
    """
    n = g.n
    dist = {v: INF for v in range(n)}
    parent = {v: None for v in range(n)}
    nearest_exit = {v: None for v in range(n)}
    visited = [False] * n

    # Virtual super-source S: distance 0 to every real exit.
    pq = []  # heap of (distance, vertex)
    for e in exits:
        if dist[e] > 0:
            dist[e] = 0.0
            nearest_exit[e] = e
            heapq.heappush(pq, (0.0, e))

    while pq:
        d, u = heapq.heappop(pq)
        if visited[u]:
            continue  # stale heap entry (we don't support decrease-key directly)
        visited[u] = True

        for v, w in g.adj[u]:
            if visited[v]:
                continue
            nd = d + w
            if nd < dist[v]:
                dist[v] = nd
                parent[v] = u           # path runs v -> u -> ... -> exit
                nearest_exit[v] = nearest_exit[u]
                heapq.heappush(pq, (nd, v))

    return dist, parent, nearest_exit


def reconstruct_route(parent: dict, start: int, nearest_exit: dict) -> list[int]:
    """Rebuild the room-by-room evacuation route from `start` to its nearest exit."""
    if nearest_exit.get(start) is None:
        return []  # unreachable
    route = [start]
    cur = start
    while parent[cur] is not None:
        cur = parent[cur]
        route.append(cur)
    return route
