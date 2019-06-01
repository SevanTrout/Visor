from PyQt5 import QtWidgets, QtSql


def create_connection():
    db = QtSql.QSqlDatabase.addDatabase("QSQLITE")
    db.setDatabaseName("test.db")
    if not db.open():
        QtWidgets.QMessageBox.critical(None, "Cannot open database",
                                       "Unable to establish a database connection.\n"
                                       "This example needs SQLite support. Please read "
                                       "the Qt SQL driver documentation for information how "
                                       "to build it.\n\n"
                                       "Click Cancel to exit.", QtWidgets.QMessageBox.Cancel)
        return False

    query = QtSql.QSqlQuery()

    query.exec_("""CREATE TABLE IF NOT EXISTS Roles(
                   id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                   name TEXT NOT NULL UNIQUE)""")

    query.exec_("""CREATE TABLE IF NOT EXISTS Users(
                   id BLOB PRIMARY KEY NOT NULL,
                   fullname TEXT NOT NULL,
                   login TEXT NOT NULL UNIQUE,
                   password_hash TEXT NOT NULL,
                   role_id INTEGER NOT NULL,
                   FOREIGN KEY (role_id) REFERENCES Roles (id))""")

    query.exec_("""CREATE TABLE IF NOT EXISTS Logs(
                   id BLOB PRIMARY KEY NOT NULL,
                   created_at DATETIME NOT NULL,
                   type INTEGER NOT NULL,
                   user_id BLOB NOT NULL,
                   FOREIGN KEY (user_id) REFERENCES Users (id))""")

    query.exec_("""CREATE TABLE IF NOT EXISTS Units(
                   id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                   name TEXT NOT NULL,
                   short_name TEXT NOT NULL)""")

    query.exec_("""CREATE TABLE IF NOT EXISTS Batches(
                   id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                   created_at DATETIME NOT NULL,
                   size INTEGER NOT NULL,
                   is_checked BOOLEAN NOT NULL,
                   user_id BLOB NOT NULL,
                   FOREIGN KEY (user_id) REFERENCES Users (id))""")

    query.exec_("""CREATE TABLE IF NOT EXISTS Standarts(
                   id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                   name TEXT NOT NULL UNIQUE,
                   min_value DOUBLE NOT NULL,
                   max_value DOUBLE NOT NULL,
                   unit_id INTEGER NOT NULL,
                   FOREIGN KEY (unit_id) REFERENCES Units (id))""")

    query.exec_("""CREATE TABLE IF NOT EXISTS Results(
                   id INTEGER PRIMARY KEY AUTOINCREMENT NOT NUll,
                   value DOUBLE NOT NULL,
                   standart_id INTEGER NOT NULL,
                   batch_id INTEGER NOT NULL,
                   unit_id INTEGER NOT NULL,
                   FOREIGN KEY (standart_id) REFERENCES Standarts (id),
                   FOREIGN KEY (batch_id) REFERENCES Batches (id))""")

    query.exec_("""CREATE TABLE IF NOT EXISTS Recommendations(
                   id INTEGER PRIMARY KEY AUTOINCREMENT NOT NUll,
                   description TEXT NOT NULL )
                   """)

    query.exec_("""CREATE TABLE IF NOT EXISTS Reports(
                       id INTEGER PRIMARY KEY AUTOINCREMENT NOT NUll,
                       result TEXT NOT NULL,
                       batch_id INTEGER NOT NULL,
                       FOREIGN KEY (batch_id) REFERENCES Batches (id))""")

    query.exec_("""CREATE TABLE IF NOT EXISTS ReportsToRecommendations(
                       recommendation_id INTEGER NOT NUll,
                       report_id INTEGER NOT NUll,
                       FOREIGN KEY (recommendation_id) REFERENCES Recommendations (id),
                       FOREIGN KEY (report_id) REFERENCES Reports (id))""")

    query.exec_("""INSERT INTO Roles(id,name) 
                   SELECT 1, 'Администратор' 
                   WHERE NOT EXISTS(SELECT 1 FROM Roles WHERE id = 1 AND name = 'Администратор')""")

    query.exec_("""INSERT INTO Users(id,fullname,login,password_hash,role_id) 
                   SELECT 1, 'Admin', 'admin', '21232f297a57a5a743894a0e4a801fc3', 1 
                   WHERE NOT EXISTS(SELECT 1 FROM Users WHERE id = 1 AND login = 'admin')""")

    query.exec_("""INSERT INTO Units(id, name, short_name)
                   SELECT 1, 'миллиметр', 'мм'
                   WHERE NOT EXISTS(SELECT 1 FROM Units WHERE id = 1)""")

    return True
