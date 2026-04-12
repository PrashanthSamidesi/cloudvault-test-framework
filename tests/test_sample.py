import pytest


def test_upload_and_download(cloud_node):
    result = cloud_node.upload_file("upload_file.txt", "Checking the upload functionality...")
    assert result["status"] == "uploaded"

    value = result["file_id"]
    download = cloud_node.download_file(value)
    assert download["filename"] == "upload_file.txt"


def test_upload_delete_download(cloud_node):
    result = cloud_node.upload_file("deletion_file.csv", "This file will be deleted.")
    assert result["status"] == "uploaded"

    value = result["file_id"]
    deleted = cloud_node.delete_file(value)
    assert deleted["status"] == "deleted"

    with pytest.raises(FileNotFoundError):
        cloud_node.download_file(value)


def test_cache_file(edge_node):
    result = edge_node.cache_file("Nasuni_Database.java", "This is a sample java file...")
    assert result["status"] == "cached"
    assert result["synced"] is False


def test_cache_count(edge_node):
    edge_node.cache_file("sample.py", "This is a sample python file")
    value = edge_node.get_pending_sync_count()
    assert value == 1


def test_sync_to_cloud(cloud_node, edge_node):
    edge_node.cache_file("Difficult_file.apk", "Should see whether it works or not")
    result = edge_node.sync_to_cloud(cloud_node)
    assert "Difficult_file.apk" in result["synced"]
    assert edge_node.get_pending_sync_count() == 0


@pytest.mark.parametrize("filename, content", [
    ("report.txt", "This is the first file"),
    ("data.csv", "name,age\nPrashanth, 23"),
    ("config.json", '{env: "Production"}'),
    ("script.py", "print('hello world')")
])
def test_multiple_files(edge_node, filename, content):
    result = edge_node.cache_file(filename, content)
    assert result["status"] == "cached"


def test_storage_manager(storage_manager):
    result = storage_manager.write_file("test.txt", "Hello world")
    assert result["sync_status"] == "success"
    assert result["cache_status"] == "cached"


def test_read_storage(storage_manager):
    storage_manager.write_file("test.txt", "Hello file")
    read_result = storage_manager.read_file(filename="test.txt")
    assert read_result["source"] == "edge_cache"


def test_node_health(storage_manager):
    result = storage_manager.get_system_health()
    assert result["cloud_node"]["status"] == "online"
    assert result["total_operations"] == 0


def test_storage_nohint(storage_manager):
    result = storage_manager.write_file("first_test.csv", "Here is my own test case")
    assert result["filename"] == "first_test.csv"


def test_storage_nohint2(storage_manager):
    storage_manager.write_file("second.txt", "Pytest")
    read_result = storage_manager.read_file("second.txt")
    assert read_result["data"]["content"] == "Pytest"


def test_edgenode_nohint(edge_node):
    edge_node.cache_file("hello.java", "What is this?")
    edge_node.simulate_failure()
    with pytest.raises(ConnectionError):
        edge_node.cache_file("hello.py", "This is a python file")


@pytest.mark.parametrize("filename, content", [
    ("text.py", "Hello Mars"),
    ("text.java", "THis is a good one"),
    ("text.exe", "Executable file")
])
def test_cloudnode_nohint(cloud_node, filename, content):
    cloud_node.upload_file(filename, content)
    result = cloud_node.list_files()
    assert len(result) == 1


@pytest.mark.parametrize("filename, content", [
    ("test.py", "I am here"),
    ("test.c", "I don't like this")
])
def test_storage_node_nohint(storage_manager, filename, content):
    storage_manager.write_file(filename, content)
    result = storage_manager.get_system_health()
    assert result["total_operations"] == 1


def test_sample(cloud_node, storage_manager, edge_node):
    result = cloud_node.upload_file("hero.java", "Learning Java")
    assert result["status"] == "uploaded"
    main = storage_manager.write_file("hero.java", "Now changing the file content")
    assert main["sync_status"] == "success"

    edge_node.simulate_failure()
    with pytest.raises(ConnectionError):
        edge_node.cache_file("hero.java", "Trying to cache during failure")
    edge_node.restore()
    result = edge_node.sync_to_cloud(cloud_node)
 