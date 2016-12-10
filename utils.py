def appropriate_title(title, params):
    # TODO make lower for cirillic.
    for param in params.split(' '):
        if param not in title:
            return False
    return True
