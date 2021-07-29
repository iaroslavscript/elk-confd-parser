import enum
import sys


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


def parse(text, start=0, end=None):

    if end is None:
        end = len(text)-1

    result = _parse(text, start, end)[0]

    return result


def _parse(text, start, end):  # noqa: C901  # FIXME

    block = _BlockType.NONE
    root = []
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
            if c == "\"":
                action |= _ParserAction.DROP_VALUE

        elif c == "\"":
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
        root.append({stack.pop(): stack.pop()})
        stack.clear()


def display(data):

    import json

    print(json.dumps(data, indent=4, sort_keys=True))


def main(filename):

    with open(filename) as f:

        text = f.read()
        data = parse(text)

        assert len(data)

        data_output = data[0].get('output')

        assert data_output

        data_elasticsearch = list(filter(lambda x: x.get('elasticsearch'), data_output))

        assert data_output

        for item in data_output:

            data_elasticsearch = item.get('elasticsearch')

            if data_elasticsearch is not None:

                host_url = list(filter(lambda x: x.get('hosts'), data_elasticsearch))
                user = list(filter(lambda x: x.get('user'), data_elasticsearch))
                password = list(filter(lambda x: x.get('password'), data_elasticsearch))

                assert all((host_url, user, password))


if __name__ == '__main__':

    main(sys.argv[1])
