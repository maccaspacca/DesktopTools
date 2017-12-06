cd "<full path to desktools.py>" 

rem - edit the above line to the path of your files

pyinstaller.exe --uac-admin --onefile --noconsole --log-level=INFO desktools.py --icon=db.ico --hidden-import=ticons

pause
