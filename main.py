import sys
import json
from PySide2.QtGui import QIcon
from PySide2.QtWidgets import *
from sweeper import DCSweeper

class Window(QWidget):
    def __init__(self):
        super().__init__()

        self.sweepers = []

        with open('const.json', encoding='utf8') as const_file:
            const = json.load(const_file)
            self.galleries = const['galleries']

        self.load_ui()

    def load_ui(self):
        self.setWindowTitle('DCSweeper')
        self.setGeometry(100, 100, 500, 300)
        self.setWindowIcon(QIcon('assets/icon.png'))

        qr = self.frameGeometry()
        cp = QApplication.primaryScreen().availableGeometry().center()

        qr.moveCenter(cp)
        self.move(qr.topLeft())

        self.cmb_galleries = QComboBox(self)
        galleries = list(sorted(self.galleries.values()))

        self.cmb_galleries.addItems(galleries)
        self.cmb_galleries.setGeometry(20, 20, 140, 20)
        self.cmb_galleries.setCurrentIndex(galleries.index('국내야구'))

        self.btn_add = QPushButton('추가', self)

        self.btn_add.setGeometry(165, 20, 40, 20)
        self.btn_add.clicked.connect(self.add_target)

        self.tbl_targets = QTableWidget(0, 2, self)

        self.tbl_targets.setHorizontalHeaderLabels(['갤러리', '화력'])
        self.tbl_targets.setGeometry(20, 60, 460, 220)

        header = self.tbl_targets.horizontalHeader()

        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)

    def add_target(self):
        gallery_title = self.cmb_galleries.currentText()
        gallery_id = self.get_gallery_id(gallery_title)
        index = self.tbl_targets.rowCount()

        self.tbl_targets.insertRow(index)
        self.tbl_targets.setItem(index, 0, QTableWidgetItem(gallery_title))
        self.tbl_targets.setItem(index, 1, QTableWidgetItem('0'))

        sweeper = DCSweeper(self, index, gallery_id, gallery_title)

        sweeper.start_sweeping()
        self.sweepers.append(sweeper)

    def get_gallery_id(self, gallery):
        for id, name in self.galleries.items():
            if name == gallery:
                return id

    def update(self, index, count):
        self.tbl_targets.setItem(index, 1, QTableWidgetItem(str(count)))

    def closeEvent(self, QCloseEvent):
        for sweeper in self.sweepers:
            sweeper.stop_sweeping()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Window()

    window.show()
    app.exec_()