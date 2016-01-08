import numpy as np
import json

class dict(dict):
    def __init__(self, *args, **kwargs):
        super(dict, self).__init__(*args, **kwargs)
        self.__dict__ = self

class decoder(json.JSONDecoder):
    def __init__(self,  **kwargs):
        json.JSONDecoder.__init__(self, **kwargs)
        # Use the custom JSONArray
        self.parse_array = self.JSONArray
        self.object_hook = self.JSONDict
        # Use the python implemenation of the scanner
        self.scan_once = json.scanner.py_make_scanner(self)

    def JSONArray(self, s_and_end, scan_once, **kwargs):
        values, end = json.decoder.JSONArray(s_and_end, scan_once, **kwargs)
        try:
            return np.array(values, dtype=np.float32), end
        except:
            return values, end

    def JSONDict(self, obj):
        return dict(obj)

geometries = json.load(open('data/data.json'), cls=decoder)
