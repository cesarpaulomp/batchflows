import os
import json

context = {
    'success' : True
}

with open('c:\\Windows\\Temp\\unity-test-step-ok', 'w') as json_file:
    json.dump(context, json_file)