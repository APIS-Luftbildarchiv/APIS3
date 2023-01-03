# update and run apis_post_install_qgis3_osgeo4w.cmd
# pip install pandas

import pathlib
import shutil
import pandas as pd
import datetime
from PyQt5.QtCore import QDateTime, QSettings, QDate
from PyQt5.QtSql import QSqlDatabase, QSqlQuery

# from osgeo import ogr
# from osgeo.gdalconst import GA_Update


def validateFilmNumberFormat(film_text, hersteller):
    try:
        # print("hersteller", film_text[:2])
        if int(film_text[8:]) < 1 or int(film_text[8:]) > 99:
            raise ValueError()
        if film_text[:2] not in hersteller:
            raise ValueError()
        datetime.datetime.strptime(film_text[2:8], '%Y%m')
        return False
    except ValueError:
        return True
        # raise ValueError("Incorrect data format, should be YYYY-MM-DD")


def validateDateFormat(date_text):
    try:
        datetime.datetime.strptime(date_text, '%Y-%m-%d')
        return False
    except ValueError:
        return True
        # raise ValueError("Incorrect data format, should be YYYY-MM-DD")


def IdToIdLegacy(id):
    millennium = ""
    if id[2:4] == "19":
        millennium = "01"
    elif id[2:4] == "20":
        millennium = "02"
    return f"{millennium}{id[4:]}"


apisAppId = 116919  # 1=A 16=P 9=I 19=S
apisSettings = QSettings(QSettings().value("APIS/config_ini"), QSettings.IniFormat)
sourceDbPath = pathlib.Path(apisSettings.value("APIS/database_file"))
sourceDb = QSqlDatabase.addDatabase("QSPATIALITE")
sourceDb.setDatabaseName(sourceDbPath.as_posix())
print("START-----------------------------------------")
# CHECK source DB
checks = True
if not sourceDb.open():
    print("Database Error: {0}".format(sourceDb.lastError().text()))
    checks = False
