from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QVBoxLayout, QDialogButtonBox


class AddRowDialog(QtWidgets.QDialog):

    def __init__(self, names, parent=None):
        super(AddRowDialog, self).__init__(parent)

        self.names = names
        self.resize(300, 200)

        self.layout = QVBoxLayout(self)

        self.lines = []
        for name in names:
            label = QtWidgets.QLabel("{0}".format(name))
            line = QtWidgets.QLineEdit()
            self.lines.append(line)
            self.layout.addWidget(label)
            self.layout.addWidget(line)

        self.buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            QtCore.Qt.Horizontal, self)
        self.layout.addWidget(self.buttons)

        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)

    @staticmethod
    def get_row_data(names, parent=None):
        dialog = AddRowDialog(names, parent)
        result = dialog.exec_()
        return list(map(lambda line: line.text(), dialog.lines)), result == QtWidgets.QDialog.Accepted
