# Green Penetration Ratio

Green's Theorem is usually taught as giving you two equivalent ways to compute the same circulation, but it actually reveals an asymmetry in measurement robustness: when vorticity concentrates far from the boundary, interior area measurements become more reliable than boundary measurements, and vice versa.

The key is not where the vorticity exists, but where its "center of mass" sits relative to how deep the region extends inward.

If you compute the average distance of all the swirling motion from the edge and divide by the maximum possible distance from edge to interior, you get a penetration ratio between 0 and 1.

When this ratio drops below 0.4, meaning spin concentrates near the boundary, any errors or wiggles in your boundary path measurement get amplified much less than errors in trying to map the interior.

When the ratio exceeds 0.6, meaning spin lives deep in the interior, your boundary measurements become fragile because they have to infer distant sources through a long integration path.

This matters practically when you have a fixed measurement budget and need to decide whether to instrument the perimeter with sensors or blanket the interior with probes.

The theorem itself has always been true, but it hides a geometric leverage effect where distance acts as a transfer function between source uncertainty and boundary observation uncertainty.

Most applications treat the two integrals as computationally interchangeable, missing that they represent physically distinct measurement strategies with different noise sensitivities.

---
