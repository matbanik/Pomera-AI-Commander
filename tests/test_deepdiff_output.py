"""Test to see what DeepDiff actually returns in the values_changed dict."""
import json
from deepdiff import DeepDiff

before = json.loads('{"result": "1", "reason": null}')
after = json.loads('{"result": "ok", "reason": "not dull"}')

diff = DeepDiff(before, after, ignore_order=False, ignore_string_case=True,
               ignore_type_in_groups=[(int, float, str)], verbose_level=2)

print("DEEPDIFF_KEYS=" + str(list(diff.keys())))
if 'values_changed' in diff:
    print(f"VALUES_CHANGED_COUNT={len(diff['values_changed'])}")
    for i, (path, change) in enumerate(diff['values_changed'].items()):
        print(f"PATH_{i}={path}")
        print(f"OLD_{i}={change.get('old_value')}")
        print(f"NEW_{i}={change.get('new_value')}")
