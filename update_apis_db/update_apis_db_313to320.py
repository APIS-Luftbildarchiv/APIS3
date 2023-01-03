# 1) Update Config INI - important repr. image dir fs
# 2) Rund this script

import pathlib
import shutil
import os.path
import glob
from PyQt5.QtCore import QDateTime, QSettings
from PyQt5.QtSql import QSqlDatabase, QSqlQuery

from osgeo import ogr
# from osgeo.gdalconst import GA_Update

# CHANGES
newCols = {
    'luftbild_schraeg_cp':
        [
            {'name': 'target', 'type': 'TEXT'}
        ],
    'luftbild_senk_cp':
        [
            {'name': 'target', 'type': 'TEXT'},
            {'name': 'beschreibung', 'type': 'TEXT'}
        ],
    'fundstelle':
        [
            {'name': 'repraesentatives_luftbild', 'type': 'TEXT'}
        ],
    'fundstelle_log':
        [
            {'name': 'repraesentatives_luftbild', 'type': 'TEXT'}
        ]
}

renameCols = {
    'luftbild_schraeg_cp':
        {
            'keyword': 'OBS_keyword',
            'description': 'OBS_description'
        }
}

sourceVersion = 313
targetVersion = 320
apisAppId = 116919  # 1=A 16=P 9=I 19=S

apisSettings = QSettings(QSettings().value("APIS/config_ini"), QSettings.IniFormat)

# sourceDbPath = pathlib.Path(apisSettings.value("APIS/repr_image_fs_dir"))
sourceDbPath = pathlib.Path('C:\\data\\development\\apis\\daten\\datenbank\\APISv3.sqlite')
targetDbPath = pathlib.Path(f'C:\\data\\development\\apis\\APIS3\\playground\\APISv{targetVersion}_{QDateTime.currentDateTime().toString("yyyyMMdd_hhmmss")}.sqlite')

# CHECK source DB
sourceDb = QSqlDatabase.addDatabase("QSPATIALITE")
sourceDb.setDatabaseName(sourceDbPath.as_posix())

checks = True
if not sourceDb.open():
    print("Database Error: {0}".format(sourceDb.lastError().text()))
    checks = False
else:
    q = QSqlQuery(sourceDb)

    # only for this version
    q.exec_(f"PRAGMA application_id = {apisAppId}")
    q.exec_(f"PRAGMA user_version = {sourceVersion}")

    q.exec_("PRAGMA application_id")
    q.seek(-1)
    while(q.next()):
        application_id = (q.record().value(0))
    if application_id != apisAppId:
        print("The source DB appears not be in the APIS DB Format.")
        checks = False
    q.exec_("PRAGMA user_version")
    q.seek(-1)
    while(q.next()):
        user_version = (q.record().value(0))
    if user_version != sourceVersion:
        print(f"The source DB appears not have the correct APIS version (found: {user_version}, expected: {sourceVersion}).")
        checks = False
    sourceDb.close()

