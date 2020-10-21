@echo off
set OSGEO4W_ROOT=C:\OSGeo4W64
call "%OSGEO4W_ROOT%"\bin\o4w_env.bat

@echo off
path %PATH%;%OSGEO4W_ROOT%\apps\qgis\bin
path %PATH%;%OSGEO4W_ROOT%\apps\Qt5\bin
path %OSGEO4W_ROOT%\apps\Python37;%OSGEO4W_ROOT%\apps\Python37\Scripts;C:\OSGeo4W64\apps\Python37\lib\site-packages;%PATH%


set PYTHONPATH=%PYTHONPATH%;%OSGEO4W_ROOT%\apps\qgis\python
set PYTHONHOME=%OSGEO4W_ROOT%\apps\Python37

cmd.exe