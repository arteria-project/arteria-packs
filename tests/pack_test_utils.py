import json

class FakeResponse(object):

    def __init__(self, status_code, text):
        self.status_code = status_code
        self.text = json.dumps(text)

    def json(self):
        return json.loads(self.text)
