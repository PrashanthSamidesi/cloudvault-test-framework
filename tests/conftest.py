import pytest
import logging
from services.cloud_node import CloudNode
from services.edge_node import EdgeNode
from services.storage_manager import StorageManager

logger = logging.getLogger("conftest")


# ──────────────────────────────────────────────
# FIXTURES — Reusable setup blocks for all tests
# ──────────────────────────────────────────────

@pytest.fixture(scope="function")
def cloud_node():
    """
    Provides a fresh CloudNode for each test.
    scope="function" means this resets before every single test.
    """
    logger.info("Setting up CloudNode fixture.")
    node = CloudNode(node_id="cloud-node-test")
    yield node
    # Teardown — runs after each test automatically
    logger.info("Tearing down CloudNode fixture.")
    node.storage.clear()


@pytest.fixture(scope="function")
def edge_node():
    """
    Provides a fresh EdgeNode for each test.
    """
    logger.info("Setting up EdgeNode fixture.")
    node = EdgeNode(node_id="edge-node-test")
    yield node
    logger.info("Tearing down EdgeNode fixture.")
    node.cache.clear()
    node.sync_queue.clear()


@pytest.fixture(scope="function")
def storage_manager(cloud_node, edge_node):
    """
    Provides a fully wired StorageManager with cloud + edge nodes.
    This simulates the complete distributed system for integration tests.
    """
    logger.info("Setting up StorageManager fixture.")
    manager = StorageManager(cloud_node=cloud_node, edge_nodes=[edge_node])
    yield manager
    logger.info("Tearing down StorageManager fixture.")


@pytest.fixture(scope="function")
def uploaded_file(cloud_node):
    """
    Pre-uploads a file to the cloud node and returns its metadata.
    Used by tests that need an existing file to work with.
    """
    result = cloud_node.upload_file("test_file.txt", "Hello from CloudVault!")
    logger.info(f"Pre-uploaded test file. ID: {result['file_id']}")
    return result


@pytest.fixture(scope="session")
def sample_files():
    """
    Provides a list of sample file data for parameterized tests.
    scope="session" means this is created once for the entire test run.
    """
    return [
        {"filename": "document.txt", "content": "This is a text document."},
        {"filename": "report.csv", "content": "col1,col2,col3\n1,2,3"},
        {"filename": "config.json", "content": '{"key": "value", "active": true}'},
        {"filename": "image_meta.xml", "content": "<image><width>1920</width></image>"},
        {"filename": "large_file.txt", "content": "x" * 10000},
    ]