# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['qtmainwindow.py'],
             pathex=['/home/desmond/Desktop/async-asr-newWebSocket'],
             binaries=[],
             datas=[('./icons/', './icons/'),('colorcode.ini', '.'), ('hotkey.ini', '.'), ('last_config.ini', '.'), ('services.ini', '.'),('/home/desmond/.local/lib/python3.8/site-packages/librosa/util/example_data','librosa/util/example_data'),('/usr/lib/libvlc.so.5', '.'),('/usr/lib/libvlccore.so.8', '.'),('/usr/lib/vlc/plugins', './vlc/plugins/'),('/usr/lib/vlc/libvlc_vdpau.so', '.'),('/usr/lib/vlc/libvlc_vdpau.so.0', '.')],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='asr',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='asr')