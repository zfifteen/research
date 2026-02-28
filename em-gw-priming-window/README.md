# EM-GW Priming Window

This project develops and documents a timing-dependent coupling mechanism between solar electromagnetic (EM) forcing and tropospheric gravity-wave (GW) forcing in the ionosphere.

## Abstract
Solar electromagnetic events (flares and high-speed solar-wind streams) can create transient ionospheric conductivity enhancements that persist for roughly 3-10 hours after the main forcing phase. In this framework, that persistence acts as a one-way memory gate that multiplicatively amplifies ionospheric responses to later-arriving tropospheric gravity waves. We define a coupling intensity, `Lambda = r_sigma(t) x (E_GW/E_0)`, with three regimes: sub-threshold (`Lambda < 1`), linear multiplicative (`1 <= Lambda <= 3`), and nonlinear amplified (`Lambda > 3`). This asymmetric, lag-dependent interaction explains why moderate solar and moderate weather disturbances can jointly produce stronger responses than isolated strong drivers. It also provides a physical basis for solar-activity correction terms in heuristic Schumann-resonance formulations. The project includes an explicit memory-kernel parameterization and figure-generation scripts to support hypothesis communication and testing with SZIGO, GNSS TEC, and public EM/GW proxy data.

## Repository Layout
- `docs/`: manuscript notes and supporting text.
- `scripts/`: figure-generation and analysis scripts.
- `figures/`: generated plots and figure assets.
- `slides/`: presentation decks.
- `videos/`: recorded talks and visual explainers.

## Presentations and Video
- Slides (PPTX): [`slides/priming-window-framework.pptx`](./slides/priming-window-framework.pptx)
- Video (MP4): [`videos/Solar-Terrestrial Coupling.mp4`](./videos/Solar-Terrestrial%20Coupling.mp4)

### Embedded Video
<video src="./videos/Solar-Terrestrial%20Coupling.mp4" controls width="960">
  Your viewer does not support embedded video.
</video>

If the embedded player is not shown in your markdown viewer, open the file directly: [`Solar-Terrestrial Coupling.mp4`](./videos/Solar-Terrestrial%20Coupling.mp4).

## Generate Timeline Figure
Run from the repository root:

```bash
/Library/Frameworks/Python.framework/Versions/3.12/bin/python3 em-gw-priming-window/scripts/make_timeline.py
```

The script writes:

- `em-gw-priming-window/figures/em-gw-priming-timeline.png`

Optional flags:

- `--output <path>`: write to a custom output path.
- `--show`: display the plot interactively after saving.

## Notes
- The default macOS `python3` in this environment may have a local NumPy/Matplotlib ABI mismatch. If so, use Python 3.12+ (as above) or a clean virtual environment with compatible `numpy` and `matplotlib` versions.
