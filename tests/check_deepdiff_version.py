"""Quick check of DeepDiff version and basic functionality"""

import deepdiff

print(f"DeepDiff version: {deepdiff.__version__}")

# Test from DeepDiff documentation
from deepdiff import DeepDiff

t1 = {1: 1, 2: 2, 3: 3}
t2 = {1: 1, 2: "2", 4: 4}

print("\nBasic example from docs:")
print(f"t1: {t1}")
print(f"t2: {t2}")

ddiff = DeepDiff(t1, t2)
print(f"\nDeepDiff result: {ddiff}")
