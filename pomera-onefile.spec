# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['pomera.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['pytest', 'test', 'tests', 'matplotlib', 'scipy', 'pandas', 'jupyter', 'IPython', 'torch', 'torchvision', 'torchaudio', 'tensorflow', 'sklearn', 'cv2', 'numpy', 'pygame', 'nltk', 'spacy', 'yt_dlp', 'transformers', 'boto3', 'botocore', 'grpc', 'onnxruntime', 'opentelemetry', 'timm', 'emoji', 'pygments', 'jinja2', 'anyio', 'orjson', 'uvicorn', 'fsspec', 'websockets', 'psutil', 'regex'],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='pomera-onefile',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
