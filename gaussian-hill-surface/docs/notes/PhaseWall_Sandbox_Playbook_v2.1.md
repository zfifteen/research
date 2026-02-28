# PhaseWall Sandbox Execution Playbook v2.1

**Environment:** Clean Ubuntu/Python 3.11+ sandbox with git, pip, numpy, scipy.

**Run these commands in order:**

```bash
git clone https://github.com/CyberAgentAILab/cmaes.git phasewall-cmaes
cd phasewall-cmaes
git checkout -b feature/phasewall-z-damping
pip install -e ".[test]"

# Paste the apply_phase_wall_z function and patch ask() as described in Spec v2.1
# (use the exact code blocks from the spec)

cd ..
git clone https://github.com/optuna/optuna.git phasewall-optuna
cd phasewall-optuna
git checkout -b feature/phasewall

# Apply Optuna fallback wrapper

# Create and run benchmark
python examples/phasewall_benchmark.py --output results.csv

# Validation
pytest tests/ -q
ruff check .
mypy .

# Output deliverables
git diff > ../phasewall.patch
```
