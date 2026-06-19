import logging

from PyQt6.QtCore import QObject, QThread, pyqtSignal, pyqtSlot, QUrl



import os


class ServiceWorker(QObject):
    execute = pyqtSignal(object, str)

    finished = pyqtSignal(str)
    failed = pyqtSignal(str)

    def __init__(self):
        super().__init__()

        self.execute.connect(self.run_job)
    

    def play_sound(self):
        self.audio.play()

    @pyqtSlot(object, str)
    def run_job(self, func, name):
        try:

            logging.info(f"Starting {name}")
            func()
            logging.info(f"{name} ended\n")
            self.finished.emit(name)

        except Exception as e:
            logging.exception(f"Service failed: {name}\n", exc_info=True, stack_info=True)
            self.failed.emit(name)



class ServiceManager:
    def __init__(self):
        self.thread = QThread()

        self.worker = ServiceWorker()
        self.worker.moveToThread(self.thread)

        self.thread.start()

    def submit(self, func, name):
        self.worker.execute.emit(func, name)

    def stop(self):
        self.thread.quit()
        self.thread.wait()