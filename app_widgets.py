from PyQt6.QtWidgets import (
    QPushButton,
    QLabel
)
import logging
import rpt_automail

def create_automail_button(config_automail):

    def on_click():
        try:
            logging.info("LAUNCHING RAPTOR EMAIL SERVICE")
            rpt_automail.send_all_emails(config_automail)
            logging.info("... Finished")
        except Exception as e:
            logging.critical("Failed to launch raptor mail service", exc_info=True)

    button = QPushButton("Automail")
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
