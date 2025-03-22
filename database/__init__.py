from database.qdrant import DatabaseInterface

def db_connection(vector_db: str, host=None, port=None) -> DatabaseInterface:

    if vector_db == "QDRANT":
        from database.qdrant import QdrantDatabase
        db = QdrantDatabase(host=host, port=port, collection_name="face_embeddings")  # Initialize the database interface
    else:
        raise ValueError("Invalid VECTOR_DB value. Please set VECTOR_DB to 'QDRANT'.")

    return db