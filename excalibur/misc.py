import sys


def merge_dicts(*dicts):
    items = []
    for single_dict in dicts:
        items.extend(single_dict.items())

    merged_dict = {key: value for (key, value) in items}
    return merged_dict


class dotdict(dict):
    """
    dot.notation access to dictionary attributes
    mydict = {'val':'it works'}
    nested_dict = {'val':'nested works too'}
    mydict = dotdict(mydict)
    mydict.val
    # 'it works'

    mydict.nested = dotdict(nested_dict)
    mydict.nested.val
    # 'nested works too'
    """
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


def dlProgress(count, blockSize, totalSize):
    percent = int(count * blockSize * 100 / totalSize)
    sys.stdout.write("\r" + "...%d%%" % percent)
    sys.stdout.flush()
