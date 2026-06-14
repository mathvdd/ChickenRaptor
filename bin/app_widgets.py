from PyQt6.QtWidgets import (
    QPushButton,
    QLabel,
)
from PyQt6.QtGui import QPainter, QPixmap
import logging
import rpt_automail
import rpt_pdf_ann
import rpt_transfer

def create_automail_button(config, service_manager, player = None):

    butname = "AutoMail"
    button = QPushButton(butname)
    
    service_name = f"RAPTOR EMAIL SERVICE: {butname}"
    def on_click():
        button.setEnabled(False)

        try:
            service_manager.submit(lambda: rpt_automail.send_all_emails(config), service_name)
        except Exception as e:
            logging.critical(f"Failed to launch {service_name}", exc_info=True)

    def on_finished(name):
        if name == service_name:
            button.setEnabled(True)
            if player:
                player.randomly_play_random()


    service_manager.worker.finished.connect(on_finished)
    service_manager.worker.failed.connect(on_finished)
    
    button.clicked.connect(on_click)
    return button


def create_annotate_button(config, service_manager, butname, player = None):

    button = QPushButton(butname)
    
    service_name = f"RAPTOR DOCUMENT ANNOTATION: {butname}"
    def on_click():
        button.setEnabled(False)

        try:
            service_manager.submit(lambda: rpt_pdf_ann.make_all_annotations(config), service_name)
        except Exception as e:
            logging.critical(f"Failed to launch {service_name}", exc_info=True)

    def on_finished(name):
        if name == service_name:
            button.setEnabled(True)
            if player:
                player.randomly_play_random()

    service_manager.worker.finished.connect(on_finished)
    service_manager.worker.failed.connect(on_finished)
    
    button.clicked.connect(on_click)
    return button

def create_transfer_button(config, service_manager, butname, player = None):

    button = QPushButton(butname)
    
    service_name = f"RAPTOR DOCUMENT TRANSFERT: {butname}"
    def on_click():
        button.setEnabled(False)

        try:
            service_manager.submit(lambda: rpt_transfer.transfertC4(config), service_name)
        except Exception as e:
            logging.critical(f"Failed to launch {service_name}", exc_info=True)

    def on_finished(name):
        if name == service_name:
            button.setEnabled(True)

            if player:
                player.randomly_play_random()

    service_manager.worker.finished.connect(on_finished)
    service_manager.worker.failed.connect(on_finished)
    
    button.clicked.connect(on_click)
    return button

def create_save_button(config_handler, player = None):
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

        finally:
            if player:
                player.randomly_play_random()
    
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

