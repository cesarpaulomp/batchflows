import logging
import unittest

from test.BaseTest import FakeContextManager, MaybeRemoveStep


class RemoteStepTest(unittest.TestCase):

    def setUp(self) -> None:
        logging.basicConfig(level=logging.DEBUG)

    def test_happy_path(self):
        step = MaybeRemoveStep(name='Remote step happy path')
        step.start(FakeContextManager())

    def test_timeout(self):
        context = FakeContextManager()
        context.all_is_done = False
        step = MaybeRemoveStep(name='Remote step timeout', timeout=1)

        expected = False

        try:
            step.start(context)
        except TimeoutError as error:
            expected = True

        self.assertTrue(expected)
            
    def upon_completion(self):
        context = FakeContextManager()
        context.all_is_done = False
        step = MaybeRemoveStep(name='Remote step timeout', timeout=1)

        expected = False

        try:
            step.start(context)
        except TimeoutError as error:
            expected = True

        self.assertTrue(expected)