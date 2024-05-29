import os
import pytest


@pytest.fixture(scope='session', autouse=True)
def setup_logs_directory():
    log_dir = '/app/logs'
    os.makedirs(log_dir, exist_ok=True)
    with open(os.path.join(log_dir, 'django_debug.log'), 'a'):
        os.utime(os.path.join(log_dir, 'django_debug.log'), None)
