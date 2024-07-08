import os
import json

context = {
    'success' : False,
    'error' : 'Some error!!!'
}

with open('c:\\Windows\\Temp\\unity-test-step-fail', 'w') as json_file:
    json.dump(context, json_file)