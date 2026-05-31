from PyQt6.QtWidgets import (
    QPushButton,
    QLabel
)
import logging
import rpt_automail

def create_automail_button(config_automail, service_manager):

    button = QPushButton("Automail")
    
    service_name = "RAPTOR EMAIL SERVICE"
    def on_click():
        button.setEnabled(False)

        try:
            service_manager.submit(lambda: rpt_automail.send_all_emails(config_automail), service_name)
        except Exception as e:
            logging.critical(f"Failed to launch {service_name}", exc_info=True)

    def on_finished(name):
        if name == service_name:
            button.setEnabled(True)

    service_manager.worker.finished.connect(on_finished)
    service_manager.worker.failed.connect(on_finished)
    
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
