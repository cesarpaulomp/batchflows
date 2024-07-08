# Batchflows for Python 3

This tool will help you create and process a lot of data in an organized manner.
You can create batches of processing synchronously and asynchronously.

*remember it's in BETA :D*

### Get Started

```python
import logging

from batchflows.Batch import Batch
from batchflows.Step import Step

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
```

### Let's try run some parallel code

```python
import logging
import time

from batchflows.Batch import Batch
from batchflows.Step import Step, ParallelFlows


class SomeStep(Step):
    def execute(self, _context):
        #count to 10 slowly
        c = 0
        while c < 10:
            c += 1
            print(c)
            time.sleep(1)

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
```
### FileContextmanager and RemoteStep

You can extend RemoteStep class and make your code to run a remote batch.
Unfortunately the basic context does not allow remote steps to be performed without customization.
To solve this problem we have FileContextManager

# let's start by creating our main batch

```python
context_manager = FileContextManager(
    filepath='/tmp', #where u set where you want batch create status file
                     #you can put a disc that all your machines share
    is_remote_step=False, #default false. You saying here this is the main batch
    process_id='123ABC', #default random uuid. You can specify an id for the process. 
                         #This field is important for remote batches to be able to write the status file correctly.
    process_name='batch name' #default random uuid. For the main batch this field has no importance, but for your remote batch
                              #you need put the same name of remote-step
    )

batch = Batch(context_manager=context_manager)
batch.add_step(RemoteBatchStep(
                name='do-a-barrel-roll',
                timeout=10 #in seconds
            ))

batch.execute()
```

# now let's create our remote batch

```python
context_manager = FileContextManager(
    filepath='/tmp',
    is_remote_step=True,
    process_id='123ABC', #exactly the same a main batch
    process_name='do-a-barrel-roll'#exactly the same name as step
    )

batch = Batch(context_manager=context_manager)
batch.add_step(...) # lot of cool things
batch.add_step(...) # lot of cool things
batch.add_step(...) # lot of cool things

batch.execute()
```

### customize your ContextManager
You can also extend the ContextManager class and create your way to run remote code.

```python
class MyContextManager(ABCContextManager):
    def __init__(self):
        self.context = dict()
        self.steps = []

    #override this method to teach your customization how to identify if remote execution is ready
    def is_remote_step_done(self, name: str):
        raise NotImplementedError()
    
    #override this method if you want to execute some code after batch conclude
    def upon_completion(self, success: bool, error: str = None):
        pass
```
