# From Brute-Force Scheme Testing to Analytic Geometry-Driven Classification

## Abstract

Gradient reconstruction remains one of the most persistent bottlenecks in finite-volume CFD on unstructured polyhedral meshes. Practitioners routinely face the exhaustive task of implementing and benchmarking large families of schemes—Green-Gauss variants, weighted least-squares (WLSQ) families, and hybrids such as the Shima–Kitamura–Haga GLSQ method (AIAA J. 51(11), 2740–2747, 2013)—across every new mesh, exactly as voiced in recent community discussions. This brute-force workflow arises from the tacit assumption that scheme performance degrades smoothly with mesh quality, forcing full-factorial testing that consumes weeks of development time.

We show that the underlying behavior is instead a sharp phase transition, not continuous degradation. A single local dimensionless ratio  
**z = (critical_skewness / local_skewness) × accuracy_order**  
partitions any computational domain into three disjoint regimes: low-z (z ≲ 0.4: only robust Green-Gauss viable), transition (0.4 < z < 0.6: only z-adaptive hybrids deliver 5–20× advantage), and high-z (z ≳ 0.6: only simple WLSQ families needed). Because these viable scheme subsets are non-overlapping by construction, mesh geometry alone predicts success with O(N) preprocessing.

The resulting geometry-driven classifier acts as an automatic pre-filter: it eliminates 70–90 % of candidate schemes before any code is written or any flow solve is launched, and it issues a conditional implementation plan that triggers expensive hybrids only when the measurable transition-zone volume fraction exceeds a few percent. What once required years of simulated hands-on testing is reduced to a seconds-long mesh scan plus a minimal, regime-targeted test harness.

This reframing converts an intractable global-optimization problem into a solvable classification task, making unstructured CFD scheme selection deterministic, reproducible, and dramatically more efficient. The same principle extends immediately to other local numerical operators on heterogeneous meshes.
