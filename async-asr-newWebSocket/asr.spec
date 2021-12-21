# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['qtmainwindow.py'],
             pathex=['C:\\Users\\desmo\\Desktop\\FYP-Fork\\async-asr'],
             binaries=[],
             datas=[('./icons/', './icons/'),('colorcode.ini', '.'), ('./VideoLAN', './VideoLAN'), ('hotkey.ini', '.'), ('last_config.ini', '.'), ('services.ini', '.'),('./venv/Lib/site-packages/librosa/util/example_data','librosa/util/example_data'),('./venv/Lib/site-packages/PyQt5/Qt/bin','PyQt5/Qt/bin')],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=['runtimefirst.py'],
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