if checks:
    print(f"Create copy of APIS DB v{sourceVersion}:", sourceDbPath)
    print(f"Save copy of APIS DB v{targetVersion}:", targetDbPath)

    shutil.copy(sourceDbPath, targetDbPath)

    # Open New DB
    targetDb = QSqlDatabase.addDatabase("QSPATIALITE")
    targetDb.setDatabaseName(targetDbPath.as_posix())

    if not targetDb.open():
        print("Database Error: {0}".format(targetDb.lastError().text()))
    else:
        q = QSqlQuery(targetDb)

        print(f"Set new APIS DB version: {targetVersion}")
        q.exec_(f"PRAGMA user_version = {targetVersion}")

        # Add Columns
        for tableName in newCols:
            for newCol in newCols[tableName]:
                print("Create new Column:", tableName, newCol)
                q.exec_(f"ALTER TABLE {tableName} ADD COLUMN {newCol['name']} {newCol['type']}")
                # Update Column
                if 'update' in newCol:
                    q.exec_(newCol['update'])

            # to see new cols in QGIS (https://gis.stackexchange.com/questions/85213/added-columns-in-spatialite-wont-appear-in-qgis-attribute-table)(30.05.2021)
            q.exec_(f"SELECT InvalidateLayerStatistics('{tableName}')")
            q.exec_(f"SELECT UpdateLayerStatistics('{tableName}')")

        # Rename Columns
        for tableName in renameCols:
            for old, new in renameCols[tableName].items():
                print("Rename Column:", tableName, old, "to", new)
                q.exec_(f"ALTER TABLE {tableName} RENAME COLUMN {old} TO {new}")

            q.exec_(f"SELECT InvalidateLayerStatistics('{tableName}')")
            q.exec_(f"SELECT UpdateLayerStatistics('{tableName}')")

        # Other Updates

        # Run SQL Updates
        # 1: trim leading and trailing spaces from certain columns in film 
        res = q.exec_("UPDATE film SET militaernummer = trim(militaernummer), militaernummer_alt = trim(militaernummer_alt), flugzeug = trim(flugzeug), fotograf = trim(fotograf), kassettennummer = trim(kassettennummer), auftragsnummer = trim(auftragsnummer)")

        # FS RepImages
        # goes through all FS rep images and takes the first for a FS and writes to db (-> main rep image!; others are then visible in interface but not stored in db!)
        repImageFindspotDir = os.path.normpath(apisSettings.value("APIS/repr_image_fs_dir"))
        repImagesPathList = glob.glob(os.path.normpath(os.path.join(repImageFindspotDir, "*_*_*-FS.jpg")))
        for img in repImagesPathList:
            imgFileName = os.path.splitext(os.path.basename(img))[0]
            splitFileName = imgFileName.split('-')[0].replace('_', '.').split('.', 3)[:3]
            foNumber = '.'.join(splitFileName[:2])
            fsNumber = splitFileName[2]
            print(imgFileName, foNumber, fsNumber)
            res = q.exec_(f'UPDATE fundstelle SET repraesentatives_luftbild = "{imgFileName}" WHERE fundortnummer = "{foNumber}" AND fundstellenummer = "{fsNumber}" AND repraesentatives_luftbild IS NULL')
        targetDb.close()

# Non DB related Tasks


#assign projection to interpretation shape files!
def shapeFileHasCrs(shapeFilePath):
    shpDriver = ogr.GetDriverByName('ESRI Shapefile')
    dataSource = shpDriver.Open(shapeFilePath, 0)
    if dataSource:
        spatialRef = dataSource.GetLayer().GetSpatialRef()
        if spatialRef:
            return True
        else:
            return False
    else:
        return False


# interpretation dir
intBaseDir = apisSettings.value("APIS/int_base_dir")
intDir = apisSettings.value("APIS/int_dir")

shpIntFiles = glob.glob(os.path.normpath(os.path.join(intBaseDir, '*', '* *', intDir, 'luftint*.shp')))
c = 0
for shapeFilePath in shpIntFiles:
    if not shapeFileHasCrs(shapeFilePath):
        print(os.path.basename(shapeFilePath))
        c += 1
        # apply defaultEpsg To Shape file
        # spatialRef = osr.SpatialReference()
        # spatialRef.ImportFromEPSG(defaultEpsg)
        # spatialRef.MorphToESRI()
        # shapePrjFilePath = os.path.splitext(shapeFilePath)[0] + '.prj'
        # file = open(shapePrjFilePath, 'w')
        # file.write(spatialRef.ExportToWkt())
        # file.close()
print("Count", c)

# # Updates 3.1.3 to 3.2.0
# """
# 1) PRAGMA application_id = 116919 (1 16 9 19 for APIS)
# 2) PRAGMA user_version = 320
# //3) We leave that for now! Remove Column: film -> target (How-To remove columns: use DB Browser for SQLite and remove manually! C:\\Program Files\\DB Browser for SQLite)
# 3) create target column in luftbild_schraeg_cp und luftbild_senk_cp
# 4) create rep luftbild in fundstelle und fundstelle_log
# 5) write fs rep luftbild into db if file available
# 6) Non DB related task: assign projection to interpretation files!
# """


