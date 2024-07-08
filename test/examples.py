import unittest
import logging
import time

from batchflows.Batch import Batch
from batchflows.Step import Step, ParallelFlows, RemoteStep
from batchflows.contextmanager.FileContextManager import FileContextManager


#First extend Step class and implement method execute
class SaveValueStep(Step):
    def __init__(self, value_name, value):
        #Remember name is required if you want use remote steps
        super().__init__()
        self.value_name = value_name
        self.value = value

    # "_context" is a dict you can use to store values that will be used in other steps.
    def execute(self, _context):
        #do what u have to do here!
        _context[self.value_name] = self.value

#creating a second step just to make the explanation richer
class SumCalculatorStep(Step):
    def __init__(self, attrs):
        super().__init__()
        self.attrs = attrs

    def execute(self, _context):
        calc = 0.0
        for attr in self.attrs:
            calc += _context[attr]

        _context['sum'] = calc

class SomeStep(Step):
    def execute(self, _context):
        #count to 10 slowly
        c = 0
        while c < 10:
            c += 1
            print(c)
            time.sleep(1)

class RemoteBatchStep(RemoteStep):
    def init_remote(self, _context):
        #put some code here to init your remote batch (Like code who will deploy a pod on kubernetes)
        pass

class ExamplesTest(unittest.TestCase):

    def setUp(self):
        logging.basicConfig(level=logging.DEBUG)

    def test_example_basic (self):
        #Here we create our batch!
        batch = Batch()
        batch.add_step(SaveValueStep('value01', 1))
        batch.add_step(SaveValueStep('value02', 4))
        batch.add_step(SumCalculatorStep(['value01', 'value02', 'other_value']))

        #You can add something useful to your steps before starting bath!
        batch.context['other_value'] = 5

        #than execute your batch and be happy ;)
        batch.execute()

        logging.info(batch.context)

    def test_example_parallel (self):
        #Create your AsyncFlow
        lazy_counter = ParallelFlows('LazySteps01')
        #add steps so they run in parallel
        lazy_counter.add_step(SomeStep('lazy01'))
        lazy_counter.add_step(SomeStep('lazy02'))

        lazy_counter2 = ParallelFlows('LazySteps02')
        lazy_counter2.add_step(SomeStep('lazy03'))
        lazy_counter2.add_step(SomeStep('lazy04'))

        batch = Batch()
        batch.add_step(lazy_counter)
        batch.add_step(lazy_counter2)

        #batchfllows will wait for each step to finish before executing the next one.
        #In this example lazy_counter will be called first and execute steps "lazy01" and "lazy02" in parallel.
        #Only when both steps finish ,the batch will star lazy_counter2
        batch.execute()

    def test_remote_step (self):
        context_manager = FileContextManager(
            filepath='/tmp',
            is_remote_step=False,
            process_id='123ABC',
            process_name='batch name'
            
        )

        batch = Batch(context_manager=context_manager)
        batch.add_step(RemoteBatchStep(timeout=10))

        batch.execute()

        pass