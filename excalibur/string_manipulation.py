def split(str_with_new_lines):
    return str_with_new_lines.split('\n')


def strip_str_arr(str_arr):
    """
    strips a str_arr, remove \n and spaces
    """
    res = []
    for string in str_arr:
        temp = string.rstrip().strip()
        if not temp:
            continue
        res.append(temp)
    return res


def pprint_str_arr(str_arr):
    """
    removes \n and spaces
    then print str_arr line by line
    """
    str_arr = ppformat_str_with_new_lines(str_arr)
    for string in str_arr:
        print(string)


def ppformat_str_with_new_lines(str_with_new_lines):
    """
    make long line with new lines symbol in it to str arr
    removes \n and spaces
    """
    split_arr = split(str_with_new_lines)
    stripped = strip_str_arr(split_arr)
    return stripped
