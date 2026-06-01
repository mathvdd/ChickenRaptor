import logging
from PyQt6.QtCore import QObject, pyqtSignal
from html import escape


class QtEmitter(QObject):
    message = pyqtSignal(str)

class QtHandler(logging.Handler):
    def __init__(self, emitter: QtEmitter):
        super().__init__()
        self.emitter = emitter
    def emit(self, record):
        msg = escape(self.format(record))

        color = {
            "INFO": "green",
            "WARNING": "orange",
            "ERROR": "red",
            "CRITICAL": "darkred",
            "DEBUG": "gray",
        }.get(record.levelname, "black")

        prefix = escape(f"[{record.levelname}]")

        html = msg.replace(
            prefix,
            f'<span style="color:{color}">{prefix}</span>',
            1
        )

        # Preserve traceback line breaks
        html = html.replace("\n", "<br>")

        self.emitter.message.emit(html)


def setup_logging(level=logging.INFO):
    logger = logging.getLogger()
    logger.setLevel(level)

    if logger.handlers:
        logger.handlers.clear()

    formatter = logging.Formatter("[%(levelname)s] %(message)s")

    console = logging.StreamHandler()
    console.setFormatter(formatter)

    logger.addHandler(console)

    return logger


def attach_qt_logger(logger, text_widget):
    emitter = QtEmitter()

    handler = QtHandler(emitter)
    handler.setFormatter(
        logging.Formatter("[%(levelname)s] %(message)s")
    )

    logger.addHandler(handler)

    emitter.message.connect(text_widget.append)

    return emitter
