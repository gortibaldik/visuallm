import time

import pytest


@pytest.mark.full_app_tests
def test_can_be_run(full_app):
    time.sleep(0.2)
