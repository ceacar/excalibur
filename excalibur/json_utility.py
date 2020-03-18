def get_json_value_by_key(json_obj, attrb: str, default=None):
    if attrb in json_obj:
        return json_obj[attrb]
    else:
        return default
