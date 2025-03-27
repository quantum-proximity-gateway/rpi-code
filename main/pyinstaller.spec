# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[
        # Flask related
        'flask',
        'flask_cors',
        'pydantic',
        'coloredlogs',
        
        # Bluetooth related
        'bluepy.btle',
        
        # Custom modules
        'scan',
        'recognise',
        'uart_rpi5',
        'encryption_client',
        'aesgcm_encryption',
        
        # Computer vision & hardware
        'face_recognition',
        'cv2',
        'numpy',
        'picamera2',
        'serial',
        
        # Encryption related
        'oqs',
        'cryptography.hazmat.primitives.ciphers.aead',
        'cryptography.hazmat.primitives.ciphers',
        'cryptography.hazmat.primitives',
        'cryptography.hazmat',
        'cryptography',
        
        # Standard libraries that might be missed
        'base64',
        'uuid',
        'json',
        'time',
        'logging',
        'threading',
        'os',
        
        # Web related
        'requests',
        'urllib3',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# Include any data files like cascades for CV
a.datas += [
    # If you have any data files to include, add them here
    # ('path/to/included/file', '/abs/path/to/your/file', 'DATA'),
]

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='proximity_gateway',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='proximity_gateway',
)