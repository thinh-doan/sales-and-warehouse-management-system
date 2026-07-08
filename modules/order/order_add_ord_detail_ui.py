from PyQt6 import QtCore, QtWidgets


class Ui_hopThoaiThemSP(object):
    def setupUi(self, hopThoaiThemSP):
        hopThoaiThemSP.setObjectName("hopThoaiThemSP")
        hopThoaiThemSP.resize(420, 220)
        hopThoaiThemSP.setWindowTitle("Thêm sản phẩm vào đơn hàng")

        self.verticalLayout = QtWidgets.QVBoxLayout(hopThoaiThemSP)
        self.verticalLayout.setObjectName("verticalLayout")

        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setObjectName("formLayout")

        self.lblSanPham = QtWidgets.QLabel(parent=hopThoaiThemSP)
        self.lblSanPham.setObjectName("lblSanPham")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.ItemRole.LabelRole, self.lblSanPham)
        self.cboSanPham = QtWidgets.QComboBox(parent=hopThoaiThemSP)
        self.cboSanPham.setObjectName("cboSanPham")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.ItemRole.FieldRole, self.cboSanPham)

        self.lblMaSP = QtWidgets.QLabel(parent=hopThoaiThemSP)
        self.lblMaSP.setObjectName("lblMaSP")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.ItemRole.LabelRole, self.lblMaSP)
        self.txtMaSP = QtWidgets.QLineEdit(parent=hopThoaiThemSP)
        self.txtMaSP.setReadOnly(True)
        self.txtMaSP.setObjectName("txtMaSP")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.ItemRole.FieldRole, self.txtMaSP)

        self.lblSoLuong = QtWidgets.QLabel(parent=hopThoaiThemSP)
        self.lblSoLuong.setObjectName("lblSoLuong")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.ItemRole.LabelRole, self.lblSoLuong)
        self.txtSoLuong = QtWidgets.QSpinBox(parent=hopThoaiThemSP)
        self.txtSoLuong.setMinimum(1)
        self.txtSoLuong.setMaximum(100000)
        self.txtSoLuong.setObjectName("txtSoLuong")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.ItemRole.FieldRole, self.txtSoLuong)

        self.verticalLayout.addLayout(self.formLayout)

        self.buttonBox = QtWidgets.QDialogButtonBox(parent=hopThoaiThemSP)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.StandardButton.Cancel | QtWidgets.QDialogButtonBox.StandardButton.Save)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(hopThoaiThemSP)
        QtCore.QMetaObject.connectSlotsByName(hopThoaiThemSP)

    def retranslateUi(self, hopThoaiThemSP):
        _translate = QtCore.QCoreApplication.translate
        self.lblSanPham.setText(_translate("hopThoaiThemSP", "Sản phẩm"))
        self.lblMaSP.setText(_translate("hopThoaiThemSP", "Mã sản phẩm"))
        self.lblSoLuong.setText(_translate("hopThoaiThemSP", "Số lượng"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    dialog = QtWidgets.QDialog()
    ui = Ui_hopThoaiThemSP()
    ui.setupUi(dialog)
    dialog.show()
    sys.exit(app.exec())