# # No CHNAGES BELWOW
# tableNames = ['begehung', 'copyright', 'datierung_quelle', 'film', 'film_fabrikat', 'fundart', 'fundgewinnung', 'fundgewinnung_quelle', 'fundort', 'fundort_log', 'fundstelle', 'fundstelle_log', 'hersteller', 'kamera', 'katastralgemeinden', 'kultur', 'luftbild_schraeg_cp', 'luftbild_schraeg_fp', 'luftbild_senk_cp', 'luftbild_senk_fp', 'osm_boundaries', 'phase', 'projekt', 'target', 'wetter', 'zeit']

# queriesSource = [
#     "PRAGMA application_id = 116199",
#     "PRAGMA user_version = 313"
# ]

# queriesTarget = [
#     "PRAGMA application_id = 116199",
#     "PRAGMA user_version = 320"
# ]

# updtFlrnm = """UPDATE fundstelle
# SET flurname = (SELECT fundort.flurname
#               FROM fundort
#               WHERE TRIM(fundort.flurname) != '' AND fundort.flurname IS NOT NULL AND fundort.ogc_fid IN (SELECT fundort.ogc_fid
#                                                                                             FROM fundort
#                                                                                             WHERE fundstelle.fundortnummer = fundort.fundortnummer AND EQUALS (fundstelle.geometry, fundort.geometry)))"""

# renameCols = {
#     'fundort':
#         {
#             'detailinterpretation': 'sonstiges'
#         },
#     'fundstelle':
#         {
#             'fundart': 'befundart',
#             'fundart_detail': 'befundart_detail',
#             'datierung_zeit': 'datierung_zeitstufe',
#             'fundgeschichte': 'befundgeschichte'
#         },
#     'fundort_log':
#         {
#             'detailinterpretation': 'sonstiges'
#         },
#     'fundstelle_log':
#         {
#             'fundart': 'befundart',
#             'fundart_detail': 'befundart_detail',
#             'datierung_zeit': 'datierung_zeitstufe',
#             'fundgeschichte': 'befundgeschichte'
#         },
#     'fundart':
#         {
#             'fundart': 'befundart',
#             'fundart_detail': 'befundart_detail'
#         }
# }

# newCols = {
#     'fundort':
#         [
#             {'name': 'common_name', 'type': 'TEXT'}
#         ],
#     'fundstelle':
#         [
#             {'name': 'common_name', 'type': 'TEXT'},
#             {'name': 'flurname', 'type': 'TEXT', 'update': updtFlrnm}
#         ],
#     'fundort_log':
#         [
#             {'name': 'common_name', 'type': 'TEXT'}
#         ],
#     'fundstelle_log':
#         [
#             {'name': 'common_name', 'type': 'TEXT'},
#             {'name': 'flurname', 'type': 'TEXT'}
#         ],
#     'luftbild_schraeg_cp':
#         [
#             {'name': 'beschreibung', 'type': 'TEXT', 'update': 'UPDATE luftbild_schraeg_cp SET beschreibung = NULLIF(COALESCE(keyword, "") || CASE LENGTH(COALESCE(keyword, "")) WHEN 0 THEN "" ELSE CASE  LENGTH(COALESCE(description, "")) WHEN 0 THEN "" ELSE "; " END END || COALESCE(description, ""), "")'}
#         ],
#     'luftbild_schraeg_fp':
#         [
#             {'name': 'source', 'type': 'TEXT', 'update': 'UPDATE luftbild_schraeg_fp SET source = CASE WHEN ST_NPoints(geometry) = 5 AND CAST(substr(filmnummer, 3,4) AS INTEGER) >= 2014 THEN "imu" WHEN ST_NPoints(geometry) = 5 AND CAST(substr(filmnummer, 3,4) AS INTEGER) < 2014 THEN "trapez_manuell" ELSE "kreis_semiauto" END, shape_length = round(PERIMETER(geometry, TRUE), 3), shape_area = round(AREA(geometry, TRUE), 3)'}  # kreis_semiauto, imu, trapez_manuell, oriental
#         ],
#     'luftbild_senk_fp':
#         [
#             {'name': 'source', 'type': 'TEXT', 'update': 'UPDATE luftbild_senk_fp SET source = "rechteck_semiauto", shape_length = round(PERIMETER(geometry, TRUE), 3), shape_area = round(AREA(geometry, TRUE), 3)'}  # rechteck_semiauto, vexcel, oriental
#         ]
# }
# # Merge: 1) new col with update 2) remove old cols
# mergeCols = {
#     ''
# }

