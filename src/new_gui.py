from PyQt6.QtWidgets import QApplication

class LocalSyncGUI:
    def __init__(self, cli_instance):
        self.cli_instance = cli_instance
        self.qt_app = QApplication.instance() or QApplication([])

        from gui.core.app_controller import AppController
        from gui.ui.main_window import MainWindow

        self.controller = AppController(cli_instance)
        self.main_window = MainWindow(self.controller)

        # Connect cleanup before app exits
        self.qt_app.aboutToQuit.connect(self.cleanup_before_exit)

    def run(self):
        self.main_window.show_login_dialog()
        self.main_window.show()
        return self.qt_app.exec()

    def cleanup_before_exit(self):
        """Stop background threads and receivers cleanly (blocking)."""
        print("🧹 Cleanup before exit (GUI)...")
        try:
            # Stop receiver if present
            if hasattr(self.cli_instance, "file_transfer") and getattr(self.cli_instance, "file_transfer", None):
                try:
                    # stop_receiver should block until threads exit (see above)
                    self.cli_instance.file_transfer.stop_receiver()
                except Exception as e:
                    print(f"⚠️ Error stopping file receiver: {e}")

            # If controller has any QThreads, tell them to stop and wait
            if hasattr(self.controller, "stop_all_threads"):
                try:
                    self.controller.stop_all_threads()
                except Exception as e:
                    print(f"⚠️ Error stopping controller threads: {e}")

            # As a last resort, give the system a moment to clean up
            import time
            time.sleep(0.2)

        except Exception as e:
            print(f"⚠️ Cleanup exception: {e}")
