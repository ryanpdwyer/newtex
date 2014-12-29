import unittest
from newtex._git import parse_git_config


class Test_parse_git_config(unittest.TestCase):

    def test_equals_signs(self):
        config_with_equals = "test.parameter=this=has=equals=signs"
        self.assertEquals(parse_git_config(config_with_equals),
                          {'test.parameter':
                          'this=has=equals=signs'})
