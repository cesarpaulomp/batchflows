import unittest
import sys
import os
import logging

from batchflows.Batch import Batch
from batchflows.contextmanager.FileContextManager import FileContextManager
from batchflows.util.CustomExceptions import RemoteStepException
from test.BaseTest import MaybeRemoveStep, SubProcessStep, RemoteBatch

def add_value_dict(some: dict, value: int):
    some['value'] = value

def explode():
    raise Exception('Boom') 

class FileContextManagerTest(unittest.TestCase):

    def setUp(self) -> None:
        logging.basicConfig(level=logging.DEBUG)

    def test_get_file_separator(self):
        context = FileContextManager(filepath='/temp', is_linux_os=False, is_remote_step=False)
        
        self.assertEqual('\\', context._get_file_separator())

        context.is_linux_os = True

        self.assertEqual('/', context._get_file_separator())

    def test_buildFileName(self):
        context = FileContextManager(filepath='/tmp', process_id='unity-test', process_name='test')
        self.assertEqual('/tmp/unity-test-test', context._buildFileName('test'))

    def test_checkIfFileExists(self):
        context = FileContextManager(filepath='c:\\Windows\\Temp', is_linux_os=False, is_remote_step=True)
        context._write_remotestep_status_file(True, None)

        self.assertTrue(context._checkIfFileExists(context._buildFileName(context.process_name)))
        os.remove(context._buildFileName(context.process_name))

        self.assertFalse(context._checkIfFileExists(context._buildFileName(context.process_name)))

    @unittest.skipUnless(sys.platform.startswith("win"), "requires Windows")
    def test_is_remote_step_done_windows(self):
        self.is_remote_step_done(filepath='c:\\Windows\\Temp')

    @unittest.skipUnless(sys.platform.startswith("linux"), "requires some Linux")
    def test_is_remote_step_done(self):
        self.is_remote_step_done()
    
    def is_remote_step_done(self, filepath: str = '/tmp'):
        context = FileContextManager(filepath=filepath, is_linux_os=False, is_remote_step=False, process_id='unity-test')
        step = SubProcessStep(name='step-ok')
        step.start(context_manager=context)

        self.assertTrue(context.is_remote_step_done('step-ok'))

    @unittest.skipUnless(sys.platform.startswith("win"), "requires Windows")
    def test_is_remote_step_done_unspected_exception_windows(self):
        self.is_remote_step_done_unspected_exception(filepath='c:\\Windows\\Temp')

    @unittest.skipUnless(sys.platform.startswith("linux"), "requires some Linux")
    def test_is_remote_step_done_unspected_exception(self):
        self.is_remote_step_done_unspected_exception()

    def is_remote_step_done_unspected_exception(self, filepath: str = '/tmp'):
        context = FileContextManager(filepath=filepath, is_linux_os=False, is_remote_step=False, process_id='unity-test')
        step = SubProcessStep(name='step-fail', fail=True)
        
        error = False

        try:
            step.start(context_manager=context)
        except RemoteStepException as identifier:
            error = True
        
        self.assertTrue(error)
        
    @unittest.skipUnless(sys.platform.startswith("win"), "requires Windows")
    def test_is_remote_step_done_file_not_exists_windows(self):
        self.is_remote_step_done_file_not_exists(filepath='c:\\')

    @unittest.skipUnless(sys.platform.startswith("linux"), "requires some Linux")
    def test_is_remote_step_done_file_not_exists(self):
        self.is_remote_step_done_file_not_exists()

    def is_remote_step_done_file_not_exists(self, filepath: str = '/tmp'):
        context = FileContextManager(filepath=filepath, is_linux_os=False, is_remote_step=False)
        self.assertFalse(context.is_remote_step_done(name='some_step'))
    
    @unittest.skipUnless(sys.platform.startswith("win"), "requires Windows")
    def test_expected_timeout_error_windows (self):
        self.expected_timeout_error(filepath='c:\\Windows\\Temp')

    @unittest.skipUnless(sys.platform.startswith("linux"), "requires some Linux")
    def test_expected_timeout_error (self):
        self.expected_timeout_error()

    def expected_timeout_error (self, filepath: str = '/tmp'):
        context = FileContextManager(filepath=filepath, is_linux_os=False, is_remote_step=False)

        batch = Batch(context_manager=context, name='FileContextManager expected timeout error')
        batch.add_step(MaybeRemoveStep(name='expected-timeout', timeout=0.5))

        expected = False

        try:
            batch.execute()
        except TimeoutError as error:
            expected = True

        self.assertTrue(expected)

    @unittest.skipUnless(sys.platform.startswith("win"), "requires Windows")
    def test_write_remotestep_status_file(self):
        context = FileContextManager(filepath='c:\\Windows\\Temp', is_linux_os=False, is_remote_step=True)
        context._write_remotestep_status_file(True, None)

        self.assertTrue(os.path.isfile(context._buildFileName(context.process_name)))
        os.remove(context._buildFileName(context.process_name))

    @unittest.skipUnless(sys.platform.startswith("win"), "requires Windows")
    def test_write_remotestep_status_file_batch(self):
        context = FileContextManager(filepath='c:\\Windows\\Temp', is_linux_os=False, is_remote_step=False, process_id='unity-test')
        step = RemoteBatch(name='remote-batch')
        step.start(context_manager=context)

    @unittest.skipUnless(sys.platform.startswith("win"), "requires Windows")
    def test_remove_files(self):
        context = FileContextManager(filepath='c:\\Windows\\Temp', is_linux_os=False, is_remote_step=False, process_id='unity-test')
        step = RemoteBatch(name='remote-batch')
        step.start(context_manager=context)

        self.assertTrue(os.path.isfile(context._buildFileName('remote-batch')))
        
        context._remove_files()

        self.assertFalse(os.path.isfile(context._buildFileName(context.process_name)))

