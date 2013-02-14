# -*- coding: utf-8 -*-
from . import config
import hashlib
import os
import random
import re
import requests
import string

# Maximum value for unsigned integer stored in 4 bytes
MAX_INT_32 = 4294967295

TYPE_DICTIONARY = {
    "production": 0,
    "technosphere": 1,
    "biosphere": 2,
    }

DOWNLOAD_URL = "http://secret.brightwaylca.org/data/"


def natural_sort(l):
    """Sort the given list in the way that humans expect"""
    # http://nedbatchelder.com/blog/200712/human_sorting.html#comments
    convert = lambda text: int(text) if text.isdigit() else text
    alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)', key)]
    return sorted(l, key=alphanum_key)


def recursively_sort(obj):
    if isinstance(obj, dict):
        return sorted([(k, recursively_sort(v)) for k, v in obj.iteritems()])
    elif hasattr(obj, "__iter__"):
        return sorted((recursively_sort(x) for x in obj))
    else:
        return obj


def random_string(length):
    return ''.join(random.choice(string.letters + string.digits
        ) for i in xrange(length))


def combine_methods(name, *ms):
    from . import Method, methods
    data = {}
    units = set([methods[tuple(x)]["unit"] for x in ms])
    for m in ms:
        for key, amount in Method(m).load().iteritems():
            data[key] = data.get(key, 0) + amount
    meta = {
        "description": "Combination of the following methods: " + \
            ", ".join([str(x) for x in ms]),
        "num_cfs": len(data),
        "unit": list(units)[0] if len(units) == 1 else "Unknown"
    }
    method = Method(name)
    method.register(**meta)
    method.write(data)
    method.process()


def database_hash(data):
    return hashlib.md5(unicode(recursively_sort(data))).hexdigest()


def activity_hash(data):
    string = (data["name"].lower() + \
        u"".join(data["categories"]) + \
        (data.get("unit", u"") or u"").lower() + \
        (data.get("location", u"") or u"").lower())
    return unicode(hashlib.md5(string.encode('utf-8')).hexdigest())


def download_file(filename):
    dirpath = config.request_dir("downloads")
    filepath = os.path.join(dirpath, filename)
    download = requests.get(DOWNLOAD_URL + filename, prefetch=False).raw
    chunk = 128 * 1024
    with open(filepath, "wb") as f:
        while True:
            segment = download.read(chunk)
            if not segment:
                break
            f.write(segment)
    return filepath
