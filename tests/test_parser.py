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
