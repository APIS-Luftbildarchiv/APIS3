from qgis.PyQt.QtSql import QSqlDatabase, QSqlQuery

db = QSqlDatabase.addDatabase('QSPATIALITE')#('QSQLITE')#
db.setDatabaseName("C:\\data\\development\\apis\\APIS2\\gdb2spl\\spatialite\\APIS_20160717_231157.sqlite")
print(db.isValid(), QSqlDatabase.isDriverAvailable('QSPATIALITE')) #returns both True, if query below is commented out

if not db.open():
    print("DB not open")
else:
    print("DB open")
    q = QSqlQuery(db)
    q.exec_("SELECT sqlite_version(), spatialite_version()")
    q.first()
    print(str(q.value(0)), str(q.value(1)))
    
    print(db.tables())
    
    db.close()