import logging
import unittest

from batchflows.Batch import Batch
from batchflows.Step import ParallelFlows
from batchflows.util.CustomExceptions import ParallelFlowsException
from batchflows.contextmanager.ContextManager import ABCContextManager
from test.BaseTest import SaveValueStep, SumCalculatorStep, LazySumStep, ExplosiveStep


class ParallelStepTest(unittest.TestCase):

    def setUp(self) -> None:
        logging.basicConfig(level=logging.DEBUG)

    def test_parallel_lazy(self):
        batch = Batch()

        flow = ParallelFlows(name='Parallel')
        flow.add_step(SaveValueStep(value_name='value01'))
        flow.add_step(SaveValueStep(value_name='value02', value=4))

        batch.add_step(flow)
        batch.add_step(LazySumStep())
        batch.execute()

        self.assertEqual(5, batch.context['result'])

    def test_parallel(self):
        context = ABCContextManager()

        flow = ParallelFlows(name='Parallel add values')
        flow.add_step(SaveValueStep(value_name='value01'))
        flow.add_step(SaveValueStep(value_name='value02', value=4))

        flow.start(context)
        print(context)
        self.assertEqual(1, context.context['value01'])
        self.assertEqual(4, context.context['value02'])

    def test_parallel_expected_error(self):
        flow = ParallelFlows(name='Parallel explosion')
        flow.add_step(ExplosiveStep())

        expected = None

        try:
            flow.start(ABCContextManager())
        except ParallelFlowsException as error:
            expected = True

        self.assertTrue(expected)