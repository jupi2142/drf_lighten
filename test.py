import unittest
from drf_lighten.parsers import StackParser


class ParserTestCase(unittest.TestCase):
    def setUp(self):
        self.parser = StackParser()
        self.correct_cases = {
            "{id,value}": {
                "type": "keep",
                "fields": {"self": ["id", "value"], "nested": {}},
            },
            "-{id,value}": {
                "type": "omit",
                "fields": {"self": ["id", "value"], "nested": {}},
            },
            "{id,value,test{id,value}}": {
                "type": "keep",
                "fields": {
                    "self": ["id", "value"],
                    "nested": {
                        "test": {
                            "type": "keep",
                            "fields": {"self": ["id", "value"], "nested": {}},
                        }
                    },
                },
            },
            "{id,value,-test{id,value}}": {
                "type": "keep",
                "fields": {
                    "self": ["id", "value"],
                    "nested": {
                        "test": {
                            "type": "omit",
                            "fields": {"self": ["id", "value"], "nested": {}},
                        }
                    },
                },
            },
            "{id,value,test{id,value},jupi}": {
                "type": "keep",
                "fields": {
                    "self": ["id", "value", "jupi"],
                    "nested": {
                        "test": {
                            "type": "keep",
                            "fields": {"self": ["id", "value"], "nested": {}},
                        }
                    },
                },
            },
            "{id,value,test{id,value},jupi,other{xms}}": {
                "type": "keep",
                "fields": {
                    "self": ["id", "value", "jupi"],
                    "nested": {
                        "test": {
                            "type": "keep",
                            "fields": {"self": ["id", "value"], "nested": {}},
                        },
                        "other": {
                            "type": "keep",
                            "fields": {"self": ["xms"], "nested": {}},
                        },
                    },
                },
            },
            "{id,value,test{id, exit{id}}}": {
                "type": "keep",
                "fields": {
                    "self": ["id", "value"],
                    "nested": {
                        "test": {
                            "type": "keep",
                            "fields": {
                                "self": ["id"],
                                "nested": {
                                    "exit": {
                                        "type": "keep",
                                        "fields": {
                                            "self": ["id"],
                                            "nested": {},
                                        },
                                    }
                                },
                            },
                        }
                    },
                },
            },
            "-{id,value,-providers{icon,users},service{id,url}}": {
                "type": "omit",
                "fields": {
                    "self": ["id", "value"],
                    "nested": {
                        "providers": {
                            "type": "omit",
                            "fields": {
                                "self": ["icon", "users"],
                                "nested": {},
                            },
                        },
                        "service": {
                            "type": "keep",
                            "fields": {
                                "self": ["id", "url"],
                                "nested": {},
                            },
                        },
                    },
                },
            },
        }
        self.wrong_cases = {
            "{id,-value}": Exception("Starts with -"),
        }

    def test_correct(self):
        for string, correct_result in self.correct_cases.items():
            with self.subTest():
                print(string.ljust(50), end="")
                print("... SUCCESS".rjust(40))
                self.assertEqual(self.parser.parse(string), correct_result)

    def test_wrong(self):
        for string, correct_result in self.wrong_cases.items():
            with self.subTest():
                print(string.ljust(50), end="")
                print("... SUCCESS".rjust(40))
                with self.assertRaises(Exception):
                    self.parser.parse(string)


if __name__ == "__main__":
    unittest.main()
