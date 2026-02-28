"""Get exact button lines for each tool file missing hints"""
import os, re

tools_dir = r'P:\Pomera-AI-Commander\tools'

MISSING = [
    'ai_tools.py', 'cron_tool.py', 'curl_tool.py', 'diff_viewer.py',
    'email_extraction_tool.py', 'email_header_analyzer.py',
    'folder_file_reporter_adapter.py', 'jsonxml_tool.py', 'list_comparator.py',
    'mcp_widget.py', 'notes_widget.py', 'regex_extractor.py', 'sorter_tools.py',
    'text_statistics_tool.py', 'url_link_extractor.py', 'url_parser.py',
    'word_frequency_counter.py',
]

# Also check which of these inherit from BaseTool and which don't
for f in MISSING:
    path = os.path.join(tools_dir, f)
    with open(path, 'r', encoding='utf-8') as fh:
        content = fh.read()
        lines = content.split('\n')
    
    # Check inheritance
    inherits = 'BaseTool' in content or 'SimpleProcessingTool' in content or 'ToolWithOptions' in content
    uses_base_apply = '_create_apply_button' in content and 'def _create_apply_button' not in content
    
    # Find all Button creations 
    btn_lines = []
    for i, line in enumerate(lines):
        s = line.strip()
        if ('Button(' in s and ('Process' in s or 'Apply' in s or 'Generate' in s or 
            'Search' in s or 'Fetch' in s or 'Convert' in s or 'Extract' in s or
            'Compare' in s or 'Send' in s or 'Analyze' in s or 'Report' in s or
            'Parse' in s or 'Wrap' in s or 'command=' in s)):
            btn_lines.append(f'  L{i+1}: {s[:100]}')
    
    status = '🔧 inherits BaseTool' if inherits else '⚠️  NO BaseTool'
    apply_str = ', uses _create_apply_button' if uses_base_apply else ''
    print(f"\n{'='*60}")
    print(f"{f} ({status}{apply_str})")
    if btn_lines:
        for b in btn_lines:
            print(b)
    else:
        print("  (no explicit Button found — inherits)")
