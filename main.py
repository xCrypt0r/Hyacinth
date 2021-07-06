import sys
import json
import threading
import qtmodern.styles
import qtmodern.windows
from PySide2.QtGui import QIcon, QFontDatabase, QFont
from PySide2.QtWidgets import *
from PySide2.QtCore import *
from sweeper import DCSweeper

class Window(QWidget):
    send_message_signal = Signal(str, str)
    update_signal = Signal(str, int)

    def __init__(self):
        super().__init__()

        self.sweepers = []

        with open('assets/json/const.json', encoding='utf8') as const_file:
            const = json.load(const_file)
            self.galleries = const['galleries']
            self.minor_galleries = dict(map(lambda x: (x[0], 'ⓜ' + x[1]),
                const['minor_galleries'].items()))

        with open('assets/json/config.json', encoding='utf8') as config_file:
            config = json.load(config_file)
            self.default_target_galleries = config['default_target_galleries']

        self.load_ui()
        self.check_sweepers()
        self.add_default_targets()
        self.send_message_signal.connect(self.show_message)
        self.update_signal.connect(self.update)

    def load_ui(self):
        self.setWindowTitle('DCSweeper')
        self.setFixedSize(500, 300)

        qr = self.frameGeometry()
        cp = QApplication.primaryScreen().availableGeometry().center()

        qr.moveCenter(cp)
        self.move(qr.topLeft())

        self.cmb_galleries = QComboBox(self)
        galleries = list(sorted(self.galleries.values()))
        minor_galleries = list(sorted(self.minor_galleries.values()))
        galleries += minor_galleries

        self.cmb_galleries.addItems(galleries)
        self.cmb_galleries.setGeometry(20, 20, 140, 30)

        self.btn_add = QPushButton('추가', self)

        self.btn_add.setGeometry(165, 20, 40, 30)
        self.btn_add.clicked.connect(self.add_target)

        self.tbl_targets = QTableWidget(0, 3, self)

        self.tbl_targets.setHorizontalHeaderLabels(['갤러리', '화력', '재연결'])
        self.tbl_targets.setGeometry(20, 60, 460, 220)
        self.tbl_targets.horizontalHeader().setStyleSheet(
            'QHeaderView::section { padding-right: 10px; border: 0 }')
        self.tbl_targets.verticalHeader().setVisible(False)
        self.tbl_targets.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tbl_targets.setFocusPolicy(Qt.NoFocus)
        self.tbl_targets.setSelectionMode(QAbstractItemView.NoSelection)
        self.tbl_targets.doubleClicked.connect(self.remove_target)

        header = self.tbl_targets.horizontalHeader()

        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)

    def check_sweepers(self):
        if len(self.sweepers) > 0:
            for sweeper in self.sweepers:
                if not sweeper._timer.is_alive():
                    print(f'\n<{sweeper.gallery_title}> 갤러리에 재연결합니다...\n')
                    self.refresh_target(sweeper.gallery_title)

                    break

        timer = threading.Timer(5, self.check_sweepers)
        timer.daemon = True

        timer.start()

    def add_default_targets(self):
        for gallery_title in self.default_target_galleries:
            self.cmb_galleries.setCurrentText(gallery_title)
            self.add_target()

    def add_target(self):
        self.btn_add.setEnabled(False)

        gallery_title = self.cmb_galleries.currentText()

        if self.get_gallery_index(gallery_title) is not None:
            self.send_message_signal.emit('이미 테이블에 추가된 갤러리입니다!', '오류')
            self.btn_add.setEnabled(True)

            return

        gallery_id = self.get_gallery_id(gallery_title)
        index = self.tbl_targets.rowCount()

        self.tbl_targets.insertRow(index)
        self.tbl_targets.setItem(index, 0, QTableWidgetItem(gallery_title))
        self.tbl_targets.setItem(index, 1, QTableWidgetItem('0'))

        btn_refresh = QPushButton(self.tbl_targets, flat=True)

        self.tbl_targets.setCellWidget(index, 2, btn_refresh)
        btn_refresh.setStyleSheet('background-color: rgba(255, 255, 255, 0)')
        btn_refresh.setIcon(QIcon('assets/images/refresh.png'))
        btn_refresh.clicked.connect(self.refresh_target)

        sweeper = DCSweeper(self, gallery_id, gallery_title)

        sweeper.start_sweeping()
        self.sweepers.append(sweeper)
        self.btn_add.setEnabled(True)

    def remove_target(self):
        index = self.tbl_targets.currentIndex().row()
        gallery_title = self.tbl_targets.item(index, 0).text()
        reply = QMessageBox.question(self,
            '삭제',
            f'{gallery_title} 갤러리 크롤링을 중지할까요?',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No)

        if reply == QMessageBox.Yes:
            sweeper = self.get_sweeper(gallery_title)

            sweeper.stop_sweeping()
            self.tbl_targets.removeRow(index)
            self.sweepers.remove(sweeper)

    def refresh_target(self, gallery_title=''):
        if not gallery_title:
            btn = self.sender()
            index = self.tbl_targets.indexAt(btn.pos()).row()
            gallery_title = self.tbl_targets.item(index, 0).text()

        gallery_id = self.get_gallery_id(gallery_title)
        sweeper = self.get_sweeper(gallery_title)

        sweeper.stop_sweeping()
        self.sweepers.remove(sweeper)

        sweeper = DCSweeper(self, gallery_id, gallery_title)

        sweeper.start_sweeping()
        self.sweepers.append(sweeper)

    def get_gallery_id(self, gallery_title):
        for id, title in { **self.galleries, **self.minor_galleries }.items():
            if title == gallery_title:
                return id

    def get_gallery_index(self, gallery_title):
        for index in range(self.tbl_targets.rowCount()):
            if self.tbl_targets.item(index, 0).text() == gallery_title:
                return index

    def get_sweeper(self, gallery_title):
        for sweeper in self.sweepers:
            if sweeper.gallery_title == gallery_title:
                return sweeper

    @Slot(str, int)
    def update(self, gallery_title, count):
        index = self.get_gallery_index(gallery_title)

        try:
            self.tbl_targets.setItem(index, 1, QTableWidgetItem(str(count)))
        except TypeError:
            pass

    @Slot(str, str)
    def show_message(self, message, title):
        msgbox = QMessageBox(self)

        msgbox.setText(message)

        if title:
            msgbox.setWindowTitle(title)

        msgbox.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = qtmodern.windows.ModernWindow(Window())
    font_db = QFontDatabase()

    font_db.addApplicationFont('assets/fonts/ONE Mobile POP.ttf')
    qtmodern.styles.dark(app)
    window.show()
    app.setFont(QFont('ONE Mobile POP', 12))
    app.exec_()