import uuid
import logging
import os
from datetime import datetime, timezone

# Create logs directory if it doesn't exist
os.makedirs("logs", exist_ok=True)

logging.basicConfig(
    filename="logs/cloudvault.log",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)

logger = logging.getLogger("CloudNode")


class CloudNode:
    """
    Simulates a cloud storage node in a distributed file system.
    Responsible for storing, retrieving, and deleting files in the cloud layer.
    """

    def __init__(self, node_id: str = "cloud-node-01"):
        self.node_id = node_id
        self.storage = {}  # Simulates cloud storage as a dictionary
        self.is_online = True
        logger.info(f"CloudNode '{self.node_id}' initialized.")

    def upload_file(self, filename: str, content: str) -> dict:
        """Upload a file to the cloud node."""
        if not self.is_online:
            logger.error(f"CloudNode '{self.node_id}' is offline. Upload failed for '{filename}'.")
            raise ConnectionError(f"CloudNode '{self.node_id}' is offline.")

        if not filename or not content:
            logger.warning(f"Invalid upload attempt — filename or content is empty.")
            raise ValueError("Filename and content cannot be empty.")

        file_id = str(uuid.uuid4())
        self.storage[file_id] = {
            "filename": filename,
            "content": content,
            "size": len(content),
            "uploaded_at": datetime.now(timezone.utc).isoformat(),
            "node": self.node_id
        }
        logger.info(f"File '{filename}' uploaded successfully. ID: {file_id}")
        return {"file_id": file_id, "status": "uploaded", "node": self.node_id}

    def download_file(self, file_id: str) -> dict:
        """Download a file from the cloud node by file ID."""
        if not self.is_online:
            logger.error(f"CloudNode '{self.node_id}' is offline. Download failed for ID '{file_id}'.")
            raise ConnectionError(f"CloudNode '{self.node_id}' is offline.")

        if file_id not in self.storage:
            logger.warning(f"File ID '{file_id}' not found in CloudNode '{self.node_id}'.")
            raise FileNotFoundError(f"File ID '{file_id}' not found.")

        file_data = self.storage[file_id]
        logger.info(f"File '{file_data['filename']}' downloaded successfully. ID: {file_id}")
        return file_data

    def delete_file(self, file_id: str) -> dict:
        """Delete a file from the cloud node."""
        if file_id not in self.storage:
            logger.warning(f"Delete failed — File ID '{file_id}' not found.")
            raise FileNotFoundError(f"File ID '{file_id}' not found.")

        filename = self.storage[file_id]["filename"]
        del self.storage[file_id]
        logger.info(f"File '{filename}' deleted successfully. ID: {file_id}")
        return {"file_id": file_id, "status": "deleted"}

    def list_files(self) -> list:
        """List all files stored in this cloud node."""
        logger.info(f"Listing all files in CloudNode '{self.node_id}'. Count: {len(self.storage)}")
        return list(self.storage.values())

    def simulate_failure(self):
        """Simulate the cloud node going offline."""
        self.is_online = False
        logger.warning(f"CloudNode '{self.node_id}' has gone OFFLINE (simulated failure).")

    def restore(self):
        """Bring the cloud node back online."""
        self.is_online = True
        logger.info(f"CloudNode '{self.node_id}' is back ONLINE.")