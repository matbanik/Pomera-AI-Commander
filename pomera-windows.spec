# -*- mode: python ; coding: utf-8 -*-

import sys
import os

# Add the current directory to the path
sys.path.insert(0, os.path.abspath('.'))

block_cipher = None

# Define the analysis
a = Analysis(
    ['pomera.py'],
    pathex=['.'],
    binaries=[],
    datas=[
        ('tools', 'tools'),  # Include the tools directory
        ('core', 'core'),    # Include the core directory
    ],
    hiddenimports=[
        # Tools modules
        'tools.ai_tools',
        'tools.find_replace',
        'tools.diff_viewer',
        'tools.base64_tools',
        'tools.case_tool',
        'tools.cron_tool',
        'tools.curl_history',
        'tools.curl_processor',
        'tools.curl_settings',
        'tools.curl_tool',
        'tools.email_extraction_tool',
        'tools.email_header_analyzer',
        'tools.folder_file_reporter_adapter',
        'tools.folder_file_reporter',
        'tools.generator_tools',
        'tools.html_tool',
        'tools.huggingface_helper',
        'tools.jsonxml_tool',
        'tools.list_comparator',
        'tools.sorter_tools',
        'tools.translator_tools',
        'tools.url_link_extractor',
        'tools.url_parser',
        'tools.regex_extractor',
        'tools.word_frequency_counter',
        # Core modules
        'core',
        # External dependencies
        'requests',
        'reportlab.pdfgen.canvas',
        'reportlab.lib.pagesizes',
        'docx',
        'huggingface_hub',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'pytest',
        'test',
        'tests',
        'matplotlib',
        'scipy',
        'pandas',
        'jupyter',
        'IPython',
        'torch',
        'torchvision',
        'torchaudio',
        'tensorflow',
        'sklearn',
        'cv2',
        'pygame',
        'nltk',
        'spacy',
        'yt_dlp',
        'transformers',
        'boto3',
        'botocore',
        'grpc',
        'onnxruntime',
        'opentelemetry',
        'timm',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='pomera-v1.0.1-test-windows',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Set to False for GUI applications
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)