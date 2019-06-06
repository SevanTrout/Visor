import datetime

from PyQt5 import QtWidgets, QtSql
from PyQt5.QtWidgets import QLabel, QFormLayout, QGroupBox

from Models.batch import Batch


class CreateBatchDialog(QtWidgets.QDialog):
    def __init__(self, parent=None, user=None):
        self.user = user
        self.batch = None

        super(CreateBatchDialog, self).__init__(parent)

        self.resize(600, 400)

        self.setWindowTitle("Создание партии")

        self.formGroupBox = QGroupBox()
        form_layout = QFormLayout()

        self.size = QtWidgets.QSpinBox(self)
        self.size.setRange(1, 80)
        self.size.setValue(80)
        form_layout.addRow(QLabel("Размер партии:"), self.size)

        self.formGroupBox.setLayout(form_layout)

        self.createBatchButton = QtWidgets.QPushButton('Создать', self)
        self.createBatchButton.clicked.connect(self.create_batch)

        main_layout = QtWidgets.QVBoxLayout(self)

        main_layout.addWidget(self.formGroupBox)
        main_layout.addWidget(self.createBatchButton)

        self.setLayout(main_layout)

    def create_batch(self):

        try:
            size = int(self.size.text())

            if size < 1 or size > 80:
                raise ValueError()

        except ValueError:
            QtWidgets.QMessageBox.warning(self, 'Внимание!',
                                          'Указано недопустимое значение параметра "Рамер партии"!')

        self.batch: Batch = Batch(user_id=self.user.id, size=size, created_at=datetime.datetime.utcnow(),
                                  is_checked=False)
        query = QtSql.QSqlQuery()
        query.prepare("""INSERT INTO Batches(size, user_id, created_at, is_checked)
                            VALUES(:size, :user_id, :created_at, :is_checked)""")
        query.bindValue(":size", self.batch.size)
        query.bindValue(":user_id", self.batch.user_id)
        query.bindValue(":created_at", self.batch.iso_created_at)
        query.bindValue(":is_checked", self.batch.is_checked)

        if not query.exec_():
            print("Error")

        query.exec_("""SELECT max(id) FROM Batches""")
        if query.isActive():
            query.first()
            self.batch.id = query.value(0)

        self.accept()

    def get_batch(self):
        return self.batch
