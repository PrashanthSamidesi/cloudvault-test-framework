import pytest
import logging

logger = logging.getLogger("test_file_upload")


class TestFileUpload:
    """
    Test suite for validating file upload behavior on the CloudNode.
    Covers: happy paths, edge cases, and failure scenarios.
    """

    def test_upload_single_file_success(self, cloud_node):
        """Verify a valid file uploads successfully and returns correct metadata."""
        result = cloud_node.upload_file("hello.txt", "Hello, Nasuni!")

        assert result["status"] == "uploaded", "Upload status should be 'uploaded'"
        assert "file_id" in result, "Response must contain a file_id"
        assert result["node"] == "cloud-node-test", "Node ID should match"
        logger.info("test_upload_single_file_success PASSED")

    def test_uploaded_file_exists_in_storage(self, cloud_node):
        """Verify the file is actually stored after upload."""
        result = cloud_node.upload_file("stored.txt", "Store this content.")
        file_id = result["file_id"]

        assert file_id in cloud_node.storage, "File ID must exist in cloud storage"
        assert cloud_node.storage[file_id]["filename"] == "stored.txt"
        assert cloud_node.storage[file_id]["content"] == "Store this content."

    def test_upload_empty_filename_raises_error(self, cloud_node):
        """Verify that uploading with an empty filename raises ValueError."""
        with pytest.raises(ValueError, match="Filename and content cannot be empty"):
            cloud_node.upload_file("", "Some content")

    def test_upload_empty_content_raises_error(self, cloud_node):
        """Verify that uploading with empty content raises ValueError."""
        with pytest.raises(ValueError, match="Filename and content cannot be empty"):
            cloud_node.upload_file("file.txt", "")

    def test_upload_while_node_offline_raises_error(self, cloud_node):
        """Verify that upload fails gracefully when cloud node is offline."""
        cloud_node.simulate_failure()

        with pytest.raises(ConnectionError, match="is offline"):
            cloud_node.upload_file("offline_test.txt", "This should fail.")

    def test_node_recovers_after_failure(self, cloud_node):
        """Verify that the cloud node can upload again after being restored."""
        cloud_node.simulate_failure()
        cloud_node.restore()

        result = cloud_node.upload_file("recovered.txt", "Back online!")
        assert result["status"] == "uploaded", "Node should upload successfully after restore"

    def test_multiple_files_get_unique_ids(self, cloud_node):
        """Verify each uploaded file receives a unique file ID."""
        result1 = cloud_node.upload_file("file1.txt", "Content 1")
        result2 = cloud_node.upload_file("file2.txt", "Content 2")
        result3 = cloud_node.upload_file("file3.txt", "Content 3")

        ids = [result1["file_id"], result2["file_id"], result3["file_id"]]
        assert len(set(ids)) == 3, "All file IDs must be unique"

    @pytest.mark.parametrize("filename,content", [
        ("doc.txt", "Simple text"),
        ("data.csv", "a,b,c\n1,2,3"),
        ("config.json", '{"env": "test"}'),
        ("large.txt", "x" * 50000),
        ("unicode.txt", "Héllo Wörld — Distributed Systems"),
    ])
    def test_upload_various_file_types(self, cloud_node, filename, content):
        """Verify different file types and content sizes upload correctly."""
        result = cloud_node.upload_file(filename, content)
        assert result["status"] == "uploaded"
        assert "file_id" in result
        logger.info(f"Parameterized upload test passed for: {filename}")
