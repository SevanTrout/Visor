from PyQt5 import QtWidgets

from connection import create_connection
from views import PersonWidget


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        self.mdiarea = QtWidgets.QMdiArea()
        self.setCentralWidget(self.mdiarea)

        sub1 = QtWidgets.QMdiSubWindow()
        sub1.setWidget(PersonWidget())
        sub1.resize(800, 600)
        self.mdiarea.addSubWindow(sub1)
        sub1.show()


if __name__ == '__main__':
    import sys

    app = QtWidgets.QApplication(sys.argv)

    if not create_connection():
        sys.exit(-1)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())
