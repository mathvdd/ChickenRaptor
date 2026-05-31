from PyQt6.QtWidgets import (
    QPushButton,
    QLabel
)
import logging
import rpt_automail
import rpt_pdf_ann

def create_automail_button(config, service_manager):

    button = QPushButton("AutoMail")
    
    service_name = "RAPTOR EMAIL SERVICE"
    def on_click():
        button.setEnabled(False)

        try:
            service_manager.submit(lambda: rpt_automail.send_all_emails(config), service_name)
        except Exception as e:
            logging.critical(f"Failed to launch {service_name}", exc_info=True)

    def on_finished(name):
        if name == service_name:
            button.setEnabled(True)

    service_manager.worker.finished.connect(on_finished)
    service_manager.worker.failed.connect(on_finished)
    
    button.clicked.connect(on_click)
    return button


def create_annotate_button(config, service_manager, butname):

    button = QPushButton(butname)
    
    service_name = "RAPTOR DOCUMENT ANNOTATION"
    def on_click():
        button.setEnabled(False)

        try:
            service_manager.submit(lambda: rpt_pdf_ann.make_all_annotations(config), service_name)
        except Exception as e:
            logging.critical(f"Failed to launch {service_name}", exc_info=True)

    def on_finished(name):
        if name == service_name:
            button.setEnabled(True)

    service_manager.worker.finished.connect(on_finished)
    service_manager.worker.failed.connect(on_finished)
    
    button.clicked.connect(on_click)
    return button

def create_transfert_button(config, service_manager, butname):

    button = QPushButton(butname)
    
    service_name = "RAPTOR DOCUMENT TRANSFERT"
    def on_click():
        button.setEnabled(False)

        try:
            service_manager.submit(lambda: rpt_transfert.transfertC4(config), service_name)
        except Exception as e:
            logging.critical(f"Failed to launch {service_name}", exc_info=True)

    def on_finished(name):
        if name == service_name:
            button.setEnabled(True)

    service_manager.worker.finished.connect(on_finished)
    service_manager.worker.failed.connect(on_finished)
    
    button.clicked.connect(on_click)
    return button

def create_save_button(config_handler):
    # todo activate button on parameter change
    button = QPushButton("Save")
    
    def on_click():
        # button.setEnabled(False)
        try:
            config_handler.sync_widget2value()
            config_handler.export_config()

            logging.info("Parameters saved")
        except Exception as e:
            logging.critical(f"Failed to save paramters", exc_info=True)
    
    button.clicked.connect(on_click)
    return button

    
def create_header_label(labelstr):
    label = QLabel(labelstr.upper())
    label.setStyleSheet("""
        font-weight: bold;
        font-size: 12px;
        margin-top: 10px;
    """)
    return label
