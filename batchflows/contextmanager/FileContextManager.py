from batchflows.contextmanager.ContextManager import ABCContextManager
from batchflows.util.CustomExceptions import RemoteStepException
from batchflows.Step import RemoteStep
import os
import json
import uuid
import logging

class FileContextManager(ABCContextManager):
    def __init__(self, filepath: str, is_linux_os: bool = True, is_remote_step: bool = False, process_id: str = None, process_name: str = None):
        super().__init__()
        self.filepath = filepath
        self.is_linux_os = is_linux_os
        self.is_remote_step = is_remote_step
        self.process_id = process_id if process_id else uuid.uuid4()
        self.process_name = process_name if process_name else uuid.uuid4()

    def is_remote_step_done(self, name: str):
        final_path = self._buildFileName(name)
        if self._checkIfFileExists(final_path):
            with open(final_path, "r") as json_file:
                loaded = json.load(json_file)
                if 'error' in loaded and not (loaded['error'] is None):
                    logging.error(loaded['error'])
                    raise RemoteStepException(loaded['error'])
                else:
                    return loaded['success']
                
        else:
            return False

    def _get_file_separator(self):
        return '/' if self.is_linux_os else '\\'

    def upon_completion(self, success: bool, error: str = None):
        if self.is_remote_step:
            self._write_remotestep_status_file(success, error)
        else:
            self._remove_files()

    def _write_remotestep_status_file(self, success : bool, error : str):
        with open(self._buildFileName(self.process_name), 'w') as json_file:
            json.dump({ 'error' : error, 'success' : success }, json_file)

    def _remove_files(self):
        for step in self.steps:
            if isinstance(step, RemoteStep):
                file_name = self._buildFileName(step.name)
                if self._checkIfFileExists(file_name):
                    os.remove(file_name)
        pass
    
    def _buildFileName(self, process_name: str):
        return f'{self.filepath}{self._get_file_separator()}{self.process_id}-{process_name}'

    def _checkIfFileExists(self, path: str):
        return os.path.exists(path) and os.path.isfile(path)