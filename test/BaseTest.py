from batchflows.Step import Step, RemoteStep
from batchflows.Batch import Batch
from batchflows.contextmanager.ContextManager import ABCContextManager
from batchflows.contextmanager.FileContextManager import FileContextManager
import random
import time
import subprocess

class UponCompletionContextManager(ABCContextManager):
    def __init__(self):
        super().__init__()
        self.all_is_done = True
        self.complete = False
        self.error = None
    
    def is_remote_step_done(self, name:str):
        return self.all_is_done

    def upon_completion(self, success: bool, error: str):
        self.complete = success
        self.error = error

class FakeContextManager(ABCContextManager):
    def __init__(self):
        super().__init__()
        self.all_is_done = True
    
    def is_remote_step_done(self, name:str):
        return self.all_is_done

class RemoteBatch(RemoteStep):
    def init_remote(self, _context):
        context = FileContextManager(filepath='c:\\Windows\\Temp', is_linux_os=False, is_remote_step=True, process_id='unity-test', process_name=self.name)

        batch = Batch(context_manager=context)
        batch.add_step(SaveValueStep())
        batch.execute()
        print('REMOTE BATCH IS DONE')

class MaybeRemoveStep(RemoteStep):
    
    def init_remote(self, _context):
        pass

class SubProcessStep(RemoteStep):
    def __init__(self, name: str = None, fail: bool = False):
        super().__init__(name=name, timeout=1)
        self.fail = fail

    def init_remote(self, _context):
        if self.fail:
            subprocess.call("python test/RemoteProcessFail.py", shell=True)
        else:
            subprocess.call("python test/RemoteProcessOk.py", shell=True)


class ExplosiveStep(Step):
    def __init__(self):
        super().__init__()
        self.explode = False

    def execute(self, _context):
        raise Exception('Kaboom!!!')


class SaveValueStep(Step):
    def __init__(self, name: str = None, value_name: str = 'some_value', value=1):
        super().__init__(name=name)
        self.value_name = value_name
        self.value = value

    def execute(self, _context):
        _context[self.value_name] = self.value


class SumCalculatorStep(Step):
    def __init__(self, name: str = None, attrs: tuple = ('value01', 'value02'), result_name: str = 'result'):
        super().__init__(name)
        self.attrs = attrs
        self.result_name = result_name

    def execute(self, _context):
        calc = 0.0
        for attr in self.attrs:
            calc += _context[attr]

        _context[self.result_name] = calc


class LazySumStep(SumCalculatorStep):
    def __init__(self, name: str = None, attrs: tuple = ('value01', 'value02'), result_name: str = 'result'):
        super().__init__(name, attrs, result_name)

    def execute(self, _context):
        time.sleep(random.randint(1, 3))
        super().execute(_context)