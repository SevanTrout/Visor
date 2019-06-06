from random import gauss
from statistics import mean

from PyQt5 import QtWidgets, QtCore, QtSql

from Models.standard import Standard
from Views.ReportWidget import ReportWidget
from connection import create_connection
from views import StandardsTableWidget, CreateBatchDialog, Login, BatchesListWidget


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None, user=None):
        super(MainWindow, self).__init__(parent)

        self.user = user

        self.setWindowTitle("Visor. Сессия пользователя {0}".format(
            user.fullname if user is not None else 'Неизвестный пользователь'))

        bar = self.menuBar()
        conveyor = bar.addMenu("&Конвейер")
        create_batch_action = conveyor.addAction("&Создать партию")
        create_batch_action.triggered.connect(self.create_batch)

        batches_list_action = conveyor.addAction("&Показать партии")
        batches_list_action.triggered.connect(self.create_batches_list)

        if user.is_operator():
            settings = bar.addMenu("&Настройки")

            edit_standards_action = settings.addAction("&Редактировать нормальные показатели")
            edit_standards_action.triggered.connect(self.edit_standards)

        if user.is_admin():
            admin = bar.addMenu("&Администрирование")

            # create_user_action = admin.addAction("&Добавить пользователя")
            # create_user_action.triggered.connect(self.create_user)

        self.progress_bar = QtWidgets.QProgressBar()
        self.statusBar().addPermanentWidget(self.progress_bar)

        self.mdi_area = QtWidgets.QMdiArea()
        self.mdi_area.setViewMode(QtWidgets.QMdiArea.TabbedView)
        self.mdi_area.setTabsMovable(True)
        self.mdi_area.setTabsClosable(True)
        self.setCentralWidget(self.mdi_area)

    def create_batches_list(self):
        batches_title = 'Партии'

        if batches_title not in list(map(lambda x: x.windowTitle(), self.mdi_area.subWindowList())):
            sub2 = QtWidgets.QMdiSubWindow()

            self.batches_list = BatchesListWidget(progress_bar=self.progress_bar, is_admin=self.user.is_admin)
            self.batches_list.show_report_signal.connect(self.show_report)

            sub2.setWidget(self.batches_list)
            sub2.setWindowTitle(batches_title)
            sub2.setAttribute(QtCore.Qt.WA_DeleteOnClose)
            sub2.resize(1024, 600)
            self.mdi_area.addSubWindow(sub2)
            sub2.show()

    def show_report(self, batch_id):
        sub1 = QtWidgets.QMdiSubWindow()

        sub1.setWindowTitle("Отчёт о партии {0}".format(batch_id))
        sub1.setWidget(ReportWidget(batch_id=batch_id))
        sub1.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        sub1.resize(1024, 600)
        self.mdi_area.addSubWindow(sub1)
        sub1.show()

    def create_batch(self):
        create_batch = CreateBatchDialog(user=self.user)
        if create_batch.exec_() == QtWidgets.QDialog.Accepted:
            batch = create_batch.get_batch()

            if self.create_results(batch):
                self.progress_bar.reset()
                QtWidgets.QMessageBox.information(self, "Успех!", "Партия создана успешно")

    def create_results(self, batch):
        standard_query = QtSql.QSqlQuery()

        if not (standard_query.exec_("""SELECT id, min_value, max_value, unit_id FROM Standards""")):
            QtWidgets.QMessageBox.warning(self, 'Ошибка!',
                                          'Произошла неизвестная ошибка, попробуйте снова')
            return False

        standards = []

        result_query = QtSql.QSqlQuery()

        while standard_query.next():
            standards.append(Standard(standard_id=standard_query.value(0),
                                      min_value=standard_query.value(1),
                                      max_value=standard_query.value(2),
                                      unit_id=standard_query.value(3)))

        progress_bar_multiplier = 100 / len(standards)
        batch_size = batch.size
        batch_id = batch.id
        value_separator = ', '

        for index, standard in enumerate(standards):
            result_query_pattern = 'INSERT INTO Results(value, standard_id, unit_id, batch_id) VALUES '

            standard_id = standard.id
            unit_id = standard.unit_id

            results = []

            for i in range(batch_size):
                results.append(
                    '({0}, {1}, {2}, {3})'.format(
                        round(gauss(round(mean([standard.min_value, standard.max_value]), 4),
                                    (standard.max_value - standard.min_value) / 4), 4),
                        standard_id,
                        unit_id,
                        batch_id)
                )

                self.progress_bar.setValue((index + (i / batch_size)) * progress_bar_multiplier)

            result_query_pattern += value_separator.join(results)

            if not (result_query.exec_(result_query_pattern)):
                QtWidgets.QMessageBox.warning(self, 'Ошибка!',
                                              'Произошла неизвестная ошибка, попробуйте снова')
                return False

        return True

    def edit_standards(self):
        edit_standard_title = "Редактировать нормальные показатели"

        if edit_standard_title not in list(map(lambda x: x.windowTitle(), self.mdi_area.subWindowList())):
            sub1 = QtWidgets.QMdiSubWindow()

            sub1.setWindowTitle(edit_standard_title)
            sub1.setWidget(StandardsTableWidget())
            sub1.setAttribute(QtCore.Qt.WA_DeleteOnClose)
            sub1.resize(1024, 600)
            self.mdi_area.addSubWindow(sub1)
            sub1.show()


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
