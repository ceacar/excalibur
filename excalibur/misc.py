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


def flat_dict_list(dict_list):
    """
    will flatten list of dict or list of list of dict to a flat dict
    """
    if type(dict_list) == dict:
        return dict_list

    res_list = []
    for temp_list in dict_list:
        if type(temp_list) == list:
            res_list.append(flat_dict_list(temp_list))
        else:
            res_list.append(temp_list)

    res = {}
    for d in res_list:
        res.update(d)
    return res
