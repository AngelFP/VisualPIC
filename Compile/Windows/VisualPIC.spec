# -*- mode: python -*-

block_cipher = None


a = Analysis(['..\\..\\VisualPIC\\__main__.py'],
             pathex=['C:\\Users\\Angel\\Source\\Repos\\VisualPIC\\VisualPIC'],
             binaries=[],
             datas=[('../../VisualPIC/Views/aboutWindow.ui', '.'), 
                    ('../../VisualPIC/Views/DataVisualizerGUI.ui', '.'), 
                    ('../../VisualPIC/Views/EditPlotFieldWindow.ui', '.'), 
                    ('../../VisualPIC/Views/ParticleTracker.ui', '.'),
                    ('../../VisualPIC/Icons/1462905433_basics-15.png', 'Icons'),
                    ('../../VisualPIC/Icons/deleteIcon.png', 'Icons'),
                    ('../../VisualPIC/Icons/editIcon.png', 'Icons'),
                    ('../../VisualPIC/Icons/icon-ios7-arrow-left-128.png', 'Icons'),
                    ('../../VisualPIC/Icons/icon-ios7-arrow-right-128.png', 'Icons'),
                    ('../../VisualPIC/Icons/logo.PNG', 'Icons'),
                    ('../../VisualPIC/Icons/logo_horizontal.png', 'Icons'),
                    ('../../VisualPIC/Icons/SelectionRectangle.png', 'Icons')],
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
          console=False,
          icon='..\\..\\VisualPIC\\Icons\\WindowsIcon.ico' )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='VisualPIC')
