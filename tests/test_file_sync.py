import pytest
import logging

logger = logging.getLogger("test_file_sync")


class TestFileSync:
    """
    Test suite for validating file sync behavior between EdgeNode and CloudNode.
    Covers: sync success, failure handling, cache behavior, and multi-file sync.
    """

    def test_file_cached_at_edge_before_sync(self, edge_node):
        """Verify file is cached at edge node before syncing to cloud."""
        result = edge_node.cache_file("sync_test.txt", "Sync me to cloud!")

        assert result["status"] == "cached"
        assert result["synced"] is False
        assert edge_node.get_pending_sync_count() == 1
        logger.info("test_file_cached_at_edge_before_sync PASSED")

    def test_file_syncs_successfully_to_cloud(self, edge_node, cloud_node):
        """Verify a cached file syncs successfully from edge to cloud."""
        edge_node.cache_file("synced_file.txt", "Ready for cloud!")
        result = edge_node.sync_to_cloud(cloud_node)

        assert "synced_file.txt" in result["synced"]
        assert len(result["failed"]) == 0
        assert edge_node.get_pending_sync_count() == 0
        logger.info("test_file_syncs_successfully_to_cloud PASSED")

    def test_synced_file_exists_in_cloud(self, edge_node, cloud_node):
        """Verify that after sync, the file actually exists in cloud storage."""
        edge_node.cache_file("cloud_check.txt", "Check me in cloud!")
        edge_node.sync_to_cloud(cloud_node)

        cloud_files = cloud_node.list_files()
        filenames = [f["filename"] for f in cloud_files]

        assert "cloud_check.txt" in filenames
        logger.info("test_synced_file_exists_in_cloud PASSED")

    def test_edge_cache_marked_synced_after_sync(self, edge_node, cloud_node):
        """Verify edge cache entry is marked as synced after successful sync."""
        edge_node.cache_file("mark_synced.txt", "Mark me!")
        edge_node.sync_to_cloud(cloud_node)

        cached = edge_node.get_cached_file("mark_synced.txt")
        assert cached["synced"] is True
        assert "cloud_file_id" in cached
        logger.info("test_edge_cache_marked_synced_after_sync PASSED")

    def test_sync_fails_when_cloud_is_offline(self, edge_node, cloud_node):
        """Verify sync handles cloud node failure gracefully."""
        edge_node.cache_file("fail_sync.txt", "This sync will fail.")
        cloud_node.simulate_failure()

        result = edge_node.sync_to_cloud(cloud_node)

        assert "fail_sync.txt" in result["failed"]
        assert len(result["synced"]) == 0
        assert edge_node.get_pending_sync_count() == 1
        logger.info("test_sync_fails_when_cloud_is_offline PASSED")

    def test_sync_fails_when_edge_is_offline(self, edge_node, cloud_node):
        """Verify sync raises error when edge node itself is offline."""
        edge_node.cache_file("edge_offline.txt", "Edge is going down.")
        edge_node.simulate_failure()

        with pytest.raises(ConnectionError, match="is offline"):
            edge_node.sync_to_cloud(cloud_node)

    def test_multiple_files_sync_together(self, edge_node, cloud_node):
        """Verify multiple files cached at edge all sync to cloud correctly."""
        files = [
            ("file_a.txt", "Content A"),
            ("file_b.txt", "Content B"),
            ("file_c.txt", "Content C"),
        ]
        for filename, content in files:
            edge_node.cache_file(filename, content)

        assert edge_node.get_pending_sync_count() == 3
        result = edge_node.sync_to_cloud(cloud_node)

        assert len(result["synced"]) == 3
        assert len(result["failed"]) == 0
        assert edge_node.get_pending_sync_count() == 0
        logger.info("test_multiple_files_sync_together PASSED")

    def test_cache_miss_raises_file_not_found(self, edge_node):
        """Verify retrieving a non-existent file from cache raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError, match="not found in edge cache"):
            edge_node.get_cached_file("ghost_file.txt")

    def test_caching_while_edge_offline_raises_error(self, edge_node):
        """Verify caching fails gracefully when edge node is offline."""
        edge_node.simulate_failure()

        with pytest.raises(ConnectionError, match="is offline"):
            edge_node.cache_file("wont_cache.txt", "Edge is offline!")

    def test_edge_recovers_and_syncs_after_failure(self, edge_node, cloud_node):
        """Verify edge node can cache and sync again after being restored."""
        edge_node.cache_file("before_failure.txt", "Cached before failure.")
        edge_node.simulate_failure()
        edge_node.restore()

        edge_node.cache_file("after_recovery.txt", "Cached after recovery.")
        result = edge_node.sync_to_cloud(cloud_node)

        assert "after_recovery.txt" in result["synced"]
        logger.info("test_edge_recovers_and_syncs_after_failure PASSED")

    @pytest.mark.parametrize("filename,content", [
        ("sync_txt.txt", "plain text"),
        ("sync_csv.csv", "id,name\n1,test"),
        ("sync_json.json", '{"synced": true}'),
        ("sync_large.txt", "y" * 20000),
    ])
    def test_sync_various_file_types(self, edge_node, cloud_node, filename, content):
        """Verify different file types sync correctly from edge to cloud."""
        edge_node.cache_file(filename, content)
        result = edge_node.sync_to_cloud(cloud_node)

        assert filename in result["synced"]
        logger.info(f"Parameterized sync test passed for: {filename}")