# updateCols = {
#     'luftbild_schraeg_fp': 'UPDATE luftbild_schraeg_fp SET shape_length = round(PERIMETER(geometry, TRUE), 3), shape_area = round(AREA(geometry, TRUE), 3)',
#     'luftbild_senk_fp': 'UPDATE luftbild_senk_fp SET shape_length = round(PERIMETER(geometry, TRUE), 3), shape_area = round(AREA(geometry, TRUE), 3)',
#     'zeit': 'UPDATE zeit SET zeit = "Rezent", periode = "Rezent", periode_detail = "Rezent" WHERE zeit = "Momentan"',
#     'fundstelle': 'UPDATE fundstelle SET datierung_zeitstufe = "Rezent", datierung_periode = "Rezent", datierung_periode_detail = "Rezent" WHERE datierung_zeitstufe = "Momentan"'
# }

# renameTabs = {
#     'fundart': 'befundart'
# }

# # How-To remove columns: use DB Browser for SQLite and remove manually! C:\Program Files\DB Browser for SQLite
# removeCols = {
#     'luftbild_schraeg_cp':
#         [
#             'keyword',
#             'description'
#         ]
# }

# insertRows = {
#     'fundgewinnung': ['INSERT INTO fundgewinnung (fundgewinnung) VALUES ("Aufsammlung")'],
#     'zeit': ['INSERT INTO zeit (zeit, periode, periode_detail) VALUES ("Frühgeschichte", "Frühgeschichte", "Frühgeschichte")',
#              'INSERT INTO zeit (zeit, periode, periode_detail) VALUES ("Urzeit", "Eisenzeit", "Eisenzeit")']
# }

# deleteRows = {
#     'luftbild_schraeg_cp': ['DELETE FROM luftbild_schraeg_cp WHERE bildnummer IS NULL AND filmnummer = "0119710806" AND bildnummer_nn = 108']  # Dubicate in Database Image 108 exists identical despite bildnummer
# }

# tmpl = """CREATE TABLE {0} (
# ogc_fid INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
# {1},
# UNIQUE({2})
# )"""

# tmplNoUnique = """CREATE TABLE {0} (
# ogc_fid INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
# {1}
# )"""

# sourceDb = QSqlDatabase.addDatabase("QSPATIALITE")
# sourceDb.setDatabaseName(sourceDbPath)

# if not sourceDb.open():
#     print("Database Error: {0}".format(sourceDb.lastError().text()))
#     sys.exit(1)
# else:
#     sourceDb.close()

# targetDb = QSqlDatabase.addDatabase("QSPATIALITE")
# targetDb.setDatabaseName(targetDbPath)

# if not targetDb.open():
#     print("Database Error: {0}".format(targetDb.lastError().text()))
#     sys.exit(1)
# else:
#     q = QSqlQuery(targetDb)
#     q2 = QSqlQuery(targetDb)
#     # if the optional argument transaction is set to TRUE the whole operation will be handled as a single Transaction (faster): the default setting is transaction=FALSE (slower, but safer).
#     q.exec_("SELECT InitSpatialMetaData(1)")

#     q.exec_("ATTACH DATABASE '{}' AS apissource".format(sourceDbPath))

