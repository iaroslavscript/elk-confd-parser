import enum
from typing import Tuple

from elkconfdparser import errors


class _BlockType(enum.Enum):
    NONE = enum.auto()
    COMMENT = enum.auto()
    STRING = enum.auto()
    VARIABLE = enum.auto()
    IGNORED = enum.auto()


class _ParserAction(enum.IntFlag):
    NONE = 0
    IGNORE_SYMBOL = enum.auto()
    DROP_VALUE = enum.auto()
    ESCAPE_NEXT = enum.auto()


class _TextPosition:

    def __init__(self, sym_i: float = 0, line_no: float = 0, line_i: float = 0):
        self.symbolIndex: float = sym_i
        self.lineNo: float = line_no
        self.lineSymbolIndex: float = line_i

    def inc(self, prev_eol: bool = False) -> None:

        self.symbolIndex += 1

        if prev_eol:
            self.lineNo += 1
            self.lineSymbolIndex = 0
        else:
            self.lineSymbolIndex += 1

    def toTuple(self) -> Tuple[float, float, float]:
        return self.symbolIndex, self.lineNo, self.lineSymbolIndex


def parse(text, start=0, end=None):

    if end is None:
        end = len(text)-1

    result = _parse(text, start, end)[0]

    return result


def _parse(text, start, end):  # noqa: C901  # FIXME

    block = _BlockType.NONE
    root = {}
    current = []
    stack = []
    action = _ParserAction.NONE
    delta = 0

    i = start
    while i <= end:

        delta = 0
        action &= ~_ParserAction.IGNORE_SYMBOL
        c = text[i]

        if c == "\n":
            action |= _ParserAction.DROP_VALUE

        elif block == _BlockType.COMMENT:
            action |= _ParserAction.IGNORE_SYMBOL

        elif block == _BlockType.STRING:

            if action & _ParserAction.ESCAPE_NEXT:
                action &= ~_ParserAction.ESCAPE_NEXT

            else:
                if c == '"':
                    action |= _ParserAction.DROP_VALUE
                elif c == "\\":
                    action |= _ParserAction.ESCAPE_NEXT | _ParserAction.IGNORE_SYMBOL

        elif c == '"':
            action |= _ParserAction.IGNORE_SYMBOL
            block = _BlockType.STRING

        elif c == "#":
            action |= _ParserAction.IGNORE_SYMBOL
            block = _BlockType.COMMENT

        elif c.isspace() or c in "=>,{}[]":
            action |= _ParserAction.DROP_VALUE

        elif c.isidentifier():
            block = _BlockType.VARIABLE

        else:
            action |= _ParserAction.IGNORE_SYMBOL

        if not (action & _ParserAction.DROP_VALUE):
            if not (action & _ParserAction.IGNORE_SYMBOL):
                current.append(c)

        else:
            if current:
                stack.insert(0, ''.join(current))
                current.clear()
                _drop_stack(root, stack)

            action &= ~_ParserAction.DROP_VALUE
            block = _BlockType.NONE

        if block != _BlockType.COMMENT and block != _BlockType.STRING:
            if c == '[':                    # Today I have no time to fix it
                block = _BlockType.IGNORED  # so for now list types are silently ignored
            elif c == ']':                  #
                block = _BlockType.NONE     #
                stack.insert(0, None)       #
                _drop_stack(root, stack)
            elif c == '{':
                data, delta = _parse(text, i+1, end)
                stack.insert(0, data)
                _drop_stack(root, stack)

            elif c == '}':
                return root, i

        i = max(i, delta) + 1

    return root, i


def _drop_stack(root, stack):
    if len(stack) > 1:
        root.setdefault(stack.pop(), []).append(stack.pop())

        if len(stack):
            raise errors.StackNotEmptyException('Unknown operands left on stack after assigment')
