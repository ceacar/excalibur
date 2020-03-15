import hashlib

def md5_string(string_input: str) -> str:
    m = hashlib.md5()
    m.update(string_input)
    return m.hexdigest()
