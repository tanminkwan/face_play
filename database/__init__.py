from database.qdrant import DatabaseInterface

def db_connection(vector_db: str) -> DatabaseInterface:

    if vector_db == "QDRANT":
        from database.qdrant import QdrantDatabase
        db = QdrantDatabase()  # Initialize the database interface
    else:
        raise ValueError("Invalid VECTOR_DB value. Please set VECTOR_DB to 'QDRANT'.")

    return db