from PyQt6.QtCore import QThread, pyqtSignal

class WorkerThread(QThread):
    finished_signal = pyqtSignal(bool, str)

    def __init__(self, task):
        super().__init__()
        self.task = task  # ✅ store the task (missing in your version)

    def run(self):
        try:
            # ✅ If task is a callable (function), call it and unpack results
            if callable(self.task):
                success, message = self.task()
            else:
                success, message = False, "Invalid task type"
            self.finished_signal.emit(success, message)
        except Exception as e:
            # ✅ Emit both bool + message as required by the signal
            self.finished_signal.emit(False, str(e))