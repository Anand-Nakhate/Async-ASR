from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import pyqtSlot


class ModuleSeletorDialog(QtWidgets.QDialog):

    def __init__(self, modules_info, parent=None):
        self.modules_info = modules_info
        super(ModuleSeletorDialog, self).__init__(parent)
        self.setWindowFlags(QtCore.Qt.WindowSystemMenuHint | QtCore.Qt.WindowTitleHint)

        self.title = "ASR - Module Select"
        self.setWindowTitle(self.title)
        self.setModal(True)

        self.verticalLayout = QtWidgets.QVBoxLayout(self)
        self.verticalLayout.setObjectName("verticalLayout")

        self.screen_label = QtWidgets.QLabel("Select the modules:")
        self.verticalLayout.addWidget(self.screen_label)

        self.parent_allmodule_hbox = QtWidgets.QHBoxLayout()
        self.parent_allmodule_hbox.setObjectName('parentlayout')
        self.parent_allmodule_hbox.insertSpacing(0, 40)

        self.allmodule_layout = QtWidgets.QVBoxLayout()
        self.allmodule_layout.insertSpacing(0, 10)
        self.allmodule_layout.setSpacing(6)
        self.allmodule_layout.setObjectName("allmodule_layout")

        self.checkboxes = []
        self.add_module_checkboxes()

        self.parent_allmodule_hbox.addLayout(self.allmodule_layout)
        self.verticalLayout.addLayout(self.parent_allmodule_hbox)

        self.button_layout = QtWidgets.QHBoxLayout()
        self.button_layout.setAlignment(QtCore.Qt.AlignCenter)
        self.button_layout.setObjectName("button_layout")

        self.box = QtWidgets.QDialogButtonBox()
        self.box.addButton("Next", QtWidgets.QDialogButtonBox.AcceptRole)
        self.box.addButton("Cancel", QtWidgets.QDialogButtonBox.RejectRole)

        self.nextButton = QtWidgets.QPushButton('Next')
        self.cancelButton = QtWidgets.QPushButton('Cancel')
        self.button_layout.addWidget(self.nextButton)
        self.button_layout.addWidget(self.cancelButton)

        #
        self.verticalLayout.addLayout(self.button_layout)

        self.nextButton.clicked.connect(self.accept)
        self.cancelButton.clicked.connect(self.reject)

        self.resize(400, 120)


    def add_module_checkboxes(self):
        modules = self.modules_info #modules_info list: [module_names]
        for module in modules:
            self.module_layout1 = QtWidgets.QVBoxLayout()
            self.module_layout1.setObjectName("module_layout1")
            #Check box setup for a device
            self.module_checkbox = QtWidgets.QCheckBox(self)
            self.module_checkbox.setText(module)
            self.module_checkbox.setObjectName("module_checkbox")
            self.module_layout1.addWidget(self.module_checkbox)
            self.allmodule_layout.addLayout(self.module_layout1)
            #self.module_checkbox.stateChanged.connect(self.)
            self.checkboxes.append(self.module_checkbox)