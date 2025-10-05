from PyQt6.QtCore import QThread, pyqtSignal

class WorkerThread(QThread):
    """Worker thread for background tasks"""
    progress_signal = pyqtSignal(int, str)
    finished_signal = pyqtSignal(bool, str)
    
    def __init__(self, task_func, *args, **kwargs):
        super().__init__()
        self.task_func = task_func
        self.args = args
        self.kwargs = kwargs
        
    def run(self):
        try:
            result = self.task_func(*self.args, **self.kwargs)
            self.finished_signal.emit(*result)
        except Exception as e:
            self.finished_signal.emit(False, str(e))