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
    query.exec_("""CREATE TABLE IF NOT EXISTS person (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, 
                                                     firstname VARCHAR(20), 
                                                    lastname VARCHAR(20))""")
    query.exec_("insert into person values(101, 'Danny', 'Young')")
    query.exec_("insert into person values(102, 'Christine', 'Holand')")
    query.exec_("insert into person values(103, 'Lars', 'Gordon')")
    query.exec_("insert into person values(104, 'Roberto', 'Robitaille')")
    query.exec_("insert into person values(105, 'Maria', 'Papadopoulos')")

    return True
