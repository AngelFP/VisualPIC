# -*- mode: python -*-

block_cipher = None


a = Analysis(['..\\..\\VisualPIC\\__main__.py'],
             pathex=['C:\\Users\\Angel\\Source\\Repos\\VisualPIC\\VisualPIC'],
             binaries=[],
             datas=[('../../VisualPIC/Views/*.ui', '.'), 
                    ('../../VisualPIC/Assets/Visualizer3D/Colormaps/*.h5', 'VisualPIC/Assets/Visualizer3D/Colormaps'),
                    ('../../VisualPIC/Assets/Visualizer3D/Opacities/*.h5', 'VisualPIC/Assets/Visualizer3D/Opacities'),
                    ('../../VisualPIC/Icons/*.png', 'Icons'),
                    ('../../VisualPIC/Icons/*.png', 'VisualPIC/Icons'),
                    ('../../VisualPIC/Icons/mpl/*.svg', 'VisualPIC/Icons/mpl')],
             hiddenimports=['h5py.defs','h5py.utils', 'h5py.h5ac', 'h5py._proxy'],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)

pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='VisualPIC',
          debug=False,
          strip=False,
          upx=True,
          console=True )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='VisualPIC')
