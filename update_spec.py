#!/usr/bin/env python3
import re
import sys

if len(sys.argv) != 3:
    print("Usage: python update_spec.py <spec_file> <new_name>")
    sys.exit(1)

spec_file = sys.argv[1]
new_name = sys.argv[2]

with open(spec_file, 'r') as f:
    content = f.read()

print(f"Updating {spec_file} with name: {new_name}")

# Replace the name parameter
content = re.sub(r"name='pomera'", f"name='{new_name}'", content)

with open(spec_file, 'w') as f:
    f.write(content)

print(f"Successfully updated {spec_file}")