import pytest

from elkconfdparser import errors
from elkconfdparser import parser


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

    @pytest.mark.parametrize(
        "test_input, expected",
        [
            ((0, 0, 0, False), (1, 0, 1), ),
            ((0, 0, 0, True), (1, 1, 0), ),
            ((1, 1, 1, False), (2, 1, 2), ),
            ((1, 1, 1, True), (2, 2, 0), ),
        ]
    )
    def testInc(self, test_input, expected):

        p = parser._TextPosition(*test_input[:3])
        p.inc(test_input[3])

        assert p.toTuple() == expected


class TestRaiseIfNoChar:

    @pytest.mark.parametrize(
        "test_input",
        [
            ('a', 'a'),
            ('a', 'b'),
            (' ', ' '),
            ('\n', '\n'),
            ('\t', '\t'),
        ]
    )
    def testNotRaised(self, test_input) -> None:

        parser._raise_if_no_char(*test_input)

    @pytest.mark.parametrize(
        "test_input",
        [
            ('', '', 'c'),
            ('', 'a', 'c'),
            ('a', '', 'prev_c'),
            ('a', 'aa', 'prev_c'),
            ('aa', 'a', 'c'),
            ('aa', 'aa', 'c'),
        ]
    )
    def testRaised(self, test_input) -> None:

        c, prev_c, name = test_input

        with pytest.raises(ValueError, match=f'.*"{name}".*'):
            parser._raise_if_no_char(c, prev_c)
