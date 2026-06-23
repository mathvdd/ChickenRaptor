from PyQt6.QtWidgets import (
    QPushButton,
    QLabel,
    QComboBox
)
from PyQt6.QtGui import QPainter, QPixmap, QTextCursor
import logging
import rpt_automail
import rpt_pdf_ann
import rpt_transfer
import subprocess
import os
import sys

class NoScrollQComboBox(QComboBox):
    def wheelEvent(self, event):
        event.ignore()

def create_log_button(logger_widget, service_manager, player = None):
    butname = "Copy log"
    button = QPushButton(butname)
    
    service_name = f"RAPTOR LOG SERVICE: {butname}"

    def copy_log():
        logger_widget.selectAll()
        logger_widget.copy()
        logging.info('Log copied in the clipboard')

        cursor = logger_widget.textCursor()
        cursor.clearSelection()
        logger_widget.setTextCursor(cursor)

    def on_click():
        button.setEnabled(False)

        try:
            service_manager.submit(lambda: copy_log(), service_name)
        except Exception as e:
            logging.critical(f"Failed during {service_name}", exc_info=True)

    def on_finished(name):
        if name == service_name:
            button.setEnabled(True)
            if player:
                player.randomly_play_random()


    service_manager.worker.finished.connect(on_finished)
    service_manager.worker.failed.connect(on_finished)
    
    button.clicked.connect(on_click)
    return button


def create_update_button(logger_widget, service_manager, player = None):

    base = os.path.join(os.path.dirname(__file__), "..")

    def git_get_behind():
        subprocess.run(
            ["git", "fetch"],
            cwd=base,
            check=True,
            capture_output=True,
            text=True,
        )

        behind = int(
            subprocess.check_output(
                ["git", "rev-list", "--count", "HEAD..@{u}"],
                cwd=base,
                text=True,
            ).strip()
        )

        return behind

    def git_update():
        nonlocal restart_required

        behind = git_get_behind()
        if behind == 0:
            logging.info("Already up to date.")
        else:    

            logging.info(
                f"Update available: {behind} commit{'s' if behind != 1 else ''} behind."
            )

            pull_result = subprocess.run(
                ["git", "pull"],
                cwd=base,
                check=True,
                capture_output=True,
                text=True,
            )
            logging.info(pull_result.stdout)

            restart_required = True

    def restart_app():
        # os.execv(sys.executable, [sys.executable] + sys.argv)
        
        python = sys.executable
        script = os.path.abspath(sys.argv[0])

        subprocess.Popen(
            [python, script] + sys.argv[1:],
            cwd=os.path.dirname(script),
        )

        os._exit(0)

    behind = git_get_behind()
    
    butname = "Update"
    button = QPushButton(butname)
    button.setText(f"{butname} {f'({behind})' if behind != 0 else ''}")

    service_name = f"RAPTOR UPDATE SERVICE: {butname}"

    restart_required = False

    def on_click():
        if restart_required:
            restart_app()
            return

        button.setEnabled(False)

        try:
            service_manager.submit(lambda: git_update(), service_name)
            
        except Exception as e:
            logging.critical(f"Failed during {service_name}", exc_info=True)

    def on_finished(name):
        if name == service_name:
            
            button.setEnabled(True)

            if restart_required:
                button.setText("Restart")
            # else:
            #     behind = git_get_behind()
            #     button.setText(f"Update ({behind})" if behind else "Update")

            if player:
                player.randomly_play_random()
            

    service_manager.worker.finished.connect(on_finished)
    service_manager.worker.failed.connect(on_finished)
    
    button.clicked.connect(on_click)
    return button


def create_mail_button(config, service_manager, butname, perso_info_selector, player = None):
    
    button = QPushButton(butname)
    
    service_name = f"RAPTOR EMAIL SERVICE: {butname}"
    def on_click():
        button.setEnabled(False)

        try:
            service_manager.submit(lambda: rpt_automail.send_emails(config, perso_info_selector), service_name)
        except Exception as e:
            logging.critical(f"Failed during: {service_name}", exc_info=True)

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
            logging.critical(f"Failed during: {service_name}", exc_info=True)

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
            service_manager.submit(lambda: rpt_transfer.transfer(config), service_name)
        except Exception as e:
            logging.critical(f"Failed during: {service_name}", exc_info=True)

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
            logging.critical(f"Failed to save parameters", exc_info=True)

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

