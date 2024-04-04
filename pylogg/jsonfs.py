""" Read and write JSON and JSONL files. """

import json

import pylogg

log = pylogg.get('jsonfs')

def load_lines(jsonl_file : str) -> list[dict]:
    """ Load a JSONL file into list of dictionaries. """
    log.trace("Load JSONL:", jsonl_file)
    with open(jsonl_file) as fp:
        jsonlines = list(fp)

    return [ json.loads(json_str) for json_str in jsonlines ]


def save_lines(linelist : list[dict] , jsonl_file : str):
    """ Save a list of dictionaries as a JSONL file. """

    assert type(linelist) == list
    log.trace("Save JSONL:", jsonl_file)

    # Make sure all dict items have the same keys.
    keys = set()
    for line in linelist:
        for k in line.keys():
            keys.add(k)

    # Add the missing ones with None.
    for line in linelist:
        for k in keys:
            if k not in line:
                line[k] = None

    jsonlines = [ json.dumps(line) + "\n" for line in linelist ]
    with open(jsonl_file, "w") as fp:
        fp.writelines(jsonlines)


def save_dict(obj : dict, filename):
    """ Save a dictionary object as JSON. """
    obj = _recurse_type(obj)

    log.trace("Save JSON: ", filename)
    try:
        json.dump(obj, open(filename, "w"), indent=4)
    except Exception as err:
        print(obj)
        print(err)


def load_dict(filename) -> dict:
    """ Load a JSON file as dict. """
    log.trace("Load JSON: ", filename)
    d = json.load(open(filename))
    return d


def _recurse_type(obj):
    if type(obj) != dict:
        obj = dict(obj)

    for k, v in obj.items():
        if hasattr(v, 'item') and callable(v.item):
            # handle numpy values
            obj[k] = v.item()
        elif type(v).__name__ == 'ndarray':
            obj[k] = [i.item() for i in v]
        elif type(v) not in [dict, list, str, int, float, type(None)]:
            obj[k] = dict(v)
        elif type(v) == dict:
            obj[k] = _recurse_type(v)
    return obj
