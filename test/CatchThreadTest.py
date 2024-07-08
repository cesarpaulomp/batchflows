import unittest
import logging

from batchflows.threading.CatchThread import CatchThread

def add_value_dict(some: dict, value: int):
    some['value'] = value

def explode():
    raise Exception('Boom') 

class CatchThreadTest(unittest.TestCase):

    def setUp(self) -> None:
        logging.basicConfig(level=logging.DEBUG)
    
    def test_simple_async_run (self):
        book = { 'value' : 10 }
        trd = CatchThread(target=lambda: add_value_dict(book, 5), name='some thread')
        trd.start()
        trd.join()

        self.assertEqual(5, book['value'])

    def test_get_exception (self):
        trd = CatchThread(target=lambda: explode(), name='some thread')
        trd.start()
        trd.join()

        error = trd.get_error_if_exists()
        
        print(error)
        
        self.assertIsNotNone(error)

