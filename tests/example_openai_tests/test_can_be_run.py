import time

import pytest


@pytest.mark.full_app_tests
def test_just_run_the_app(full_app):
    time.sleep(0.05)
