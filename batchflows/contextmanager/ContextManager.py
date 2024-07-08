from abc import ABC, abstractmethod

class ABCContextManager(ABC):
    def __init__(self):
        self.context = dict()
        self.steps = []

    def is_remote_step_done(self, name: str):
        raise NotImplementedError()

    def upon_completion(self, success: bool, error: str = None):
        pass
