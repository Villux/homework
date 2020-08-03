import unittest
import sys
sys.path.append(".")
import pytest
from unittest.mock import patch
from unittest import TestCase
from api import api
from sqlalchemy.orm import Query


class TestAPI(unittest.TestCase):
    test_case_folder = 'test_year2011'

    @pytest.mark.run(order=1)
    def test_query(self):
        api.process_query(Query(api.StyleImage).filter(api.StyleImage.year == 2011).limit(10), self.test_case_folder)
        files = api.list_folder(self.test_case_folder)
        self.assertTrue('images' in files)
        self.assertTrue('styles' in files)
        self.assertEqual(len(files['images']), 10)
        self.assertEqual(len(files['styles']), 10)


    @pytest.mark.run(order=2)
    def test_trasnformation(self):
        api.transform_folder(self.test_case_folder)
        files = api.list_folder(self.test_case_folder)
        self.assertTrue('augmented_images' in files)
        self.assertEqual(len(files['augmented_images']), 10)


    @pytest.mark.run(order=3)
    def test_prediction(self):
        result = api.predict_folder(self.test_case_folder)
        self.assertEqual(len(result), 10)
        self.assertTrue('boxes' in result[0])
        self.assertTrue('labels' in result[0])


    @pytest.mark.run(order=4)
    def test_cleanup(self):
        api.clean_folder(self.test_case_folder)
        files = api.list_folder(self.test_case_folder)
        self.assertIsNone(files)


if __name__ == '__main__':
    unittest.main()