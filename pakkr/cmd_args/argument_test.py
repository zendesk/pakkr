from mock import MagicMock
from .argument import argument, _Argument


def test_argument_class():
    arg = _Argument('-c', '--config', desc="config file")
    assert arg.args == ('-c', '--config')
    assert arg.kwargs == dict(desc="config file")

    mock_parser = MagicMock()
    arg(mock_parser)
    mock_parser.add_argument.assert_called_once_with('-c', '--config', desc="config file")


def test_argument_fn():
    arg = argument('-c', '--config', desc="config file")

    assert isinstance(arg, _Argument)
    assert arg.args == ('-c', '--config')
    assert arg.kwargs == dict(desc="config file")
