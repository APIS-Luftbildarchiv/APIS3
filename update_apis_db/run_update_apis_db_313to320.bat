@echo off
echo Update APIS DB from 3.1.3 to 3.2.0
call "C:\OSGeo4W\bin\o4w_env.bat"
call "C:\OSGeo4W\bin\python-qgis.bat" update_apis_db_313to320.py
pause