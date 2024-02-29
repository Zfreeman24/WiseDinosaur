import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Source Code')))

import unittest
from unittest.mock import patch, mock_open
import json
from WiseDinosaur import load_json_data, get_random_dinosaur_name, get_dinosaur_prompt_and_personality

class TestDinosaurApp(unittest.TestCase):
    def test_load_json_data(self):
        """
        Test the load_json_data function to ensure it correctly loads data from a JSON file.
        """
        test_data = {"test": "value"}
        with patch('builtins.open', mock_open(read_data=json.dumps(test_data))):
            result = load_json_data("dummy_file.json")
        self.assertEqual(result, test_data)

    def test_get_random_dinosaur_name(self):
        """
        Test the get_random_dinosaur_name function to ensure it returns a string.
        This test doesn't guarantee randomness but ensures the function's basic correctness.
        """
        result = get_random_dinosaur_name()
        self.assertIsInstance(result, str)

    @patch('WiseDinosaur.random.choice')
    def test_get_dinosaur_prompt_and_personality(self, mock_choice):
        """
        Test the get_dinosaur_prompt_and_personality function.
        Mock random.choice to control the output and ensure the function returns expected values.
        """
        mock_choice.return_value = ("T-Rex", "friendly")
        dinosaurs = {"T-Rex": "friendly"}
        result = get_dinosaur_prompt_and_personality(dinosaurs)
        self.assertEqual(result, ("T-Rex", "friendly"))

if __name__ == '__main__':
    unittest.main()
