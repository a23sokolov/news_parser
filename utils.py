# -*- coding: utf-8 -*-
def appropriate_title(title, params):
    # TODO make lower for cirillic.
    for param in params.split(' '):
        if param in title:
            return True
    return False
