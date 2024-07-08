from batchflows.util.CustomExceptions import ParallelFlowsException
from batchflows.threading.CatchThread import CatchThread
from batchflows.contextmanager.ContextManager import ABCContextManager
from abc import ABC, abstractmethod
import logging
import uuid
import time


class _Step(ABC):
    def __init__(self, name: str = None):
        self._name = name if name else str(uuid.uuid4())

    @property
    def name(self):
        return self._name

    @abstractmethod
    def start(self, context_manager: ABCContextManager):
        pass


class Step(_Step):

    @abstractmethod
    def execute(self, _context):
        pass

    def start(self, context_manager: ABCContextManager):
        logging.debug(f'{self.name} is running')
        self.execute(context_manager.context)
        logging.debug(f'{self.name} is done')


class ParallelFlows(_Step):
    def __init__(self, name: str = None):
        super().__init__(name)
        self.__steps = []

    def add_step(self, step: Step):
        self.__steps.append(step)

    @property
    def steps(self):
        return self.__steps

    def _run_steps(self, context_manager: ABCContextManager):
        t_list = []
        error_list = []

        for step in self.__steps:
            trd = CatchThread(target=lambda: step.start(context_manager), name=step.name)
            trd.start()
            t_list.append(trd)

        for trd in t_list:
            trd.join()

            if trd.has_error():
                error_list.append(trd.get_error_if_exists())

        if error_list:
            raise ParallelFlowsException(self.name, error_list)

    def start(self, context_manager: ABCContextManager):
        logging.debug(f'{self.name} is running')
        self._run_steps(context_manager)
        logging.debug(f'{self.name} is done')


class RemoteStep(_Step):
    def __init__(self, name: str = None, timeout: float = 2):
        super().__init__(name)
        self.__steps = []
        self._timeout = timeout

    @abstractmethod
    def init_remote(self, _context):
        pass

    def start(self, context_manager: ABCContextManager):
        logging.debug(f'{self.name} is running')
        self.init_remote(context_manager.context)
        
        time.process_time()
        starttime = time.time()
        elapsed = 0

        while not context_manager.is_remote_step_done(name=self.name):
            logging.debug(f'current time: {elapsed}')
            if elapsed > self._timeout:
                logging.debug(f'{self.name} raise timeout error. Step exceeded {self._timeout} second(s)')
                raise TimeoutError(f'{self.name} raise timeout error. Step exceeded {self._timeout} second(s)')
            
            elapsed = time.time() - starttime
            time.sleep(.150)

        logging.debug(f'{self.name} is done')
