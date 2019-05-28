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
                   password TEXT NOT NULL,
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

    query.exec_("""CREATE TABLE IF NOT EXISTS Defects(
                   id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                   name TEXT NOT NULL UNIQUE)""")

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
                   value DOUBLE NOT NULL,
                   unit_id INTEGER NOT NULL,
                   FOREIGN KEY (unit_id) REFERENCES Units (id))""")

    query.exec_("""CREATE TABLE IF NOT EXISTS Results(
                   id INTEGER PRIMARY KEY AUTOINCREMENT NOT NUll,
                   value DOUBLE NOT NULL,
                   is_defect BOOLEAN,
                   defect_value DOUBLE,
                   defect_id INTEGER,
                   standart_id INTEGER NOT NULL,
                   batch_id INTEGER NOT NULL,
                   FOREIGN KEY (defect_id) REFERENCES Defects (id),
                   FOREIGN KEY (standart_id) REFERENCES Standarts (id),
                   FOREIGN KEY (batch_id) REFERENCES Batches (id))""")

    query.exec_("""INSERT INTO Roles(id,name) 
                   SELECT 1, 'Admin' 
                   WHERE NOT EXISTS(SELECT 1 FROM Roles WHERE id = 1 AND name = 'Admin')""")

    query.exec_("""INSERT INTO Users(id,fullname,login,password,role_id) 
                   SELECT 1, 'Admin', 'admin', 'admin', 1 
                   WHERE NOT EXISTS(SELECT 1 FROM Users WHERE id = 1 AND login = 'admin')""")

    return True
