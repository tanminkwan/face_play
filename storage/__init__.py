from storage.storage_interface import StorageInterface

def storage_client(object_storage: str) -> StorageInterface:

    if object_storage == "MINIO":
        from storage.minio import MinIO
        storage = MinIO()  # Initialize the database interface
    else:
        raise ValueError("Invalid Storage value.")

    return storage
