from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QBrush, QColor
from .customtreeitem import CustomTreeWidgetItem


class Ui_manage_speakers_top_layout(QtWidgets.QDialog):
    def __init__(self, speaker_tree, conversation_table, customsignal, icons, colors, *args, **kwargs):
        super(Ui_manage_speakers_top_layout, self).__init__(*args, **kwargs)
        self.conversation_table = conversation_table
        self.customsignal = customsignal
        self.speaker_tree = speaker_tree
        self.icons = icons
        self.colors = colors
        self.setObjectName("manage_speakers_top_layout")
        self.resize(556, 470)

        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self)
        self.verticalLayout_4.setSpacing(6)
        self.verticalLayout_4.setObjectName("verticalLayout_4")

        self.dialog_label = QtWidgets.QLabel(self)
        self.dialog_label.setObjectName("dialog_label")
        self.verticalLayout_4.addWidget(
            self.dialog_label, 0, QtCore.Qt.AlignHCenter)

        self.manage_speakers_hbox = QtWidgets.QHBoxLayout()
        self.manage_speakers_hbox.setObjectName("manage_speakers_hbox")
        self.manage_speaker_tree = QtWidgets.QTreeWidget(self)
        self.manage_speaker_tree.setObjectName("manage_speaker_tree")
        self.manage_speakers_hbox.addWidget(self.manage_speaker_tree)

        self.buttons_layout = QtWidgets.QVBoxLayout()
        self.buttons_layout.setSpacing(36)
        self.buttons_layout.setObjectName("buttons_layout")

        self.assign_button = QtWidgets.QPushButton(self)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.assign_button.sizePolicy().hasHeightForWidth())
        self.assign_button.setSizePolicy(sizePolicy)
        self.assign_button.setObjectName("assign_button")
        self.buttons_layout.addWidget(
            self.assign_button, 0, QtCore.Qt.AlignTop)

        self.add_button = QtWidgets.QPushButton(self)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.add_button.sizePolicy().hasHeightForWidth())
        self.add_button.setSizePolicy(sizePolicy)
        self.add_button.setObjectName("add_button")
        self.buttons_layout.addWidget(self.add_button, 0, QtCore.Qt.AlignTop)

        self.delete_button = QtWidgets.QPushButton(self)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.delete_button.sizePolicy().hasHeightForWidth())
        self.delete_button.setSizePolicy(sizePolicy)
        self.delete_button.setObjectName("delete_button")
        self.buttons_layout.addWidget(
            self.delete_button, 0, QtCore.Qt.AlignTop)

        self.close_button = QtWidgets.QPushButton(self)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(
            self.close_button.sizePolicy().hasHeightForWidth())
        self.close_button.setSizePolicy(sizePolicy)
        self.close_button.setObjectName("close_button")
        self.buttons_layout.addWidget(
            self.close_button, 0, QtCore.Qt.AlignTop)

        self.manage_speakers_hbox.addLayout(self.buttons_layout)
        self.verticalLayout_4.addLayout(self.manage_speakers_hbox)
        self.verticalLayout_4.setStretch(1, 1)

        self.retranslateUi()
        QtCore.QMetaObject.connectSlotsByName(self)

        self.delete_button.setEnabled(False)

        self.add_button.clicked.connect(self.add_button_handler)
        self.delete_button.clicked.connect(self.delete_button_handler)
        self.manage_speaker_tree.itemClicked.connect(self.handle_itemclick)
        self.assign_button.clicked.connect(self.handle_assign)
        self.close_button.clicked.connect(self.reject)

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("manage_speakers_top_layout", "Form"))
        self.dialog_label.setText(_translate(
            "manage_speakers_top_layout", "Manage Speakers"))
        self.manage_speaker_tree.headerItem().setText(
            0, _translate("manage_speakers_top_layout", "Speakers"))
        __sortingEnabled = self.manage_speaker_tree.isSortingEnabled()
        self.manage_speaker_tree.setSortingEnabled(False)
        self.manage_speaker_tree.setSortingEnabled(__sortingEnabled)
        self.assign_button.setText(_translate(
            "manage_speakers_top_layout", "Assign"))
        self.add_button.setText(_translate(
            "manage_speakers_top_layout", "Add"))
        self.delete_button.setText(_translate(
            "manage_speakers_top_layout", "Delete"))
        self.close_button.setText(_translate(
            "manage_speakers_top_layout", "Close"))
        self.restore_legend()

    def restore_legend(self):
        for index in range(self.speaker_tree.topLevelItemCount()):
            top_level_item = self.speaker_tree.topLevelItem(index)
            name = top_level_item.text(1)
            icon = top_level_item.icon(1)
            bg = top_level_item.background(1)
            item_0 = CustomTreeWidgetItem(
                self.manage_speaker_tree, customsignal=self.customsignal)
            item_0.setFlags(item_0.flags() | QtCore.Qt.ItemIsEditable)
            item_0.setText(0, name)
            item_0.setIcon(0, icon)
            item_0.setBackground(0, bg)

    def add_button_handler(self):
        item_0 = CustomTreeWidgetItem(
            self.manage_speaker_tree, customsignal=self.customsignal, ref="popup")
        item_0.setFlags(item_0.flags() | QtCore.Qt.ItemIsEditable)
        item_0.setText(0, "Please enter a speaker name")
        item_0.setIcon(
            0, self.icons[self.manage_speaker_tree.topLevelItemCount()-1])
        color = self.colors[self.manage_speaker_tree.topLevelItemCount()-1]
        item_0.setBackground(
            0, QBrush(QColor(color[0], color[1], color[2], color[3])))

    def handle_itemclick(self, item, column):
        speaker_row = self.manage_speaker_tree.indexOfTopLevelItem(item)
        if self.manage_speaker_tree.topLevelItemCount() > 1:
            for i in range(self.conversation_table.rowCount()):
                speaker = self.conversation_table.item(
                    i, 3).data(QtCore.Qt.UserRole)
                if speaker == speaker_row:
                    self.delete_button.setEnabled(False)
                    return
            self.delete_button.setEnabled(True)

    def delete_button_handler(self):
        current_item_index = self.manage_speaker_tree.indexOfTopLevelItem(
            self.manage_speaker_tree.currentItem())
        item = self.manage_speaker_tree.takeTopLevelItem(current_item_index)
        speaker_name = item.text(0)
        self.customsignal.delete_speakers.emit(
            current_item_index, speaker_name)

        if self.manage_speaker_tree.topLevelItemCount() == 1:
            self.delete_button.setEnabled(False)

    def handle_assign(self):
        self.customsignal.assign_speakers.emit(
            self.manage_speaker_tree.currentItem().text(0))
        self.accept()
