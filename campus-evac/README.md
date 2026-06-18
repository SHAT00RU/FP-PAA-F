# EvacRoute — Fastest-Path Campus Evacuation Planner

**EF234405 Design & Analysis of Algorithms — Final Exam (Group Capstone Project)**
2025/2026(2)

A campus evacuation route planner that models a building complex as a weighted
graph and computes the fastest route from any room to its nearest evacuation
exit, using two independently implemented algorithms:

- **Algorithm A — Dijkstra's algorithm** (binary min-heap), the core, non-trivial
  algorithm.
- **Algorithm B — Bellman-Ford**, used both as a comparison baseline and as a
  correctness cross-check (the two algorithms share no relaxation logic and
  must agree exactly on every instance).

Both algorithms solve the same "nearest of several exits" problem via a
standard virtual super-source reduction (a zero-weight edge from a synthetic
source to every exit), so a single-source shortest-path algorithm directly
answers the multi-target evacuation question.

## Team

| Name | Student ID | Class | Role |
|------|-------------|-------|------|
| [Member 1 Full Name] | [5025221xxx] | [D/IUP/E/F/G] | Model & Dijkstra |
| [Member 2 Full Name] | [5025221xxx] | [D/IUP/E/F/G] | Bellman-Ford & demo |
| [Member 3 Full Name] | [5025221xxx] | [D/IUP/E/F/G] | Analysis & benchmarks |

## Repository structure

```
.
├── README.md
├── requirements.txt
├── src/
│   ├── graph.py              # Graph class + synthetic campus-graph generator
│   ├── dijkstra.py            # Algorithm A: Dijkstra (binary heap), from scratch
│   ├── bellman_ford.py        # Algorithm B: Bellman-Ford, from scratch
│   ├── demo.py                 # End-to-end CLI demo
│   └── test_correctness.py     # Automated Dijkstra-vs-Bellman-Ford cross-check
└── bench/
    ├── benchmark.py             # ONE-COMMAND reproducible benchmark harness
    ├── results.csv               # Generated benchmark output (committed for convenience)
    ├── runtime_vs_n_loglog.png
    └── runtime_vs_n_linear.png
```

## Setup

Requires Python 3.10+ (developed and tested on Python 3.12).

```bash
git clone https://github.com/[your-username]/evacroute-daa-final.git
cd evacroute-daa-final
pip install -r requirements.txt
```

The only third-party dependency is `matplotlib`, used solely to render the
benchmark plots. **No graph library is used anywhere for algorithmic logic** —
Dijkstra and Bellman-Ford are implemented entirely from scratch in
`src/dijkstra.py` and `src/bellman_ford.py`. The only library primitive used
is Python's built-in `heapq` module, which supplies a generic binary-heap
data structure (not a shortest-path routine).

## Usage

### 1. Correctness cross-check

Runs both algorithms on several graph sizes and asserts every per-vertex
distance matches exactly:

```bash
python src/test_correctness.py
```

### 2. Interactive demo

Computes the fastest evacuation route from a chosen room, with both
algorithms, and reports their agreement and relative speed:

```bash
python src/demo.py --n 1000 --exits 5 --start 17 --seed 42
```

Options: `--n` (graph size), `--exits` (number of evacuation exits),
`--start` (room to evacuate from), `--seed` (RNG seed), `--avg-degree`
(average corridor connections per room).

### 3. Reproduce the full benchmark (one command)

```bash
python bench/benchmark.py
```

This regenerates `bench/results.csv` and both plots from scratch, using a
fixed seed (42) and six input sizes from n = 100 to n = 30,000 (2.5 orders
of magnitude), as required by the assignment brief. No arguments needed —
every parameter is a documented constant at the top of `bench/benchmark.py`.

## Algorithm summary

| | Dijkstra (binary heap) | Bellman-Ford |
|---|---|---|
| Time (worst case) | O((V + E) log V) | O(V · E) |
| Space | O(V + E) | O(V + E) |
| Requires non-negative weights | Yes | No |
| Detects negative cycles | No | Yes |

See `Report.pdf` for the full correctness proofs, complexity derivations,
empirical results, and theory-vs-practice discussion.

## Citations / attribution

- T. H. Cormen, C. E. Leiserson, R. L. Rivest, and C. Stein, *Introduction to
  Algorithms*, 4th ed., MIT Press, 2022 — algorithm descriptions and
  complexity analysis referenced throughout.
- Python `heapq` standard library module — generic binary-heap primitive used
  inside `dijkstra.py` (no shortest-path logic taken from it).
- `matplotlib` — used only to render `bench/*.png`.

## Academic integrity

All core algorithmic logic (Dijkstra and Bellman-Ford relaxation) in this
repository is the team's own work, written from scratch as required by the
assignment brief. See `Declaration.pdf` (submitted separately) for the
signed academic integrity pledge.
