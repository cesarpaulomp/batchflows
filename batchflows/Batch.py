from batchflows.contextmanager.ContextManager import ABCContextManager
from batchflows.Step import _Step
from abc import ABC, abstractmethod
import logging
import uuid

class Batch:
    def __init__(self, name: str = None, context_manager: ABCContextManager = None, after = None):
        self.context_manager = context_manager if context_manager else ABCContextManager()
        self.__name = name if name else str(uuid.uuid4())
        self.after = after

    @property
    def name(self):
        return self.__name

    @property
    def context(self):
        return self.context_manager.context

    def add_step(self, flow: _Step):
        self.context_manager.steps.append(flow)

    def execute(self):
        logging.debug(f"batch_id: {self.__name} is running")
        success = False
        error = None

        for step in self.context_manager.steps:
            try:
                step.start(self.context_manager)
                success = True
            except Exception as unspected:
                error = str(unspected)
                raise unspected
            finally:
                self.context_manager.upon_completion(success=success, error=error)
                if self.after:
                    self.after()

        logging.debug(f"batch_id: {self.__name} is done")
