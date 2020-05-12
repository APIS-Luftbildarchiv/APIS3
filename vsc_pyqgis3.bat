@echo off
set OSGEO4W_ROOT=C:\OSGeo4W64
path %PATH%;%OSGEO4W_ROOT%\apps\qgis\bin
path %PATH%;%OSGEO4W_ROOT%\apps\grass\grass-7.4.2\lib
path %PATH%;%OSGEO4W_ROOT%\apps\Qt5\bin
path %PATH%;%OSGEO4W_ROOT%\apps\qgis\python\qgis\PyQt
path %PATH%;%OSGEO4W_ROOT%\apps\Python37\Scripts
set PYTHONPATH=%PYTHONPATH%;%OSGEO4W_ROOT%\apps\qgis\python
set PYTHONHOME=%OSGEO4W_ROOT%\apps\Python37
path %PATH%;%OSGEO4W_ROOT%\apps\Python37\Scripts

start "VSCode QGIS" /B "C:\Users\johannes\AppData\Local\Programs\Microsoft VS Code\Code.exe" %*