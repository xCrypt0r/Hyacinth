import sys
import qtmodern.styles
import qtmodern.windows
from PySide2.QtGui import (
    QFont,
    QFontDatabase
)
from PySide2.QtWidgets import QApplication
from window import Window

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = qtmodern.windows.ModernWindow(Window())
    font_db = QFontDatabase()

    font_db.addApplicationFont('assets/fonts/ONE Mobile POP.ttf')
    qtmodern.styles.dark(app)
    window.show()
    app.setFont(QFont('ONE Mobile POP', 12))
    app.exec_()