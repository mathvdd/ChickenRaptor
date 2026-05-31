import logging

from PyQt6.QtCore import QObject, QThread, pyqtSignal, pyqtSlot


class ServiceWorker(QObject):
    execute = pyqtSignal(object, str)

    finished = pyqtSignal(str)
    failed = pyqtSignal(str)

    def __init__(self):
        super().__init__()

        self.execute.connect(self.run_job)

    @pyqtSlot(object, str)
    def run_job(self, func, name):
        try:

            logging.info(f"Starting {name}")
            func()
            logging.info(f"... Finished {name}")
            self.finished.emit(name)

        except Exception:
            logging.exception(f"Service {name} failed")
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