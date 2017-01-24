pyinstaller VisualPIC.spec
RD /S /Q "build"
cd dist
DEL /Q "VisualPIC.zip"
powershell.exe -nologo -noprofile -command "& { Add-Type -A 'System.IO.Compression.FileSystem'; [IO.Compression.ZipFile]::CreateFromDirectory('VisualPIC', 'VisualPIC.zip'); }"