#     q.exec_("SELECT name FROM apissource.sqlite_master WHERE type='table' ORDER BY name;")
#     q.seek(-1)
#     while(q.next()):
#         for i in range(q.record().count()):
#             tableName = str(q.record().value(i))
#             unique = []
#             fields = []
#             if tableName in tableNames:
#                 q2.exec_("PRAGMA table_info({0});".format(tableName))
#                 #print(q2.lastError().text())
#                 q2.seek(-1)
#                 isSpatial = False
#                 geomType = ""
#                 fieldNames = []
#                 while(q2.next()):
#                     fieldName = str(q2.record().value(1))
#                     fieldNames.append(fieldName)
#                     fieldType = str(q2.record().value(2))
#                     fields.append("{0} {1}".format(fieldName, fieldType))
#                     if q2.record().value(5) > 0:
#                         unique.append(fieldName)
#                     if fieldName == 'geometry':
#                         isSpatial = True
#                         geomType = fieldType
#                         #print(tableName)
#                 if unique:
#                     ctQry = tmpl.format(tableName, ",\n".join(fields), ", ".join(unique))
#                 else:
#                     ctQry = tmplNoUnique.format(tableName, ",\n".join(fields))
#                 #print(ctQry)
#                 q2.exec_(ctQry)
#                 q2.exec_("INSERT INTO main.{0}({1}) SELECT {1} FROM apissource.{0}".format(tableName, ", ".join(fieldNames)))
#                 # if spatial
#                 if isSpatial:
#                     q2.exec_("SELECT DISTINCT Srid(geometry) FROM apissource.{0};".format(tableName))
#                     q2.seek(-1)
#                     q2.first()
#                     srid = q2.record().value(0)
#                     q2.exec_("SELECT RecoverGeometryColumn('{0}', 'geometry', {1}, '{2}')".format(tableName, srid, geomType))
#                     q2.exec_("SELECT CreateSpatialIndex('{0}', 'geometry')".format(tableName))

#                 # Rename Columns
#                 if tableName in renameCols:
#                     for old, new in renameCols[tableName].items():
#                         q2.exec_("ALTER TABLE {0} RENAME COLUMN {1} TO {2}".format(tableName, old, new))

#                 # Add Columns
#                 if tableName in newCols:
#                     for nC in newCols[tableName]:
#                         q2.exec_("ALTER TABLE {0} ADD COLUMN {1} {2}".format(tableName, nC['name'], nC['type']))
#                         #Update Columns
#                         if 'update' in nC:
#                             q2.exec_(nC['update'])

#                 # Update Columns
#                 if tableName in updateCols:
#                     q2.exec_(updateCols[tableName])

#                 # Remove Columns
#                 # see comment above

#                 # Insert Rows
#                 if tableName in insertRows:
#                     for insert in insertRows[tableName]:
#                         q2.exec_(insert)

#                 # Delete Rows
#                 if tableName in deleteRows:
#                     for delete in deleteRows[tableName]:
#                         q2.exec_(delete)

#                 # Finally renmae Table
#                 if tableName in renameTabs:
#                     q2.exec_("ALTER TABLE {0} RENAME TO {1}".format(tableName, renameTabs[tableName]))

#     # update radii for NULL schräg Centerpoints

#     q3 = QSqlQuery(targetDb)
#     import xlrd

#     # Give the location of the file
#     loc = ("C:\\data\\development\\apis\\APIS3\\playground\\0-Footprints-Liste_2019-01-11.xlsx")

#     wb = xlrd.open_workbook(loc)
#     sheet = wb.sheet_by_index(0)

#     for i in range(1, sheet.nrows):
#         imageNumber = sheet.cell_value(i, 0)
#         radius = sheet.cell(i, 1).value
#         if radius:
#             print(imageNumber, int(radius))
#             q3.exec_("UPDATE luftbild_schraeg_cp SET radius = '{0}' WHERE bildnummer = '{1}'".format(int(radius), imageNumber))
#         else:
#             radius = "175"
#             q3.exec_("UPDATE luftbild_schraeg_cp SET radius = '{0}' WHERE bildnummer = '{1}'".format(radius, imageNumber))
#         # Update Footprint, length, area
#         # q3.exec_("UPDATE luftbild_schraeg_fp SET geometry = Transform(Buffer(Transform(geometry, 31287), {0}), 4312), source = 'kreis_semiauto' WHERE bildnummer = '{1}'".format(int(radius), imageNumber))
#         # q3.exec_("UPDATE luftbild_schraeg_fp SET geometry = Buffer(geometry, {0}), source = 'kreis_semiauto' WHERE bildnummer = '{1}'".format(int(radius), imageNumber))
#         q3.exec_("UPDATE luftbild_schraeg_fp SET geometry = Transform(Buffer((SELECT Transform(geometry, 31287) FROM luftbild_schraeg_cp WHERE bildnummer = '{1}'), {0}), 4312) WHERE bildnummer = '{1}'".format(int(radius), imageNumber))
#         # "UPDATE luftbild_schraeg_fp SET shape_length = round(PERIMETER(geometry, TRUE), 3), shape_area = round(AREA(geometry, TRUE), 3) WHERE bildnummer = '{1}'".format(imageNumber)

