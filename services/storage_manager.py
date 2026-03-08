import logging
import os
from datetime import datetime, timezone

os.makedirs("logs", exist_ok=True)

logging.basicConfig(
    filename="logs/cloudvault.log",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)

logger = logging.getLogger("StorageManager")


class StorageManager:
    """
    Orchestrates file operations across cloud and edge nodes.
    Acts as the central coordinator of the distributed file system.
    """

    def __init__(self, cloud_node, edge_nodes: list = None):
        self.cloud_node = cloud_node
        self.edge_nodes = edge_nodes or []
        self.operation_history = []
        logger.info(f"StorageManager initialized with {len(self.edge_nodes)} edge node(s).")

    def add_edge_node(self, edge_node):
        """Register a new edge node with the storage manager."""
        self.edge_nodes.append(edge_node)
        logger.info(f"EdgeNode '{edge_node.node_id}' registered with StorageManager.")

    def write_file(self, filename: str, content: str, edge_node_id: str = None) -> dict:
        """
        Write a file — caches at edge first, then syncs to cloud.
        This is the core distributed write operation.
        """
        target_edge = self._get_edge_node(edge_node_id)

        if target_edge:
            cache_result = target_edge.cache_file(filename, content)
            sync_result = target_edge.sync_to_cloud(self.cloud_node)
            operation = {
                "operation": "write",
                "filename": filename,
                "edge_node": target_edge.node_id,
                "cache_status": cache_result["status"],
                "sync_status": "success" if filename in sync_result["synced"] else "failed",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        else:
            # Direct cloud write if no edge node available
            upload_result = self.cloud_node.upload_file(filename, content)
            operation = {
                "operation": "write",
                "filename": filename,
                "edge_node": None,
                "cache_status": "skipped",
                "sync_status": "direct_upload",
                "file_id": upload_result["file_id"],
                "timestamp": datetime.now(timezone.utc).isoformat()
            }

        self.operation_history.append(operation)
        logger.info(f"Write operation completed for '{filename}': {operation['sync_status']}")
        return operation

    def read_file(self, filename: str, file_id: str = None, edge_node_id: str = None) -> dict:
        """
        Read a file — checks edge cache first, falls back to cloud.
        This is the core distributed read operation.
        """
        target_edge = self._get_edge_node(edge_node_id)

        # Try edge cache first
        if target_edge:
            try:
                file_data = target_edge.get_cached_file(filename)
                logger.info(f"Cache HIT for '{filename}' at EdgeNode '{target_edge.node_id}'.")
                return {"source": "edge_cache", "data": file_data}
            except FileNotFoundError:
                logger.info(f"Cache MISS for '{filename}'. Falling back to cloud.")

        # Fall back to cloud
        if file_id:
            file_data = self.cloud_node.download_file(file_id)
            return {"source": "cloud", "data": file_data}

        raise FileNotFoundError(f"File '{filename}' not found in edge cache or cloud.")

    def get_system_health(self) -> dict:
        """Returns health status of all nodes in the system."""
        health = {
            "cloud_node": {
                "node_id": self.cloud_node.node_id,
                "status": "online" if self.cloud_node.is_online else "offline",
                "file_count": len(self.cloud_node.storage)
            },
            "edge_nodes": [
                {
                    "node_id": e.node_id,
                    "status": "online" if e.is_online else "offline",
                    "cached_files": len(e.cache),
                    "pending_sync": e.get_pending_sync_count()
                }
                for e in self.edge_nodes
            ],
            "total_operations": len(self.operation_history)
        }
        logger.info(f"System health check performed. Cloud: {health['cloud_node']['status']}")
        return health

    def _get_edge_node(self, edge_node_id: str = None):
        """Internal helper to find an edge node by ID."""
        if not self.edge_nodes:
            return None
        if edge_node_id:
            for node in self.edge_nodes:
                if node.node_id == edge_node_id:
                    return node
        return self.edge_nodes[0]
