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
    QLabel,
    QScrollArea,
)
from PyQt6.QtCore import Qt, QSize
import app_logger
import logging
import rpt_config
import app_widgets
from rpt_service_manager import ServiceManager

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

        #logger
        self.logger_widget = QTextEdit()
        self.logger_widget.setReadOnly(True)
        layout.addWidget(self.logger_widget, 0, 1, 5, 1)
        self.logger = app_logger.setup_logging()
        app_logger.attach_qt_logger(self.logger, self.logger_widget)
        logging.info("CHICKEN RAPTOR IS ON STEROIDS")

        #import app_config
        self.config_handler = rpt_config.RptConfig()
        
        #initiate service manager
        self.service_manager = ServiceManager()

        #app buttons
        layout.addWidget(QPushButton('First app'), 0, 0)
        layout.addWidget(QPushButton('Second app'), 1, 0)
        layout.addWidget(QPushButton('Third app'), 2, 0)
        layout.addWidget(
            app_widgets.create_automail_button(
                self.config_handler.config.get("automail"),
                self.service_manager
                )
                , 3, 0)
        layout.setRowStretch(4, 1)


        # parameter_page
        contact_page = QWidget(self)

        page_layout = QGridLayout(contact_page)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)

        form_widget = QWidget()
        form_layout = QFormLayout(form_widget)

        for paramdictkey, paramdict in self.config_handler.config.items():
            form_layout.addRow(app_widgets.create_header_label(paramdictkey))

            for key, value in paramdict.items():
                edit = QLineEdit(str(value) if value is not None else "")
                form_layout.addRow(f"{key}:", edit)

        scroll.setWidget(form_widget)

        page_layout.addWidget(scroll)
        

        # finishing startup
        tab.addTab(launch_page, 'Launcher')
        tab.addTab(contact_page, 'Configuration')

        main_layout.addWidget(tab)


        self.show()


    def closeEvent(self, event):
        self.service_manager.stop()
        event.accept()        
                

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec())
