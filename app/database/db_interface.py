from abc import ABC, abstractmethod

# Abstract base class for database operations
class DatabaseInterface(ABC):
    @abstractmethod
    def save_face_data(self, id, photo_title, photo_id, face_index, age, gender, file_name, embedding):
        pass

    @abstractmethod
    def get_data(self, id=None, file_name=None, photo_id=None):
        pass


