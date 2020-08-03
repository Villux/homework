import unittest
import sys
sys.path.append(".")
sys.path.append("./celery_queue")
import pytest
from unittest.mock import patch
from unittest import TestCase
from celery import chain
from celery_queue import tasks


class TestCelery(unittest.TestCase):

    def test_task_state_and_addition(self):

        task = tasks.add.apply(args=[3, 5])
        self.assertEqual(task.status, "SUCCESS")
        self.assertEqual(task.result, 8)


    def test_task_state_and_multiply(self):

        task = tasks.multiply.apply(args=[3, 5])
        self.assertEqual(task.status, "SUCCESS")
        self.assertEqual(task.result, 15)


if __name__ == '__main__':
    unittest.main()