def merge_dicts(*dicts):
    items = []
    for single_dict in dicts:
        items.extend(single_dict.items())

    merged_dict = {key: value for (key, value) in items}
    return merged_dict
