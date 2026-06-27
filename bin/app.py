import sys
import os
from PyQt6.QtGui import QTextCursor, QPixmap
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
    QComboBox,
)
from PyQt6.QtCore import Qt, QSize
import app_logger
import logging
import rpt_config
import app_widgets
from rpt_service_manager import ServiceManager
import rpt_player
from rpt_db_connect import info_from_RN, info_from_barcode
from rpt_pdf_ann import rename_C4

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        app = QApplication.instance()
        if app is not None:
            font = app.font()
            font.setPointSize(11)
            app.setFont(font)

        self.setWindowTitle('ChickenRaptor')
        self.setFixedSize(QSize(1050, 550))

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
        # self.logger_widget.setStyleSheet("""
        #     QTextEdit {
        #         background-image: url(assets/ChickenRaptor.png);
        #         background-repeat: no-repeat;
        #         background-position: center;
        #         background-color: rgba(255,255,255,180);
        #     }
        # """)
        layout.addWidget(self.logger_widget, 0, 1, 10, 1)
        self.logger = app_logger.setup_logging(level=logging.DEBUG)
        app_logger.attach_qt_logger(self.logger, self.logger_widget)
        logging.info("CHICKEN RAPTOR IS ON STEROIDS")

        #import app_config
        self.config_handler = rpt_config.RptConfig()
        self.param_widgets_holder = {}
        
        self.player = rpt_player.Player()

        #initiate service manager
        self.service_manager = ServiceManager()

        #app buttons
        layout.addWidget(app_widgets.create_header_label("Contrats"),0,0)
        layout.addWidget(
            app_widgets.create_annotate_button(
                self.config_handler.config.get("AnnotateContrat2Pages") | self.config_handler.config.get("general_annotate"),
                self.service_manager,
                'AnnotateContrat2Pages',
                self.player
                ), 1,0)

        layout.addWidget(
            app_widgets.create_mail_button(
                self.config_handler.config.get("mail_server") | self.config_handler.config.get("send_email_contract") | self.config_handler.config.get("database"),
                self.service_manager,
                "Contracts AutoMail",
                info_from_barcode,
                self.player
                )
                , 2, 0)
        layout.addWidget(
            app_widgets.create_transfer_button(
                self.config_handler.config.get("TransfertContrat"),
                self.service_manager,
                'TransfertContrat',
                self.player
                ), 3,0)
    

        layout.addWidget(app_widgets.create_header_label("C4"),4,0)
        layout.addWidget(
            app_widgets.create_annotate_button(
                self.config_handler.config.get("specific_C4Bis") | self.config_handler.config.get("AnnotateC4") | self.config_handler.config.get("general_annotate"),
                self.service_manager,
                'AnnotateC4Bis',
                self.player,
                rename_C4
                ), 5,0)
        layout.addWidget(
            app_widgets.create_annotate_button(
                self.config_handler.config.get("specific_C4Mis") | self.config_handler.config.get("AnnotateC4") | self.config_handler.config.get("general_annotate"),
                self.service_manager,
                'AnnotateC4Mis',
                self.player,
                rename_C4
                ), 6,0)
        layout.addWidget(
            app_widgets.create_mail_button(
                self.config_handler.config.get("mail_server") | self.config_handler.config.get("send_email_C4") | self.config_handler.config.get("database"),
                self.service_manager,
                "C4 AutoMail",
                info_from_RN,
                self.player
                )
                , 7, 0)
        
        label = QLabel(self)
        pixmap = QPixmap(os.path.join(self.config_handler.package_path, '..', 'assets', 'ChickenRaptor_medium.png'))
        label.setPixmap(pixmap)
        layout.addWidget(label, 8, 0)

        layout.addWidget(
            app_widgets.create_update_button(
                self.logger_widget,
                self.service_manager,
                self.player
                ), 9,0)
        layout.setRowStretch(9, 1)


        # parameter_page
        contact_page = QWidget(self)

        page_layout = QGridLayout(contact_page)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)

        form_widget = QWidget()
        form_layout = QFormLayout(form_widget)

        page_layout.addWidget(app_widgets.create_save_button(self.config_handler, self.player))

        for section, fields in self.config_handler.config.items():
            form_layout.addRow(app_widgets.create_header_label(section))
            for key, element in fields.items():
                if element.get_value_type() is bool:
                    edit = app_widgets.NoScrollQComboBox()
                    edit.addItems([rpt_config.translate_values.get("True"), rpt_config.translate_values.get("False")])
                    if element.get_value():
                        edit.setCurrentText(rpt_config.translate_values.get("True"))
                    else:
                        edit.setCurrentText(rpt_config.translate_values.get("False"))
                    
                else:
                    edit = QLineEdit(str(element.get_value()))
                # key_display = element.display if element.display is not None else key
                key_display = key
                form_layout.addRow(f"{key_display}:", edit)
                element.set_widget(edit)

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
