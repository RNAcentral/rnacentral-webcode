import logging
import os

import psutil
from gunicorn.workers.sync import SyncWorker

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class CustomWorker(SyncWorker):
    def handle_exit(self, sig, frame):
        """
        Use psutil to log memory usage of each worker before it exits
        """
        process = psutil.Process(os.getpid())
        memory_info = process.memory_info()

        logger.info(
            f"Worker {os.getpid()} is exiting. Memory used: {memory_info.rss / (1024 * 1024):.2f} MB (RSS), "
            f"{memory_info.vms / (1024 * 1024):.2f} MB (VMS)"
        )

        super().handle_exit(sig, frame)
