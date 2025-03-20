from abc import ABC, abstractmethod

# Abstract base class for database operations
class DatabaseInterface(ABC):
    @abstractmethod
    def save_face_data(self, id, photo_title, photo_id, face_index, age, gender, file_name, embedding):
        pass

    @abstractmethod
    def save_special_face_data(self, id, age, num_people, last_processed_at, embedding):
        pass

    @abstractmethod
    def save_face_data_batch(self, face_data_list):
        pass

    @abstractmethod
    def get_data(self, file_name=None, photo_id=None, with_vectors=False):
        pass

    @abstractmethod
    def get_data_by_id(self, id, with_vectors=False):
        pass

    @abstractmethod
    def get_data_after_date_sorted(self, date_str: str):
        pass