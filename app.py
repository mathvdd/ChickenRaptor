import sys
from PyQt6.QtGui import QTextCursor
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QFormLayout,
    QGridLayout,
    QTabWidget,
    QLineEdit,
    QDateEdit,
    QPushButton,
    QTextEdit,
)
from PyQt6.QtCore import Qt, QSize
from app_logger import AppLogger


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('ChickenRaptor')
        self.setFixedSize(QSize(800, 400))

        main_layout = QGridLayout(self)
        self.setLayout(main_layout)

        # create a tab widget
        tab = QTabWidget(self)

        # launch_page
        launch_page = QWidget(self)
        layout = QGridLayout()
        launch_page.setLayout(layout)
        layout.addWidget(QPushButton('First app'), 0, 0)
        layout.addWidget(QPushButton('Second app'), 1, 0)
        layout.addWidget(QPushButton('Third app'), 2, 0)
        layout.addWidget(QPushButton('Last app'), 3, 0)
        layout.setRowStretch(4, 1)


        self.logger = QTextEdit()
        self.logger.setReadOnly(True)
#        self.logger.verticalScrollBar().setValue(self.logger.verticalScrollBar().maximum())

        layout.addWidget(self.logger, 0, 1, 5, 1)

        self.app_logger = AppLogger(self.logger)
        
       
        # parameter_page
        contact_page = QWidget(self)
        layout = QFormLayout()
        contact_page.setLayout(layout)
        layout.addRow('Field 1:', QLineEdit(self))
        layout.addRow('Field 2:', QLineEdit(self))

        # finishing startup
        tab.addTab(launch_page, 'Launcher')
        tab.addTab(contact_page, 'Configuration')

        main_layout.addWidget(tab)


        self.show()

        self.app_logger.title("CHICKEN RAPTOR IS ON STEROIDS")
        

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec())
