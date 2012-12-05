import os


DEFAULT_LOCATION = os.path.join('/var', 'loadtest', 'loadtest')


def read_password(location=DEFAULT_LOCATION):
    with open(location) as f:
        return f.read().strip()
