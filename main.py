from PyQt5 import QtWidgets

from SQLTest.connection import createConnection
from SQLTest.views import PersonWidget, ItemsWidget, NewTableWidget


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
        #
        # sub2 = QtWidgets.QMdiSubWindow()
        # sub2.setWidget(ItemsWidget())
        # self.mdiarea.addSubWindow(sub2)
        # sub2.show()

        # sub3 = QtWidgets.QMdiSubWindow()
        # sub3.setWidget(NewTableWidget())
        # self.mdiarea.addSubWindow(sub3)
        # sub3.show()


if __name__ == '__main__':
    import sys

    app = QtWidgets.QApplication(sys.argv)

    if not createConnection():
        sys.exit(-1)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())
