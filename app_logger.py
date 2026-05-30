from PyQt6.QtGui import QTextCursor
import sys

class QtLogger:
    def __init__(self, widget):
        self.widget = widget

    def write(self, text):
        #self.widget.moveCursor(QTextCursor.MoveOperation.End)
        # self.widget.insertPlainText(text)
        # self.widget.moveCursor(QTextCursor.MoveOperation.End)

        if text:
            self.widget.insertPlainText(text)
            self.widget.ensureCursorVisible()


    def flush(self):
        pass

class Tee:
    def __init__(self, *streams):
        self.streams = streams

    def write(self, text):
        for s in self.streams:
            s.write(text)

    def flush(self):
        for s in self.streams:
            s.flush()


class AppLogger():

    def __init__(self, QTextEdit_object):
        self.original_stdout = sys.stdout
        self.original_stderr = sys.stderr

        self.qt_logger = QtLogger(QTextEdit_object)
        
        sys.stdout = Tee(self.qt_logger, self.original_stdout)
        sys.stderr = Tee(self.qt_logger, self.original_stderr)

    def info(self, text: str):
        line = f"[INFO] {text}\n"
        self.qt_logger.write(line)
        self.original_stdout.write(line)        

    def title(self, text: str):
        line = f"[INFO]  ----- {text} -----\n".upper()
        self.qt_logger.write(line)
        self.original_stdout.write(line)        
