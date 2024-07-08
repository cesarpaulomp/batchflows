import logging
import unittest

from batchflows.Batch import Batch
from test.BaseTest import SaveValueStep, ExplosiveStep, UponCompletionContextManager


class BatchTest(unittest.TestCase):

    def setUp(self) -> None:
        logging.basicConfig(level=logging.DEBUG)

    def test_upon_completion(self):
        context = UponCompletionContextManager()
        batch = Batch(context_manager=context)
        batch.add_step(SaveValueStep(value_name='value01'))
        batch.execute()

        self.assertTrue(context.complete)

    def test_upon_completion_execution_error(self):
        context = UponCompletionContextManager()
        batch = Batch(context_manager=context)
        batch.add_step(ExplosiveStep())

        try:
            batch.execute()
        except Exception as identifier:
            pass
            
        self.assertFalse(context.complete)
        self.assertIsNotNone(context.error)