else:
    q = QSqlQuery(sourceDb)
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
        sourceVersion = int(q.record().value(0))
    if sourceVersion == 0:
        print(f"The source DB appears not have a APIS DB version associated (found: {sourceVersion}).")
        checks = False

    # Load Excel Sheet
    pathUpdateList = 'C:\\data\\development\\apis\\APIS3\\update_apis_db\\update_flight_date_and_film_number.xlsx'

    with pd.ExcelFile(pathUpdateList) as xlsx:
        df = pd.read_excel(xlsx, "UpdateList", index_col=None, usecols="A:C", converters={'FilmnummerAlt': str, 'FilmnummerNeu': str, 'FlugdatumNeu': str})

        # Check if FilmNumbers follow Filmnumber Pattern HH YYYY MM NN, Check if Date follows YYYY-MM-DD pattern
        q.exec_("SELECT id, kurz FROM hersteller")
        q.seek(-1)
        hersteller = {}
        while(q.next()):
            hersteller[str(q.record().value(0))] = str(q.record().value(1))

        df['invalidFilmNumberFormat'] = df.apply(lambda row: validateFilmNumberFormat(row['FilmnummerNeu'], hersteller), axis=1)
        if df['invalidFilmNumberFormat'].any():
            print("----------------------------------------------")
            print("The following rows have an incorrect film number format (FilmnummerNeu). It should be HHYYYYMMNN.")
            print(df[df['invalidFilmNumberFormat']])
            checks = False
        df.drop(columns=['invalidFilmNumberFormat'], inplace=True)

        df['invalidDateFormat'] = df.apply(lambda row: validateDateFormat(row['FlugdatumNeu']), axis=1)
        if df['invalidDateFormat'].any():
            print("----------------------------------------------")
            print("The following rows have an incorrect date format. It should be YYYY-MM-DD.")
            print(df[df['invalidDateFormat']])
            checks = False
        df.drop(columns=['invalidDateFormat'], inplace=True)

        # Check if there is a duplicate in FilmNumber Old and New
        if df.duplicated(subset=['FilmnummerAlt']).any():
            print("----------------------------------------------")
            print("The following rows have an identical FilmnummerAlt. Please clean up the data set. Only one entry allowed.")
            print(df[df.duplicated(['FilmnummerAlt'], keep=False)])
            checks = False

        if df.duplicated(subset=['FilmnummerNeu']).any():
            print("----------------------------------------------")
            print("The following rows have an identical FilmnummerNeu. Please clean up the data set. Only one entry allowed.")
            print(df[df.duplicated(['FilmnummerNeu'], keep=False)])
            checks = False

        # For each row check if new Date is plausible for new FilmNumber (Date -> YYYY, Date-> MM => hhYYYYMMnn ?) (if not -> checks=False; info: row x date and filmnumber do not match)
        df['invalidDate'] = df.apply(lambda row: True if row['FilmnummerNeu'][2:6] != row['FlugdatumNeu'][:4] or row['FilmnummerNeu'][6:8] != row['FlugdatumNeu'][5:7] else False, axis=1)
        if df['invalidDate'].any():
            print("----------------------------------------------")
            print("The following rows have conflicting FilmnummerNeu and FlugdaumNeu (year and/or month). Please clean up the data set. YYYYMM and YYYY-MM have to match.")
            print(df[df['invalidDate']])
            checks = False
        df.drop(columns=['invalidDate'], inplace=True)
        if checks:
            # For each row check if old FilmNumber is in sourceDB (if not -> checks False; info: entry row x old FilmNumber not in DB)
            q = QSqlQuery(sourceDb)
            oldFilmNumbers = df['FilmnummerAlt'].tolist()
            fNString = ", ".join(["\'{}\'".format(fN) for fN in oldFilmNumbers])
            qStr = f"""
                SELECT filmnummer
                FROM film
                WHERE filmnummer IN ({fNString})
            """
            q.exec_(qStr)
            fNs = []
            while q.next():
                fNs.append(q.value(0))
            notInDb = list(set(oldFilmNumbers).difference(set(fNs)))
            if notInDb:
                print("----------------------------------------------")
                print("The following rows have a FilmnummerAlt that is not in the APIS DB. Please check the data set. The film has to exist in the Database.")
                print(df[df['FilmnummerAlt'].isin(notInDb)])
                checks = False

            # For each row check if new FilmnNumber not in sourceDB (if -> checks = False; info new Filmnumber is in DB )
            newFilmNumbers = df['FilmnummerNeu'].tolist()
            fNString = ", ".join(["\'{}\'".format(fN) for fN in newFilmNumbers])
            qStr = f"""
                SELECT filmnummer
                FROM film
                WHERE filmnummer IN ({fNString})
            """
            q.exec_(qStr)
            fNs = []
            while q.next():
                fNs.append(q.value(0))
            if fNs:
                dfSel = df[df['FilmnummerNeu'].isin(fNs) & (df['FilmnummerNeu'] != df['FilmnummerAlt'])]
                if not dfSel.empty:
                    print("----------------------------------------------")
                    print("The following rows have a FilmnummerNeu that already exist in the APIS DB and is different to FilmnummerAlt. Please check the data set. The film cannot exist in the database except FilmnummerAlt = FilmnummerNeu")
                    print(dfSel)
                    checks = False
            sourceDb.close()

            if checks:
                targetDbPath = pathlib.Path(f'C:\\data\\development\\apis\\APIS3\\playground\\APISv{sourceVersion}_{QDateTime.currentDateTime().toString("yyyyMMdd_hhmmss")}.sqlite')

                print(f"Create copy of APIS DB v{sourceVersion}:", sourceDbPath)
                print(f"Save copy of APIS DB v{sourceVersion}:", targetDbPath)
                print("----------------------------------------------")
                shutil.copy(sourceDbPath, targetDbPath)

                # Open New DB
                targetDb = QSqlDatabase.addDatabase("QSPATIALITE")
                targetDb.setDatabaseName(targetDbPath.as_posix())

                if not targetDb.open():
                    print("Database Error: {0}".format(targetDb.lastError().text()))
                else:
                    q = QSqlQuery(targetDb)
                    now = QDate.currentDate()
                    chagnedFilmNumbers = []
                    # Row by Row
                    # print(df)
                    for index, row in df.iterrows():
                        # IS FILM OBLIQUE OR VERTICAL (GET FROM Film Tabelle) => setTableName
                        qStr = f"""
                            SELECT weise, flugdatum, kommentar
                            FROM film
                            WHERE filmnummer = \'{row['FilmnummerAlt']}\'
                        """
                        q.exec_(qStr)
                        q.first()
                        orientation = str(q.value(0))
                        flightDate = str(q.value(1))
                        comment = str(q.value(2))

                        # =============
                        # Update film

                        # filmnummer
                        # filmnummer_legacy
                        # filmnummer_hh_jjjj_mm
                        # filmnummer_nn

                        # if hh is different update hersteller > get list from tabelle hersteller

                        # datum_aenderung (YYYY-MM-DD) nows
                        # flugdatum (YYYY-MM-DD)

                        #Kommentar zur Änderung + Flugdatum

                        if comment and comment != "NULL":
                            # comment = comment.replace('"', '""').replace('\'', '\'\'')
                            comment += "\n"
                        else:
                            comment = ""

                        if orientation not in ["schräg", "senk."]:
                            print(f"Row {index}: The orientation of the film {row['FilmnummerAlt']} is not correct ({orientation}, expected: schräg or senkrecht). Row skipped.")
                            continue
                        # print(flightDate, type(flightDate))
                        if row['FilmnummerAlt'] == row['FilmnummerNeu'] and row['FlugdatumNeu'] == flightDate:
                            print(f"Row {index}: Neither FlightNumber ({row['FilmnummerAlt']}) nor FlightDate ({flightDate}) are different to existing data. Row skipped.")
                            continue

                        setUpdateList = []

                        # film number
                        if row['FilmnummerAlt'] != row['FilmnummerNeu']:
                            chagnedFilmNumbers.append({'old': row['FilmnummerAlt'], 'new': row['FilmnummerNeu']})
                            setUpdateList.append(f"filmnummer = \'{row['FilmnummerNeu']}\'")
                            setUpdateList.append(f"filmnummer_legacy = \'{IdToIdLegacy(row['FilmnummerNeu'])}\'")
                            if row['FilmnummerAlt'][:8] != row['FilmnummerNeu'][:8]:
                                setUpdateList.append(f"filmnummer_hh_jjjj_mm = \'{row['FilmnummerNeu'][:8]}\'")
                            if row['FilmnummerAlt'][8:] != row['FilmnummerNeu'][8:]:
                                setUpdateList.append(f"filmnummer_nn = {int(row['FilmnummerNeu'][8:])}")
                            if row['FilmnummerNeu'][:2] != row['FilmnummerAlt'][:2]:
                                setUpdateList.append(f"hersteller = \'{hersteller[row['FilmnummerAlt'][:2]]}\'")
                            comment += f"Achtung! Die Filmnummer wurde am {now.toString('yyyy-MM-dd')} geändert ({row['FilmnummerAlt']} > {row['FilmnummerNeu']}). Dateinamen der Bilder, Flugwege, etc. sind ggf. manuell umzubenennen."

                        #date
                        if row['FlugdatumNeu'] != flightDate:
                            setUpdateList.append(f"flugdatum = \'{row['FlugdatumNeu']}\'")

                        setUpdateList.append(f"datum_aenderung = \'{now.toString('yyyy-MM-dd')}\'")
                        setUpdateList.append(f"kommentar = \'{comment}\'")

                        qStr = f"""UPDATE film
                                SET {', '.join(setUpdateList)}
                                WHERE filmnummer = \'{row['FilmnummerAlt']}\'
                                """
                        if not q.exec_(qStr):
                            print(q.lastError())

                        # =============
                        # Update fundort
                        # filmnummer_projekt
                        # datum_aenderung (YYYY-MM-DD) now
                        if row['FilmnummerAlt'] != row['FilmnummerNeu']:

                            setUpdateList = []

                            setUpdateList.append(f"filmnummer_projekt = \'{row['FilmnummerNeu']}\'")
                            setUpdateList.append(f"datum_aenderung = \'{now.toString('yyyy-MM-dd')}\'")

                            qStr = f"""UPDATE fundort
                                    SET {', '.join(setUpdateList)}
                                    WHERE filmnummer_projekt = \'{row['FilmnummerAlt']}\'
                                    """
                            if not q.exec_(qStr):
                                print(q.lastError())

                        # =============
                        # Update luftbild_schraeg_cp
                        # datum_aenderung (YYYY-MM-DD) now
                        # bildnummer
                        # filmnummer
                        # filmnummer_hh_jjjj_mm
                        # filmnummer_nn

                        # =============
                        # Update luftbild_senk_cp
                        # datum_aenderung (YYYY-MM-DD) now
                        # bildnummer
                        # filmnummer
                        # filmnummer_hh_jjjj_mm
                        # filmnummer_nn

                        if row['FilmnummerAlt'] != row['FilmnummerNeu']:

                            setUpdateList = []

                            setUpdateList.append(f"bildnummer = \'{row['FilmnummerNeu']}\' || substr( bildnummer, 11, 4 )")
                            setUpdateList.append(f"filmnummer = \'{row['FilmnummerNeu']}\'")
                            if row['FilmnummerAlt'][:8] != row['FilmnummerNeu'][:8]:
                                setUpdateList.append(f"filmnummer_hh_jjjj_mm = \'{row['FilmnummerNeu'][:8]}\'")
                            if row['FilmnummerAlt'][8:] != row['FilmnummerNeu'][8:]:
                                setUpdateList.append(f"filmnummer_nn = {int(row['FilmnummerNeu'][8:])}")

                            setUpdateList.append(f"datum_aenderung = \'{now.toString('yyyy-MM-dd')}\'")

                            qStr = f"""UPDATE luftbild_{'schraeg' if orientation == "schräg" else 'senk'}_cp
                                    SET {', '.join(setUpdateList)}
                                    WHERE filmnummer = \'{row['FilmnummerAlt']}\'
                                    """
                            if not q.exec_(qStr):
                                print(q.lastError())

                        # =============
                        # Update luftbild_schraeg_fp
                        # bildnummer
                        # filmnummer

                        # =============
                        # Update luftbild_senk_fp
                        # bildnummer
                        # filmnummer

                        if row['FilmnummerAlt'] != row['FilmnummerNeu']:
                            setUpdateList = []

                            setUpdateList.append(f"bildnummer = \'{row['FilmnummerNeu']}\' || substr( bildnummer, 11, 4 )")
                            setUpdateList.append(f"filmnummer = \'{row['FilmnummerNeu']}\'")

                            qStr = f"""UPDATE luftbild_{'schraeg' if orientation == "schräg" else 'senk'}_fp
                                    SET {', '.join(setUpdateList)}
                                    WHERE filmnummer = \'{row['FilmnummerAlt']}\'
                                    """
                            if not q.exec_(qStr):
                                print(q.lastError())

                    targetDb.close()
                    # if all went well delete image registry from plugin dir
                    # Warning about Files to be renamed!!
                    # Flugwege
                    # Luftbild
                    if chagnedFilmNumbers:
                        print("----------------------------------------------")
                        print("IMPORTANT: The film number changed for the following films:")
                        for cFN in chagnedFilmNumbers:
                            print(f"{cFN['old']} > {cFN['new']}")
                        print("It is important to rename flightpath files, image files, etc. accordingly. Otherwise APIS cannot find them.")
                        print("The APIS ImageRegistry file might be outdated. Please refresh the Image Registry in the Settings Dialog after updating the filenames.")
                    # if all went well delete image registry from plugin dir
                    # if os.path.isfile(os.path.normpath(os.path.join(QSettings().value("APIS/plugin_dir"), "apis_image_registry.json"))):
                        # os.remove(os.path.normpath(os.path.join(QSettings().value("APIS/plugin_dir"), "apis_image_registry.json")))
print("-------------------------------------------END")
