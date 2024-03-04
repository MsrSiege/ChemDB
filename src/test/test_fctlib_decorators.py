# ++---------------------------------------------------------------------------------------------------------------------++#
# ++ Imports
# ++---------------------------------------------------------------------------------------------------------------------++#
import contextlib
import unittest

from src.fctlib import decorators


# ++---------------------------------------------------------------------------------------------------------------------++#
# ++ Unit test for Retry (generated by Cody.AI)
# ++---------------------------------------------------------------------------------------------------------------------++#
class TestRetry(unittest.TestCase):
    def test_retry_success(self):
        @decorators.Retry()
        def test_func():
            return "success"

        result = test_func()
        self.assertEqual(result, "success")

    def test_retry_failure(self):
        @decorators.Retry(ExcException=ValueError)
        def test_func():
            raise ValueError("failure")

        with contextlib.suppress(decorators.RetryFailedException):
            test_func()

    def test_retry_attempts(self):
        attempt_count = 0

        @decorators.Retry(ExcException=ValueError, attempts=3)
        def test_func():
            nonlocal attempt_count
            attempt_count += 1
            raise ValueError("failure")

        with contextlib.suppress(decorators.RetryFailedException):
            test_func()
        self.assertEqual(attempt_count, 3)