from PyQt5 import QtWidgets, QtCore

from connection import create_connection
from views import StandardsTableWidget, CreateBatchDialog, Login


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None, user=None):
        super(MainWindow, self).__init__(parent)

        self.standard_edit_is_open = False

        self.user = user

        self.setWindowTitle("Visor. Сессия пользователя {0}".format(
            user.fullname if user is not None else 'Неизвестный пользователь'))

        bar = self.menuBar()
        conveyor = bar.addMenu("&Конвейер")
        create_batch_action = conveyor.addAction("&Создать партию")
        create_batch_action.triggered.connect(self.create_batch)

        load_data_action = conveyor.addAction("&Загрузить данные")
        load_data_action.triggered.connect(self.load_data)

        if user.is_operator():
            settings = bar.addMenu("&Настройки")

            edit_standards_action = settings.addAction("&Редактировать нормальные показатели")
            edit_standards_action.triggered.connect(self.edit_standards)

        if user.is_admin():
            admin = bar.addMenu("&Администрирование")

            create_user_action = admin.addAction("&Добавить пользователя")
            create_user_action.triggered.connect(self.create_user)

        self.mdi_area = QtWidgets.QMdiArea()
        self.mdi_area.setViewMode(QtWidgets.QMdiArea.TabbedView)
        self.mdi_area.setTabsMovable(True)
        self.mdi_area.setTabsClosable(True)
        self.setCentralWidget(self.mdi_area)

    def create_user(self):
        print("User")

    def load_data(self):
        print("Load")

    def create_batch(self):
        create_batch = CreateBatchDialog(user=self.user)
        if create_batch.exec_() == QtWidgets.QDialog.Accepted:
            QtWidgets.QMessageBox.information(self, "Успех!", "Партия создана успешно")

    def edit_standards(self):

        if not self.standard_edit_is_open:
            sub1 = QtWidgets.QMdiSubWindow()

            sub1.setWindowTitle("Редактировать нормальные показатели")
            sub1.setWidget(StandardsTableWidget())
            sub1.setAttribute(QtCore.Qt.WA_DeleteOnClose)
            sub1.resize(1024, 600)
            self.mdi_area.addSubWindow(sub1)
            sub1.show()

            self.standard_edit_is_open = True


if __name__ == '__main__':
    import sys

    app = QtWidgets.QApplication(sys.argv)
    if not create_connection():
        sys.exit(-1)

    login_window = Login()

    if login_window.exec_() == QtWidgets.QDialog.Accepted:
        w = MainWindow(user=login_window.user)
        w.show()
        sys.exit(app.exec_())
