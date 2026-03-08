import logging
import os
from datetime import datetime

os.makedirs("logs", exist_ok=True)

logging.basicConfig(
    filename="logs/cloudvault.log",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)

logger = logging.getLogger("EdgeNode")


class EdgeNode:
    """
    Simulates an edge node in a distributed file system.
    Acts as a local cache layer that syncs with the cloud node.
    """

    def __init__(self, node_id: str = "edge-node-01"):
        self.node_id = node_id
        self.cache = {}         # Local file cache
        self.sync_queue = []    # Files waiting to be synced to cloud
        self.is_online = True
        logger.info(f"EdgeNode '{self.node_id}' initialized.")

    def cache_file(self, filename: str, content: str) -> dict:
        """Cache a file locally at the edge node."""
        if not self.is_online:
            logger.error(f"EdgeNode '{self.node_id}' is offline. Caching failed for '{filename}'.")
            raise ConnectionError(f"EdgeNode '{self.node_id}' is offline.")

        if not filename or not content:
            raise ValueError("Filename and content cannot be empty.")

        self.cache[filename] = {
            "filename": filename,
            "content": content,
            "size": len(content),
            "cached_at": datetime.utcnow().isoformat(),
            "synced": False
        }
        self.sync_queue.append(filename)
        logger.info(f"File '{filename}' cached at EdgeNode '{self.node_id}'. Pending sync.")
        return {"filename": filename, "status": "cached", "synced": False}

    def sync_to_cloud(self, cloud_node) -> list:
        """Sync all pending files from edge cache to cloud node."""
        if not self.is_online:
            logger.error(f"EdgeNode '{self.node_id}' is offline. Sync aborted.")
            raise ConnectionError(f"EdgeNode '{self.node_id}' is offline.")

        synced_files = []
        failed_files = []

        for filename in list(self.sync_queue):
            try:
                file_data = self.cache[filename]
                result = cloud_node.upload_file(filename, file_data["content"])
                self.cache[filename]["synced"] = True
                self.cache[filename]["cloud_file_id"] = result["file_id"]
                self.sync_queue.remove(filename)
                synced_files.append(filename)
                logger.info(f"File '{filename}' synced from EdgeNode to CloudNode. Cloud ID: {result['file_id']}")
            except Exception as e:
                failed_files.append(filename)
                logger.error(f"Sync failed for '{filename}': {str(e)}")

        return {"synced": synced_files, "failed": failed_files}

    def get_cached_file(self, filename: str) -> dict:
        """Retrieve a file from the edge cache."""
        if filename not in self.cache:
            logger.warning(f"File '{filename}' not found in EdgeNode cache.")
            raise FileNotFoundError(f"File '{filename}' not found in edge cache.")
        return self.cache[filename]

    def get_pending_sync_count(self) -> int:
        """Returns number of files waiting to sync to cloud."""
        return len(self.sync_queue)

    def simulate_failure(self):
        """Simulate the edge node going offline."""
        self.is_online = False
        logger.warning(f"EdgeNode '{self.node_id}' has gone OFFLINE (simulated failure).")

    def restore(self):
        """Bring the edge node back online."""
        self.is_online = True
        logger.info(f"EdgeNode '{self.node_id}' is back ONLINE.")