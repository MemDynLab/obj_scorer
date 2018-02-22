from PyQt5 import QtCore
from PyQt5 import QtWidgets
from PyQt5 import QtGui

from .session_manager_control import SessionManagerControlWidget


class SessionController(QtCore.QAbstractTableModel):
    comments_inserted_signal = QtCore.pyqtSignal(str, name="SessionController.comments_inserted_signal")
    def __init__(self, data, parent=None):
        self.columns_to_show = ['subject', 'obj', 'loc_1', 'loc_2']
        super(SessionController, self).__init__(parent=parent)
        self.comments_dialog = None
        self.widget = SessionManagerControlWidget(parent=parent)
        self._data = data[self.columns_to_show]
        self.widget.ui.tableView.setModel(self)
        for i in range(len(self.columns_to_show)):
            self.widget.ui.tableView.setColumnWidth(i, 60)
        for i in range(len(self._data)):
            self.widget.ui.tableView.setRowHeight(i, 20)
        self.widget.ui.tableView.verticalHeader().setVisible(True)
        self.widget.ui.commentButton.clicked.connect(self.get_comments)
        self.current_row = 0

    @QtCore.pyqtSlot()
    def get_comments(self):
        # noinspection PyArgumentList,PyTypeChecker
        comment, ok = QtWidgets.QInputDialog.getMultiLineText(self.parent(), "Insert comments", "Comments")
        # dialog.setInputMode(QtWidgets.QInputDialog.TextInput)
        # dialog.setLabelText("Comments:")
        # dialog.setWindowTitle("Insert Comments")
        # dialog.setOption(QtWidgets.QInputDialog.UsePlainTextEditForTextInput)
        # # noinspection PyUnresolvedReferences
        # dialog.accepted.connect(self.process_comments)
        # self.comments_dialog = dialog
        # dialog.show()
        if ok:
            self.comments_inserted_signal.emit(comment)


    def process_comments(self):
        text = self.comments_dialog.textValue()
        print("window comments: " + text)
        self.comments_received.emit(text)

    def rowCount(self, parent=None):
        return len(self._data.values)

    def columnCount(self, parent=None):
        return self._data.columns.size

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if index.isValid():
            if role == QtCore.Qt.DisplayRole:
                return str(self._data.values[index.row()][index.column()])
            elif role == QtCore.Qt.ForegroundRole:
                if index.row() == self.current_row:
                    return QtGui.QBrush(QtCore.Qt.red)
                else:
                    return QtGui.QBrush(QtCore.Qt.black )

        return None

    # noinspection PyMethodOverriding
    def headerData(self, idx, orientation, role):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return self._data.columns[idx]
        if orientation == QtCore.Qt.Vertical and role == QtCore.Qt.DisplayRole:
            return str(self._data.index[idx])
        return None

    def set_current_row(self, row):
        l = list(self._data.index)
        self.current_row = l.index(row)
        self.scroll_to_row(row)

    def scroll_to_row(self, row):
        self.widget.ui.tableView.scrollTo(self.index(row, 0), self.widget.ui.tableView.PositionAtCenter)
