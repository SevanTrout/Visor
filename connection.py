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

    query.exec_("""CREATE TABLE IF NOT EXISTS  items (id INT primary key, 
                                       imagefile INT,
                                       itemtype varchar(20),
                                       description varchar(100))""");
    query.exec_("insert into items "
                "values(0, 0, 'Qt',"
                "'Qt is a full development framework with tools designed to "
                "streamline the creation of stunning applications and  "
                "amazing user interfaces for desktop, embedded and mobile "
                "platforms.')");
    query.exec_("insert into items "
                "values(1, 1, 'Qt Quick',"
                "'Qt Quick is a collection of techniques designed to help "
                "developers create intuitive, modern-looking, and fluid "
                "user interfaces using a CSS & JavaScript like language.')");
    query.exec_("insert into items "
                "values(2, 2, 'Qt Creator',"
                "'Qt Creator is a powerful cross-platform integrated "
                "development environment (IDE), including UI design tools "
                "and on-device debugging.')");
    query.exec_("insert into items "
                "values(3, 3, 'Qt Project',"
                "'The Qt Project governs the open source development of Qt, "
                "allowing anyone wanting to contribute to join the effort "
                "through a meritocratic structure of approvers and "
                "maintainers.')");
    return True
