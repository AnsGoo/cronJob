import json
from typing import Dict

def remove_none(data:Dict) -> Dict:
    keys = json.loads(json.dumps(data)).keys()
    for key in keys:
        if data[key] is None:
            del data[key]  
    return data