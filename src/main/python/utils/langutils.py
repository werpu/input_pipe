import unicodedata
import re


# normalizes a string into a caseless one
def normalize_caseless(text):
    if text is None:
        return "____none____"
    return unicodedata.normalize("NFKD", text.casefold())


# equal ignore case equivalent
def caseless_equal(left, right):
    return normalize_caseless(left) == normalize_caseless(right)


# a caseless re match
def re_match(my_str, r_exp):
    if r_exp is None:
        return False
    return re.search(r_exp, my_str, re.RegexFlag.IGNORECASE) is not None


def save_fetch(first_order_func: callable, default=None):
    try:
        return first_order_func()
    except KeyError or IndexError:
        return default


# from https://stackoverflow.com/questions/19053707/converting-snake-case-to-lower-camel-case-lowercamelcase
def to_camel_case(snake_str):
    components = snake_str.split('_')
    return components[0] + ''.join(x.title() for x in components[1:])

def build_tree(target, *args):

    curr_root = target
    for arg in args:
        curr_root[arg] = save_fetch(lambda: curr_root[arg], {})
        curr_root = curr_root[arg]

    return curr_root

DUMMY_DEFAULT = "__booga__"