import enum
from typing import List, Tuple

from elkconfdparser import errors


class TokenFlag(enum.IntFlag):
    UNKNOWN = enum.auto()
    SPACE = enum.auto()
    COMMENT = enum.auto()
    IDENTIFIER = enum.auto()
    STRING = enum.auto()
    NUMBER = enum.auto()
    OPERATOR = enum.auto()
    FLAG_END = enum.auto()
    FLAG_ALL = FLAG_END


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

    if (prev_token == TokenFlag.UNKNOWN) or (prev_token & TokenFlag.FLAG_END):
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

        elif c == '=':
            current = TokenFlag.OPERATOR

        elif c in '{}[],':
            current = TokenFlag.OPERATOR | TokenFlag.FLAG_END

        else:
            raise errors.ElkSyntaxError('Syntax error - Unknown token')

        buf.append(c)

    elif prev_token == TokenFlag.SPACE:
        if c.isspace():
            current = prev_token
            buf.append(c)

    elif prev_token == TokenFlag.IDENTIFIER:
        if c.isalnum():  # no need to use c.isidentifier as we already know that it's not a first symbol
            current = prev_token
            buf.append(c)

    elif prev_token == TokenFlag.STRING:

        if c == '\n':
            raise errors.ElkSyntaxError('Syntax error - string without closing quotes')

        elif c == '"' and prev_c != '\\':
            current = prev_token | TokenFlag.FLAG_END

        else:
            current = prev_token

        buf.append(c)

    elif prev_token == TokenFlag.NUMBER:
        if c.isnumeric():  # no need to use c.isidentifier as we already know that it's not a first symbol
            current = prev_token
            buf.append(c)

    elif prev_token == TokenFlag.OPERATOR:

        if prev_c == '=':

            if c == '>':
                current = prev_token | TokenFlag.FLAG_END
                buf.append(c)
            else:
                raise errors.ElkSyntaxError('Syntax error - unknown operator')

    else:
        raise errors.ElkValueError('Syntax error - wrong token id', prev_token)

    return current


def _collect_token(c: str, prev_c: str, pos: TextPos, buf: List[str], prev_token: TokenFlag) -> None:

    result = []

    for i in range(2):

        token = _tokenise(c, prev_c, buf, prev_token)

        if token == TokenFlag.UNKNOWN:
            result.append((prev_token, ''.join(buf)))
            buf.clear()
            prev_token = token

        elif token & TokenFlag.FLAG_END:
            result.append((token & ~TokenFlag.FLAG_ALL, ''.join(buf)))
            buf.clear()
            prev_token = token
            break

        else:
            prev_token = token
            break

    if prev_token == TokenFlag.UNKNOWN:
        raise errors.ElkValueError('Syntax error - unknown token')

    return token, result


def _parse_char(c: str, prev_c: str, pos: TextPos, buf: List[str], prev_token: TokenFlag) -> None:

    _raise_if_no_char(c, prev_c)

    return _collect_token(c, prev_c, pos, buf, prev_token)
