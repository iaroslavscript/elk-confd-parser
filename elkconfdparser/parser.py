import enum
from typing import List, Tuple

from elkconfdparser import errors


class TokenFlag(enum.IntFlag):
    UNKNOWN = enum.auto()

    """multichar unknown sequence"""
    UNKNOWN_SEQ = enum.auto()

    SPACE = enum.auto()
    COMMENT = enum.auto()
    IDENTIFIER = enum.auto()
    STRING = enum.auto()
    STRING_SQ = enum.auto()
    NUMBER = enum.auto()

    """assign"""
    OPERATOR_ASG = enum.auto()

    """curly brace open"""
    OPERATOR_CBO = enum.auto()

    """curly brace open"""
    OPERATOR_CBC = enum.auto()

    """square brackets open"""
    OPERATOR_SBO = enum.auto()

    """square brackets close"""
    OPERATOR_SBC = enum.auto()

    """operator comma"""
    OPERATOR_COMMA = enum.auto()

    FLAG_PREV_END = enum.auto()
    FLAG_END = enum.auto()
    FLAG_ALL = FLAG_PREV_END | FLAG_END


class TextPos:

    def __init__(self, sym_i: float = 0, line_no: float = 0, line_i: float = 0):
        self.symbolIndex: float = sym_i
        self.lineNo: float = line_no
        self.lineSymbolIndex: float = line_i

    def inc(self, new_line: bool = False) -> None:

        self.symbolIndex += 1

        if new_line:
            self.lineNo += 1
            self.lineSymbolIndex = 0
        else:
            self.lineSymbolIndex += 1

    def toTuple(self) -> Tuple[float, float, float]:
        return self.symbolIndex, self.lineNo, self.lineSymbolIndex


def parse(text, debug_on_c=None, debug_on_i=None):

    buf: List[str] = []
    pos: TextPos = TextPos()
    prev_c: str = '\n'
    token = TokenFlag.UNKNOWN

    import pudb

    for c in text:

        pos.inc( c == '\n' )

        if c in debug_on_c:
            pudb.set_trace()

        if str(pos.lineNo) in debug_on_i:
            pudb.set_trace()

        token, tokens = _parse_char(c, prev_c, pos, buf, token)
        prev_c = c

        for x in tokens:
            value = '' if x[0] == TokenFlag.SPACE else x[1]
            print(f'{pos.toTuple()}\t{x[0].name[:6]}  {value}')


def _raise_if_no_char(c: str, prev_c: str) -> None:

    if len(c) != 1:
        raise errors.ElkValueError('Arg "c" expected to be a string contained only one char')

    if len(prev_c) != 1:
        raise errors.ElkValueError('Arg "prev_c" expected to be a string contained only one char')


def _tokenise(c: str, prev_c: str, buf: List[str], prev_token: TokenFlag) -> List:  # noqa: C901

    current = TokenFlag.UNKNOWN

    if  prev_token & (TokenFlag.UNKNOWN | TokenFlag.FLAG_END | TokenFlag.FLAG_PREV_END):

        if c.isspace():
            current = TokenFlag.SPACE

        elif c.isalpha():
            current = TokenFlag.IDENTIFIER

        elif c.isdigit():
            current = TokenFlag.NUMBER

        elif c == '#':
            current = TokenFlag.COMMENT

        elif c == '"':
            current = TokenFlag.STRING

        elif c == '\'':
            current = TokenFlag.STRING_SQ

        elif c == '=':
            current = TokenFlag.UNKNOWN_SEQ

        elif c in '{':
            current = TokenFlag.OPERATOR_CBO | TokenFlag.FLAG_END

        elif c in '}':
            current = TokenFlag.OPERATOR_CBC | TokenFlag.FLAG_END

        elif c in '[':
            current = TokenFlag.OPERATOR_SBO | TokenFlag.FLAG_END

        elif c in ']':
            current = TokenFlag.OPERATOR_SBC | TokenFlag.FLAG_END

        elif c in ',':
            current = TokenFlag.OPERATOR_COMMA | TokenFlag.FLAG_END

        else:
            raise errors.ElkSyntaxError('Syntax error - Unknown token')

        buf.append(c)

    elif prev_token == TokenFlag.SPACE:
        if c.isspace():
            current = prev_token
            buf.append(c)

        else:
            current |= TokenFlag.FLAG_PREV_END

    elif prev_token == TokenFlag.COMMENT:

        if c == '\n':
            current = TokenFlag.SPACE | TokenFlag.FLAG_PREV_END
        else:
            current |= TokenFlag.FLAG_PREV_END

    elif prev_token == TokenFlag.IDENTIFIER:
        if c.isalnum():  # no need to use c.isidentifier as we already know that it's not a first symbol
            current = prev_token
            buf.append(c)
        else:
            current |= TokenFlag.FLAG_PREV_END

    elif prev_token == TokenFlag.STRING:

        if c == '\n':
            raise errors.ElkSyntaxError('Syntax error - string without closing quotes')

        elif c == '"' and prev_c != '\\':
            current = prev_token | TokenFlag.FLAG_END

        else:
            current = prev_token

        buf.append(c)

    elif prev_token == TokenFlag.STRING_SQ:

        if c == '\n':
            raise errors.ElkSyntaxError('Syntax error - string without closing quotes')

        elif c == '\'' and prev_c != '\\':
            current = prev_token | TokenFlag.FLAG_END

        else:
            current = prev_token

        buf.append(c)

    elif prev_token == TokenFlag.NUMBER:
        if c.isnumeric():  # no need to use c.isidentifier as we already know that it's not a first symbol
            current = prev_token
            buf.append(c)
        else:
            current |= TokenFlag.FLAG_PREV_END

    elif prev_token & TokenFlag.UNKNOWN_SEQ:

        if c == '>' and prev_c == '=':

            current = TokenFlag.OPERATOR_ASG | TokenFlag.FLAG_END
            buf.append(c)
        else:
            raise errors.ElkSyntaxError('Syntax error - unknown operator ', c)

    else:
        raise errors.ElkValueError('Syntax error - wrong token id', prev_token)

    return current


def _collect_token(c: str, prev_c: str, pos: TextPos, buf: List[str], prev_token: TokenFlag) -> None:

    result = []
    token = TokenFlag.UNKNOWN

    for i in range(2):

        token = _tokenise(c, prev_c, buf, prev_token)

        if token & TokenFlag.FLAG_PREV_END:
            result.append((prev_token & ~TokenFlag.FLAG_ALL, ''.join(buf)))
            buf.clear()

        if token & TokenFlag.FLAG_END:
            result.append((token & ~TokenFlag.FLAG_ALL, ''.join(buf)))
            buf.clear()

        prev_token = token

        if not (token & TokenFlag.UNKNOWN):
            break

    if token & TokenFlag.UNKNOWN:
        raise errors.ElkValueError('Syntax error - unknown token ', token)

    return token, result


def _parse_char(c: str, prev_c: str, pos: TextPos, buf: List[str], prev_token: TokenFlag) -> None:

    _raise_if_no_char(c, prev_c)

    return _collect_token(c, prev_c, pos, buf, prev_token)
