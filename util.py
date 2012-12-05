import os
import os.path


DEFAULT_LOCATION = os.path.join('/var', 'loadtest', 'loadtest')


def read_password(location=DEFAULT_LOCATION):
    if os.path.exists(location):
        with open(location) as f:
            return f.read().strip()
    # hard-coded token from zamboni settings_test_vaurien
    return 'sqldkjqlskjd34'
