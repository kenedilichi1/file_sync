import time
import sys
from threading import Lock

class ProgressBar:
    def __init__(self, total, description="Progress", width=50):
        self.total = total
        self.description = description
        self.width = width
        self.current = 0
        self.start_time = time.time()
        self.lock = Lock()
    
    def update(self, value):
        """Update progress bar with new value"""
        with self.lock:
            self.current = value
            self._display()
    
    def increment(self, delta=1):
        """Increment progress by delta"""
        with self.lock:
            self.current += delta
            self._display()
    
    def _display(self):
        """Display the progress bar"""
        progress = min(1.0, self.current / self.total)
        bar_width = int(self.width * progress)
        bar = "█" * bar_width + " " * (self.width - bar_width)
        
        elapsed = time.time() - self.start_time
        if progress > 0:
            eta = elapsed / progress * (1 - progress)
        else:
            eta = 0
        
        sys.stdout.write(
            f"\r{self.description}: |{bar}| {progress*100:.1f}% "
            f"({self.current}/{self.total}) "
            f"[{time.strftime('%H:%M:%S', time.gmtime(elapsed))}<"
            f"{time.strftime('%H:%M:%S', time.gmtime(eta))}]"
        )
        sys.stdout.flush()
    
    def close(self):
        """Complete the progress bar"""
        self.update(self.total)
        sys.stdout.write("\n")
        sys.stdout.flush()

class TransferProgress:
    def __init__(self, filename, total_size):
        self.filename = filename
        self.total_size = total_size
        self.progress_bar = ProgressBar(total_size, f"Transferring {filename}")
    
    def update(self, transferred):
        self.progress_bar.update(transferred)
    
    def close(self):
        self.progress_bar.close()