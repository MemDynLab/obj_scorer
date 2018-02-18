import logging
import os.path

from PyQt5 import QtWidgets, QtCore, QtGui

from score_behavior.trial_dialog_ui import Ui_TrialDialog


class TrialDialog(QtWidgets.QDialog):
    trial_dialog_error_signal = QtCore.pyqtSignal(str, name='TrialDialog.trial_dialog_error_signal')

    def __init__(self, caller=None, trial_params=None, locations=None, object_dir=None, object_list=None):
        super(TrialDialog, self).__init__(flags=QtCore.Qt.WindowFlags())
        self.log = logging.getLogger(__name__)
        self.log.debug('Trial Dialog initializing')
        self.ui = Ui_TrialDialog()
        self.ui.setupUi(self)
        self.ui.objectComboBox.currentIndexChanged.connect(self.update_object_change)
        if caller:
            self.ui.addTrialButton.clicked.connect(caller.add_trial)
            self.ui.skipTrialButton.clicked.connect(caller.skip_trial)

        if locations:
            self.ui.location1ComboBox.addItems(locations)
            self.ui.location2ComboBox.addItems(locations)
            self.locations = locations
        else:
            self.log.error('Locations missing')
            self.trial_dialog_error_signal.emit('Locations missing')
            raise ValueError("missing argument locations")

        if object_list:
            self.obj_idx = object_list

        if object_dir:
            self.obj_dir = object_dir

        str_obj_idxs = [str(i) for i in self.obj_idxs]
        self.ui.objectComboBox.addItems(str_obj_idxs)

        self.set_values(trial_params)
        self.set_image()
        self.setWindowTitle("Next Trial")

    def make_null_image(self):
        pixmap = QtGui.QPixmap(self.ui.objectLabel.size())
        pixmap.fill(QtCore.Qt.black)
        return pixmap

    def set_image(self):
        obj_idx = self.get_current_object()
        pixmap = None
        try:
            # noinspection PyCallByClass,PyTypeChecker,PyArgumentList
            pixmap = QtGui.QPixmap(os.path.join(self.obj_dir, str(obj_idx) + '.JPG'))
            pixmap = pixmap.scaled(self.ui.objectLabel.size(), QtCore.Qt.KeepAspectRatio)
        except ValueError:
            self.log.warning('Object {} not in list!'.format(obj_idx))
            pixmap = self.make_null_image()
        finally:
            self.ui.objectLabel.setPixmap(pixmap)
            return obj_idx

    def set_readonly(self, ro):
        self.ui.sessionLineEdit.setReadOnly(ro)
        self.ui.runLineEdit.setReadOnly(ro)
        self.ui.trialLineEdit.setReadOnly(ro)
        self.ui.subjectLineEdit.setReadOnly(ro)
        self.ui.subjectTrialLineEdit.setReadOnly(ro)
        self.ui.objectComboBox.setEnabled(not ro)
        self.ui.location1ComboBox.setEnabled(not ro)
        self.ui.location2ComboBox.setEnabled(not ro)

    @QtCore.pyqtSlot(int)
    def update_object_change(self, _):
        self.set_image()
        self.update()

    def get_current_object(self):
        return self.obj_idxs[self.ui.objectComboBox.currentIndex()]

    def set_values(self, values):
        print(values['trial'])
        self.ui.sessionLineEdit.setText(str(values['session']))
        self.ui.runLineEdit.setText(str(values['run_nr']))
        self.ui.trialLineEdit.setText(str(values['sequence_nr']))
        self.ui.subjectLineEdit.setText(str(values['subject']))
        self.ui.subjectTrialLineEdit.setText(str(values['trial']))
        self.ui.location1ComboBox.setCurrentIndex(self.locations.index(values['loc_1']))
        self.ui.location2ComboBox.setCurrentIndex(self.locations.index(values['loc_2']))
        self.ui.objectComboBox.setCurrentIndex(self.obj_idxs.index(values['obj']))
        px = self.make_location_map(values)
        self.ui.objLocLabel.setPixmap(px)

    def make_location_map(self, values):
        w = self.ui.objLocLabel
        p = QtGui.QPixmap(w.width(), w.height())
        p.fill(QtCore.Qt.white)
        width = w.width()
        height = w.height()

        sz = min(width, height) * 0.96

        painter = QtGui.QPainter()
        pen = QtGui.QPen()
        pen.setColor(QtCore.Qt.black)
        pen.setWidth(5)
        painter.begin(p)
        painter.setPen(pen)
        painter.drawRect(width * 0.02, height * 0.02, sz, sz)

        obj_rect = {
            'UL': QtCore.QRect(width * 0.1, height * 0.1, sz * 0.2, sz * 0.2),
            'UR': QtCore.QRect(width * 0.7, height * 0.1, sz * 0.2, sz * 0.2),
            'LL': QtCore.QRect(width * 0.1, height * 0.7, sz * 0.2, sz * 0.2),
            'LR': QtCore.QRect(width * 0.7, height * 0.7, sz * 0.2, sz * 0.2)}

        painter.setBrush(QtCore.Qt.black)
        painter.drawEllipse(obj_rect[values['loc_1']])
        painter.drawEllipse(obj_rect[values['loc_2']])
        painter.end()

        return p

    def get_values(self):
        values = {'session': int(self.ui.sessionLineEdit.text()), 'run_nr': int(self.ui.runLineEdit.text()),
                  'sequence_nr': int(self.ui.trialLineEdit.text()), 'subject': int(self.ui.subjectLineEdit.text()),
                  'loc_1': self.locations[self.ui.location1ComboBox.currentIndex()],
                  'loc_2': self.locations[self.ui.location2ComboBox.currentIndex()],
                  'obj': self.obj_idxs[self.ui.objectComboBox.currentIndex()],
                  'trial': int(self.ui.subjectTrialLineEdit.text())}
        return values