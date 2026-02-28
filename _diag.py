"""Find the main Process button and all apply_callback buttons"""
with open(r'P:\Pomera-AI-Commander\pomera.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print("=== Process/Apply buttons ===")
for i, line in enumerate(lines):
    s = line.strip()
    if ('text="Process"' in s or "text='Process'" in s or 
        'text="Apply"' in s or "text='Apply'" in s or
        'text="Generate"' in s or "text='Generate'" in s or
        'text="Search"' in s or "text='Search'" in s or
        'text="Fetch"' in s or "text='Fetch'" in s or
        'apply_callback' in s):
        print(f'{i+1}: {s[:140]}')

print("\n=== self.process_button / btn ===")
for i, line in enumerate(lines):
    s = line.strip()
    if ('process_button' in s or 'process_btn' in s) and '=' in s:
        print(f'{i+1}: {s[:140]}')
