import enum
from typing import List, Tuple

from elkconfdparser import errors


class TokenFlag(enum.Enum):
    UNKNOWN = enum.auto()
    SPACE = enum.auto()
    COMMENT = enum.auto()
    IDENTIFIER = enum.auto()
    STRING = enum.auto()
    NUMBER = enum.auto()
    OPERATOR = enum.auto()
    END = enum.auto()


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


def parse(text):

    buf: List[str] = []
    pos: TextPos = TextPos()
    prev_c: str = '\n'
    token = TokenFlag.UNKNOWN

    for c in text:
        token, tokens = _parse_char(c, prev_c, pos, buf, token)
        prev_c = c

        for x in tokens:
            if x[0] != TokenFlag.SPACE:
                print(f'{pos.toTuple()}\t{x[0].name[:6]}  {x[1]}')


def _raise_if_no_char(c: str, prev_c: str) -> None:

    if len(c) != 1:
        raise errors.ElkValueError('Arg "c" expected to be a string contained only one char')

    if len(prev_c) != 1:
        raise errors.ElkValueError('Arg "prev_c" expected to be a string contained only one char')


def _tokenise(c: str, prev_c: str, buf: List[str], prev_token: TokenFlag) -> List:  # noqa: C901

    current = TokenFlag.UNKNOWN

    if prev_token in (TokenFlag.UNKNOWN, TokenFlag.END):
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

        elif c in '={}[],':
            current = TokenFlag.OPERATOR

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

    elif prev_token == TokenFlag.STRING:

        if c == '\n':
            raise errors.ElkSyntaxError('Syntax error - string without closing quotes')

        elif c == '"' and prev_c != '\\':
            current = TokenFlag.END

        else:
            current = prev_token

        buf.append(c)

    elif prev_token == TokenFlag.NUMBER:
        if c.isnumeric():  # no need to use c.isidentifier as we already know that it's not a first symbol
            current = prev_token

    elif prev_token == TokenFlag.OPERATOR:

        if prev_c == '=':

            if c == '>':
                current = TokenFlag.END
                buf.append(c)
            else:
                raise errors.ElkSyntaxError('Syntax error - unknown operator')

    else:
        raise errors.ElkValueError('Syntax error - unknown token', prev_token)

    return current


def _parse_char(c: str, prev_c: str, pos: TextPos, buf: List[str], prev_token: TokenFlag) -> None:

    _raise_if_no_char(c, prev_c)

    pos.inc(prev_c == '\n')

    result = []
    token = _tokenise(c, prev_c, buf, prev_token)

    if token == TokenFlag.END:
        result.append((prev_token, ''.join(buf)))
        buf.clear()

    elif token == TokenFlag.UNKNOWN:
        result.append((prev_token, ''.join(buf)))
        buf.clear()

        token = _tokenise(c, prev_c, buf, token)
        
        result.append((prev_token, ''.join(buf)))
        buf.clear()

    return token, result
