from abc import ABC, abstractmethod

class StoreProvider(ABC):
    @abstractmethod
    def add(self, obj):
        pass

    @abstractmethod
    def get(self, obj_id):
        pass

    @abstractmethod
    def update(self, obj_id, **kwargs):
        pass

    @abstractmethod
    def delete(self, obj_id):
        pass
