import pytest
import logging

logger = logging.getLogger("test_integration")


class TestIntegration:
    """
    End-to-end integration test suite for the CloudVault distributed system.
    Validates cross-component behaviors through the StorageManager orchestrator.
    """

    def test_full_write_cycle_edge_to_cloud(self, storage_manager, edge_node):
        """
        Validate complete write path:
        Client → EdgeNode (cache) → CloudNode (sync) → Verified in cloud.
        """
        result = storage_manager.write_file(
            filename="integration_write.txt",
            content="Full write cycle test.",
            edge_node_id="edge-node-test"
        )

        assert result["operation"] == "write"
        assert result["cache_status"] == "cached"
        assert result["sync_status"] == "success"
        logger.info("test_full_write_cycle_edge_to_cloud PASSED")

    def test_full_read_cycle_cache_hit(self, storage_manager, edge_node):
        """
        Validate read path when file exists in edge cache.
        System should return from cache without hitting cloud (cache HIT).
        """
        storage_manager.write_file(
            filename="cache_hit.txt",
            content="Read me from cache!",
            edge_node_id="edge-node-test"
        )
        result = storage_manager.read_file(
            filename="cache_hit.txt",
            edge_node_id="edge-node-test"
        )

        assert result["source"] == "edge_cache"
        assert result["data"]["content"] == "Read me from cache!"
        logger.info("test_full_read_cycle_cache_hit PASSED")

    def test_full_read_cycle_cache_miss_fallback_to_cloud(
        self, storage_manager, cloud_node
    ):
        """
        Validate read fallback path:
        Cache MISS at edge → System falls back to CloudNode.
        """
        upload = cloud_node.upload_file("cloud_only.txt", "Only in cloud!")
        result = storage_manager.read_file(
            filename="cloud_only.txt",
            file_id=upload["file_id"]
        )

        assert result["source"] == "cloud"
        assert result["data"]["content"] == "Only in cloud!"
        logger.info("test_full_read_cycle_cache_miss_fallback_to_cloud PASSED")

    def test_system_health_all_nodes_online(self, storage_manager):
        """
        Validate system health check reports all nodes as online
        in a healthy distributed environment.
        """
        health = storage_manager.get_system_health()

        assert health["cloud_node"]["status"] == "online"
        assert all(
            e["status"] == "online" for e in health["edge_nodes"]
        ), "All edge nodes should be online"
        logger.info("test_system_health_all_nodes_online PASSED")

    def test_system_health_reflects_cloud_failure(self, storage_manager, cloud_node):
        """
        Validate system health check correctly reflects cloud node failure.
        Critical for monitoring and alerting in distributed systems.
        """
        cloud_node.simulate_failure()
        health = storage_manager.get_system_health()

        assert health["cloud_node"]["status"] == "offline"
        logger.info("test_system_health_reflects_cloud_failure PASSED")

    def test_system_health_reflects_edge_failure(self, storage_manager, edge_node):
        """
        Validate system health check correctly reflects edge node failure.
        """
        edge_node.simulate_failure()
        health = storage_manager.get_system_health()

        edge_statuses = [e["status"] for e in health["edge_nodes"]]
        assert "offline" in edge_statuses
        logger.info("test_system_health_reflects_edge_failure PASSED")

    def test_write_falls_back_to_direct_cloud_when_no_edge(
        self, cloud_node
    ):
        """
        Validate that StorageManager writes directly to cloud
        when no edge nodes are registered — graceful degradation.
        """
        from services.storage_manager import StorageManager
        manager = StorageManager(cloud_node=cloud_node, edge_nodes=[])

        result = manager.write_file("direct_cloud.txt", "No edge available!")

        assert result["sync_status"] == "direct_upload"
        assert result["edge_node"] is None
        assert "file_id" in result
        logger.info("test_write_falls_back_to_direct_cloud_when_no_edge PASSED")

    def test_operation_history_tracks_writes(self, storage_manager):
        """
        Validate that StorageManager tracks all write operations
        in its operation history for audit and debugging.
        """
        storage_manager.write_file("track1.txt", "First write.")
        storage_manager.write_file("track2.txt", "Second write.")
        storage_manager.write_file("track3.txt", "Third write.")

        health = storage_manager.get_system_health()
        assert health["total_operations"] == 3
        logger.info("test_operation_history_tracks_writes PASSED")

    def test_cloud_node_file_count_increases_after_writes(
        self, storage_manager, cloud_node
    ):
        """
        Validate cloud storage grows correctly with each write operation.
        """
        initial_count = len(cloud_node.storage)

        storage_manager.write_file("count1.txt", "File 1")
        storage_manager.write_file("count2.txt", "File 2")

        assert len(cloud_node.storage) == initial_count + 2
        logger.info("test_cloud_node_file_count_increases_after_writes PASSED")

    def test_read_nonexistent_file_raises_error(self, storage_manager):
        """
        Validate that reading a file that doesn't exist anywhere
        raises FileNotFoundError — no silent failures.
        """
        with pytest.raises(FileNotFoundError):
            storage_manager.read_file(
                filename="ghost.txt",
                edge_node_id="edge-node-test"
            )

    def test_multiple_edge_nodes_registered(self, cloud_node):
        """
        Validate StorageManager correctly handles multiple edge nodes —
        simulating a real multi-site distributed deployment.
        """
        from services.storage_manager import StorageManager
        from services.edge_node import EdgeNode

        edge1 = EdgeNode("edge-site-A")
        edge2 = EdgeNode("edge-site-B")
        edge3 = EdgeNode("edge-site-C")

        manager = StorageManager(
            cloud_node=cloud_node,
            edge_nodes=[edge1, edge2, edge3]
        )
        health = manager.get_system_health()

        assert len(health["edge_nodes"]) == 3
        assert all(e["status"] == "online" for e in health["edge_nodes"])
        logger.info("test_multiple_edge_nodes_registered PASSED")

    @pytest.mark.parametrize("filename,content", [
        ("int_doc.txt", "Integration document"),
        ("int_data.csv", "x,y,z\n1,2,3"),
        ("int_config.json", '{"distributed": true}'),
    ])
    def test_write_read_cycle_various_file_types(
        self, storage_manager, filename, content
    ):
        """
        Validate complete write → read cycle works for various file types
        across the distributed system.
        """
        storage_manager.write_file(
            filename=filename,
            content=content,
            edge_node_id="edge-node-test"
        )
        result = storage_manager.read_file(
            filename=filename,
            edge_node_id="edge-node-test"
        )

        assert result["data"]["content"] == content
        assert result["source"] == "edge_cache"
        logger.info(f"Write-read cycle passed for: {filename}")
