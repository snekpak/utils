from abc import ABC, abstractmethod

class CacheProvider(ABC):
    @abstractmethod
    def add(self, k):
        pass

    @abstractmethod
    def get(self, k):
        pass

    @abstractmethod
    def upd(self, k, v):
        pass

    @abstractmethod
    def rm(self, k):
        pass

    @abstractmethod
    def pop(self, k,n=None):
        pass

    @abstractmethod
    def push(self, k):
        pass
    
    @abstractmethod
    def start():
        pass
    
    @abstractmethod
    def end():
        pass
      
      
