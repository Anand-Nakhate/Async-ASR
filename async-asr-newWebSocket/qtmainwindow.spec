# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['qtmainwindow.py'],
             pathex=['D:\\async-asr'],
             binaries=[],
             datas=[('./icons/', './icons/'), ('./VideoLAN', './VideoLAN'), ('./services_example.ini', './services_example.ini')],
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
          console=False,
          icon='./asricon.ico')
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='asr')