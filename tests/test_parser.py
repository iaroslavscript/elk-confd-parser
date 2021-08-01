import pytest

from elkconfdparser import errors
from elkconfdparser import parser


class TestDropStack:
    @pytest.mark.parametrize(
        "input_root, input_stack, expected_root, expected_stack",
        [
            ({}, [], {}, []),
            ({}, [1], {}, [1]),
            ({}, [2, 1], {1: [2]}, []),
            ({1: [8]}, [2, 1], {1: [8, 2]}, []),
            ({1: [8], 3: [9]}, [2, 1], {1: [8, 2], 3: [9]}, []),
        ],
    )
    def testTwoOperands(self, input_root, input_stack, expected_root, expected_stack):

        assert parser._drop_stack(input_root, input_stack) is None
        assert input_root == expected_root
        assert input_stack == expected_stack

    @pytest.mark.parametrize(
        "input_root, input_stack, expected_root, expected_stack",
        [
            ({}, [3, 2, 1], {1: [2]}, [3]),
        ],
    )
    def testMultipleOperands(self, input_root, input_stack, expected_root, expected_stack):

        with pytest.raises(errors.StackNotEmptyException, match=r'.*operands left.*'):
            parser._drop_stack(input_root, input_stack)

        assert input_root == expected_root
        assert input_stack == expected_stack


class TestParse:

    @pytest.mark.parametrize(
        "test_input, expected",
        [
            ("", {}),
            (" ", {}),
            (" \n ", {}),
            ("a{}", {'a': [{}]}),
            ("aa{}", {'aa': [{}]}),
            (" a{} ", {'a': [{}]}),
            (" a { } ", {'a': [{}]}),
            (" \na\n \n{\n \n}\n ", {'a': [{}]}),
            ('a{b=>"c"}', {'a': [{'b': ['c']}]}),
            ('\na\n\n{\nb\n=>\n"c"\n}\n', {'a': [{'b': ['c']}]}),
        ],
    )
    def testSectionDetected(self, test_input, expected):
        assert parser.parse(test_input) == expected

    @pytest.mark.parametrize(
        "test_input, expected",
        [
            ('b=>"c"', [{'b': ['c']}]),
        ],
    )
    def testSectionValueDetection(self, test_input, expected):
        test_input = f"a {{ {test_input} }}"
        assert parser.parse(test_input)['a'] == expected

    @pytest.mark.parametrize(
        "test_input, expected",
        [
            ('"the string"', ['the string']),
            ('"\\"quoted string\\""', ['"quoted string"']),
            ('"middle \\"quoted\\" string"', ['middle "quoted" string']),
            ('"unpair \\"\\"\\" string"', ['unpair """ string']),
        ],
    )
    def testSectionAttrValue(self, test_input, expected):
        test_input = f"a {{ b => {test_input} }}"
        assert parser.parse(test_input)['a'][0]['b'] == expected

    def testReal(self):

        test_input = """
        aa {
            bb {
                cc => "dd"
                ee => "ff"
            }

            gg {
                hh => "the string 1"
                jj => "\\"with\\" quotes 1"
            }

            gg {
                hh => "the string 2"
                jj => "\\"with\\" quotes 2"
            }
        }
        """
        expected = {
            "aa": [
                {
                    "bb": [
                        {
                            "cc": ["dd"],
                            "ee": ["ff"],
                        }
                    ],
                    "gg": [
                        {
                            "hh": ["the string 1"],
                            "jj": ["\"with\" quotes 1"],
                        },
                        {
                            "hh": ["the string 2"],
                            "jj": ["\"with\" quotes 2"],
                        }
                    ]
                }
            ]
        }

        assert parser.parse(test_input) == expected


class TestTextPosition:

    def testInitDefault(self):

        pos = parser._TextPosition()

        assert pos.symbolIndex == 0
        assert pos.lineNo == 0
        assert pos.lineSymbolIndex == 0

    @pytest.mark.parametrize(
        "test_input, expected",
        [
            ((), (0, 0, 0), ),
            ((0, 0, 0), (0, 0, 0), ),
            ((1, 2, 3), (1, 2, 3), ),
            ((-1, -2, -3), (-1, -2, -3), ),
        ]
    )
    def testInitArgs(self, test_input, expected):

        pos = parser._TextPosition(*test_input)

        assert pos.symbolIndex == expected[0]
        assert pos.lineNo == expected[1]
        assert pos.lineSymbolIndex == expected[2]

    @pytest.mark.parametrize(
        "test_input, expected",
        [
            ({}, (0, 0, 0), ),
            ({'sym_i': 0, 'line_no': 0, 'line_i': 0}, (0, 0, 0), ),
            ({'sym_i': 1, 'line_no': 2, 'line_i': 3}, (1, 2, 3), ),
            ({'sym_i': -1, 'line_no': -2, 'line_i': -3}, (-1, -2, -3), ),
        ]
    )
    def testInitKwargs(self, test_input, expected):

        pos = parser._TextPosition(**test_input)

        assert pos.symbolIndex == expected[0]
        assert pos.lineNo == expected[1]
        assert pos.lineSymbolIndex == expected[2]

    @pytest.mark.parametrize(
        "test_input, expected",
        [
            ((), (0, 0, 0), ),
            ((0, 0, 0), (0, 0, 0), ),
            ((1, 2, 3), (1, 2, 3), ),
            ((-1, -2, -3), (-1, -2, -3), ),
        ]
    )
    def testToTuple(self, test_input, expected):

        assert parser._TextPosition(*test_input).toTuple() == expected
