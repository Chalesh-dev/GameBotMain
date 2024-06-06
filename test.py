# import the modules
import os
import sys
import time
import logging
from typing import Optional

from watchdog.events import FileSystemEventHandler, FileSystemEvent, DirMovedEvent, FileMovedEvent, FileCreatedEvent, \
    DirCreatedEvent
from watchdog.observers import Observer


def run():
    print("hey sasdasalam")


class LoggingEventHandler(FileSystemEventHandler):
    def __init__(self, logger: Optional[logging.Logger] = None) -> None:
        super().__init__()
        self.logger = logger or logging.root



    def on_moved(self, event: FileSystemEvent) -> None:
        super().on_moved(event)
        run()

    def on_created(self, event: FileSystemEvent) -> None:
        super().on_created(event)
        run()

    def on_deleted(self, event: FileSystemEvent) -> None:
        super().on_deleted(event)
        run()

    def on_modified(self, event: FileSystemEvent) -> None:
        super().on_modified(event)
        run()

    def on_closed(self, event: FileSystemEvent) -> None:
        super().on_closed(event)
        run()

    def on_opened(self, event: FileSystemEvent) -> None:
        super().on_opened(event)
        run()


if __name__ == "__main__":
    # Set the format for logging info
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')

    # Set format for displaying path
    path = sys.argv[1] if len(sys.argv) > 1 else '.'

    # # Initialize logging event handler
    event_handler = LoggingEventHandler()

    # Initialize Observer
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)

    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
