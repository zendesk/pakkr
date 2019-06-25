from argparse import ArgumentParser


class _Argument:
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def __call__(self, parser: ArgumentParser) -> ArgumentParser:
        parser.add_argument(*self.args, **self.kwargs)
        return parser


def argument(*args, **kwargs) -> _Argument:
    return _Argument(*args, **kwargs)