#     # Footprint filmnumber correction
#     filmNumbers = [
#         {'old': '01600001', 'new': '0119600501'},
#         {'old': '01600002', 'new': '0119600401'},
#         {'old': '01600003', 'new': '0119600602'}
#     ]
#     for film in filmNumbers:
#         q3.exec_("UPDATE luftbild_schraeg_fp SET bildnummer = '{1}' || substr(bildnummer, 9, 4), filmnummer = '{1}' WHERE filmnummer = '{0}'".format(film['old'], film['new']))

#     # Centerpoints bildnumber correction
#     imageNumbers = [
#         {'old': '0119650003.001', 'new': '0119650003.007'},
#         {'old': '0119650003.002', 'new': '0119650003.008'}
#     ]
#     for image in imageNumbers:
#         q3.exec_("UPDATE luftbild_schraeg_cp SET bildnummer = '{1}' WHERE bildnummer = '{0}'".format(image['old'], image['new']))
#         q3.exec_("UPDATE luftbild_schraeg_fp SET geometry = Transform(Buffer((SELECT Transform(geometry, 31287) FROM luftbild_schraeg_cp WHERE bildnummer = '{0}'), (SELECT CAST(radius AS INTEGER) FROM luftbild_schraeg_cp WHERE bildnummer = '{0}')), 4312) WHERE bildnummer = '{0}'".format(image['new']))

#     newFootprints = [
#         {'bildnummer': '0119650903.004'},
#         {'bildnummer': '0119650306.014'},
#         {'bildnummer': '0119650306.020'}
#     ]
#     for fp in newFootprints:
#         q3.exec_("INSERT INTO luftbild_schraeg_fp (bildnummer, filmnummer, source) VALUES ('{0}', '{1}', 'kreis_semiauto')".format(fp['bildnummer'], fp['bildnummer'][:10]))
#         q3.exec_("UPDATE luftbild_schraeg_fp SET geometry = Transform(Buffer((SELECT Transform(geometry, 31287) FROM luftbild_schraeg_cp WHERE bildnummer = '{0}'), (SELECT CAST(radius AS INTEGER) FROM luftbild_schraeg_cp WHERE bildnummer = '{0}')), 4312) WHERE bildnummer = '{0}'".format(fp['bildnummer']))

#     # UPDATE NULL shape length and area fields
#     q3.exec_("UPDATE luftbild_schraeg_fp SET shape_length = round(PERIMETER(geometry, TRUE), 3), shape_area = round(AREA(geometry, TRUE), 3) WHERE shape_length IS NULL OR shape_area IS NULL")

#     # q.exec_("CREATE TABLE main.fundort AS SELECT * FROM apissource.fundort")

#     # q.exec_("SELECT sql FROM apissource.sqlite_master WHERE type = 'table' AND name = 'fundort'")
#     # q.seek(-1)
#     # while(q.next()):
#     #     print(str(q.record().value(0)))
#     #     q.exec_(str(q.record().value(0)))

#     # q.exec_("SELECT name, sql FROM apissource.sqlite_master WHERE type = 'index' AND tbl_name = 'fundort'")
#     # q.seek(-1)
#     # while(q.next()):
#     #    print(str(q.record().value(0)), str(q.record().value(1)))

#     # q.exec_("INSERT INTO main.fundort SELECT * FROM apissource.fundort")
#     # q.exec_("CREATE UNIQUE INDEX fundortnummer_unique_index ON fundort(fundortnummer)")
#     # q.exec_("SELECT RecoverGeometryColumn('fundort', 'geometry', 4312, 'POLYGON')")
#     # q.exec_("SELECT CreateSpatialIndex('fundort', 'geometry')")

#     q.exec_("DETACH DATABASE 'apissource'")
#     targetDb.close()
