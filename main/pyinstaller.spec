# -*- mode: python ; coding: utf-8 -*-
import os
import bluepy
import sys

block_cipher = None

# Find the bluepy path
bluepy_path = os.path.dirname(bluepy.__file__)

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        # Include bluepy data files
        (os.path.join(bluepy_path, 'bluepy-helper'), 'bluepy'),
        (os.path.join(bluepy_path, '*.json'), 'bluepy'),
    ],
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

# Include bluepy data files more explicitly
for root, dirs, files in os.walk(bluepy_path):
    for file in files:
        if file.endswith('.json'):
            source = os.path.join(root, file)
            dest = os.path.join('bluepy', os.path.relpath(source, bluepy_path))
            a.datas.append((dest, source, 'DATA'))

# Include the bluepy-helper binary
helper_path = os.path.join(bluepy_path, 'bluepy-helper')
if os.path.exists(helper_path):
    a.datas.append(('bluepy/bluepy-helper', helper_path, 'DATA'))
else:
    print("WARNING: bluepy-helper not found at", helper_path)

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