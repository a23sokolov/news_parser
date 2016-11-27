

def appropriate_title(title, params):
    for param in params.split(' '):
        if params not in title:
            return False
    return True
