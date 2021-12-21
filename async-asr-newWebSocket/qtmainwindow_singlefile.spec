# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['qtmainwindow.py'],
             pathex=['D:\\async-asr'],
             binaries=[],
             datas=[('./icons/', './icons/'), ('./VideoLAN', './VideoLAN')],
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
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='qtmainwindow',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=True )
