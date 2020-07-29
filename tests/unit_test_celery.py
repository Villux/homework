import unittest
import sys
sys.path.append(".")
sys.path.append("./celery_queue")
import pytest
from unittest.mock import patch
from unittest import TestCase
from celery import chain
from celery_queue import tasks

# Ref of celery mock unit test
# - https://www.distributedpython.com/2018/05/15/testing-celery-chains/
# - https://www.distributedpython.com/2018/05/01/unit-testing-celery-tasks/
# - http://docs.celeryproject.org/en/latest/userguide/testing.html

class TestAddTask(unittest.TestCase):

    def test_task_state_and_addition(self):

        task = tasks.add.apply(args=[3, 5])
        self.assertEqual(task.status, "SUCCESS")
        self.assertEqual(task.result, 8)

class TestMultiplyTask(unittest.TestCase):

    def test_task_state_and_multiply(self):

        task = tasks.multiply.apply(args=[3, 5])
        self.assertEqual(task.status, "SUCCESS")
        self.assertEqual(task.result, 15)


if __name__ == '__main__':
    unittest.main()