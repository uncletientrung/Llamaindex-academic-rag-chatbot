import time
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Thư mục cần theo dõi
PROJECT_DIR = Path(__file__).resolve().parent

# Bỏ qua những thư mục/file thường xuyên thay đổi
IGNORED_DIRS = {
    ".git",
    ".venv",
    "__pycache__",
    "node_modules",
}

class FileChangeHandler(FileSystemEventHandler):
    def should_ignore(self, path):
        p = Path(path)

        # Bỏ qua file nằm trong các thư mục không cần theo dõi
        try:
            relative = p.relative_to(PROJECT_DIR)
        except ValueError:
            return True

        if any(part in IGNORED_DIRS for part in relative.parts):
            return True

        return False

    def on_created(self, event):
        if not self.should_ignore(event.src_path):
            print(f"[THÊM] {event.src_path}")

    def on_deleted(self, event):
        if not self.should_ignore(event.src_path):
            print(f"[XÓA] {event.src_path}")

    def on_modified(self, event):
        if not self.should_ignore(event.src_path):
            print(f"[SỬA] {event.src_path}")

    def on_moved(self, event):
        if not self.should_ignore(event.src_path):
            print(f"[DI CHUYỂN] {event.src_path} -> {event.dest_path}")


if __name__ == "__main__":
    observer = Observer()
    observer.schedule(
        FileChangeHandler(),
        str(PROJECT_DIR),
        recursive=True,
    )
    observer.start()

    print(f"Đang theo dõi file trong: {PROJECT_DIR}")
    print("Nhấn Ctrl+C để dừng.")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()