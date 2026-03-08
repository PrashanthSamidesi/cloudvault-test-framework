import pytest
import logging

logger = logging.getLogger("test_regression")


class TestRegression:
    """
    Regression test suite for CloudVault distributed file system.
    Ensures previously validated behaviors remain stable across code changes.
    Each test here represents a real bug scenario that must never regress.
    """

    # ──────────────────────────────────────────
    # REG-001: Cloud Node Core Behaviors
    # ──────────────────────────────────────────

    def test_reg001_upload_returns_file_id(self, cloud_node):
        """
        REG-001: Verify upload always returns a valid file_id.
        Regression guard: file_id must never be None or empty.
        """
        result = cloud_node.upload_file("reg001.txt", "Regression content.")
        assert result.get("file_id") is not None
        assert len(result["file_id"]) > 0
        logger.info("REG-001 PASSED")

    def test_reg002_download_returns_correct_content(self, cloud_node):
        """
        REG-002: Verify downloaded content exactly matches uploaded content.
        Regression guard: content must never be corrupted or truncated.
        """
        original_content = "Exact content integrity check — REG-002"
        result = cloud_node.upload_file("reg002.txt", original_content)
        downloaded = cloud_node.download_file(result["file_id"])

        assert downloaded["content"] == original_content
        logger.info("REG-002 PASSED")

    def test_reg003_delete_removes_file_from_storage(self, cloud_node):
        """
        REG-003: Verify deleted files are completely removed from storage.
        Regression guard: deleted files must never linger in storage.
        """
        result = cloud_node.upload_file("reg003.txt", "Delete me.")
        file_id = result["file_id"]
        cloud_node.delete_file(file_id)

        assert file_id not in cloud_node.storage
        logger.info("REG-003 PASSED")

    def test_reg004_download_deleted_file_raises_error(self, cloud_node):
        """
        REG-004: Verify downloading a deleted file raises FileNotFoundError.
        Regression guard: no ghost file access after deletion.
        """
        result = cloud_node.upload_file("reg004.txt", "Soon to be deleted.")
        file_id = result["file_id"]
        cloud_node.delete_file(file_id)

        with pytest.raises(FileNotFoundError):
            cloud_node.download_file(file_id)
        logger.info("REG-004 PASSED")

    def test_reg005_offline_node_rejects_downloads(self, cloud_node):
        """
        REG-005: Verify offline cloud node rejects download attempts.
        Regression guard: offline nodes must never serve stale data.
        """
        result = cloud_node.upload_file("reg005.txt", "Offline test.")
        file_id = result["file_id"]
        cloud_node.simulate_failure()

        with pytest.raises(ConnectionError):
            cloud_node.download_file(file_id)
        logger.info("REG-005 PASSED")

    # ──────────────────────────────────────────
    # REG-006: Edge Node Core Behaviors
    # ──────────────────────────────────────────

    def test_reg006_pending_sync_count_accurate(self, edge_node):
        """
        REG-006: Verify pending sync count is always accurate.
        Regression guard: sync queue must never miscount.
        """
        assert edge_node.get_pending_sync_count() == 0
        edge_node.cache_file("reg006a.txt", "File A")
        assert edge_node.get_pending_sync_count() == 1
        edge_node.cache_file("reg006b.txt", "File B")
        assert edge_node.get_pending_sync_count() == 2
        logger.info("REG-006 PASSED")

    def test_reg007_sync_clears_pending_queue(self, edge_node, cloud_node):
        """
        REG-007: Verify sync queue is fully cleared after successful sync.
        Regression guard: synced files must never remain in pending queue.
        """
        edge_node.cache_file("reg007a.txt", "Sync A")
        edge_node.cache_file("reg007b.txt", "Sync B")
        edge_node.sync_to_cloud(cloud_node)

        assert edge_node.get_pending_sync_count() == 0
        logger.info("REG-007 PASSED")

    def test_reg008_failed_sync_keeps_files_in_queue(self, edge_node, cloud_node):
        """
        REG-008: Verify failed syncs keep files in the pending queue.
        Regression guard: failed files must stay queued for retry.
        """
        edge_node.cache_file("reg008.txt", "Will fail to sync.")
        cloud_node.simulate_failure()
        edge_node.sync_to_cloud(cloud_node)

        assert edge_node.get_pending_sync_count() == 1
        logger.info("REG-008 PASSED")

    # ──────────────────────────────────────────
    # REG-009: StorageManager Core Behaviors
    # ──────────────────────────────────────────

    def test_reg009_write_operation_logged_in_history(self, storage_manager):
        """
        REG-009: Verify every write is tracked in operation history.
        Regression guard: audit trail must never drop operations.
        """
        storage_manager.write_file("reg009.txt", "Track this write.")
        assert len(storage_manager.operation_history) == 1
        assert storage_manager.operation_history[0]["filename"] == "reg009.txt"
        logger.info("REG-009 PASSED")

    def test_reg010_system_health_always_returns_all_nodes(self, storage_manager):
        """
        REG-010: Verify system health always reports all registered nodes.
        Regression guard: health check must never omit nodes.
        """
        health = storage_manager.get_system_health()

        assert "cloud_node" in health
        assert "edge_nodes" in health
        assert isinstance(health["edge_nodes"], list)
        logger.info("REG-010 PASSED")

    def test_reg011_node_restore_re_enables_uploads(self, cloud_node):
        """
        REG-011: Verify restored node accepts uploads again.
        Regression guard: restore() must fully re-enable node operations.
        """
        cloud_node.simulate_failure()
        cloud_node.restore()

        result = cloud_node.upload_file("reg011.txt", "Post restore upload.")
        assert result["status"] == "uploaded"
        logger.info("REG-011 PASSED")

    def test_reg012_large_file_upload_and_download_integrity(self, cloud_node):
        """
        REG-012: Verify large file content integrity across upload and download.
        Regression guard: large files must never be corrupted or truncated.
        """
        large_content = "NASUNI_DISTRIBUTED_SYSTEM_" * 5000  # ~130KB
        result = cloud_node.upload_file("reg012_large.txt", large_content)
        downloaded = cloud_node.download_file(result["file_id"])

        assert downloaded["content"] == large_content
        assert downloaded["size"] == len(large_content)
        logger.info("REG-012 PASSED")

    def test_reg013_list_files_reflects_current_state(self, cloud_node):
        """
        REG-013: Verify list_files always reflects current storage state.
        Regression guard: file listing must always be accurate after mutations.
        """
        cloud_node.upload_file("reg013a.txt", "File A")
        cloud_node.upload_file("reg013b.txt", "File B")
        result_upload = cloud_node.upload_file("reg013c.txt", "File C")

        files = cloud_node.list_files()
        assert len(files) == 3

        cloud_node.delete_file(result_upload["file_id"])
        files_after_delete = cloud_node.list_files()
        assert len(files_after_delete) == 2
        logger.info("REG-013 PASSED")
