import pytest
from mock import call, MagicMock
from .argument import argument
from .cmd_args import ATTR_CMD_ARGS, cmd_args


def test_add_attribute():
    @cmd_args(argument('--x'))
    def fn(x):
        return 'hello'

    assert hasattr(fn, ATTR_CMD_ARGS)
    assert fn(1) == 'hello'


def test_add_attribute_to_class():
    @cmd_args(argument('--x'))
    class Test:
        def __call__(self, x):
            return 'hello'

    test = Test()
    assert hasattr(test, ATTR_CMD_ARGS)
    assert test(1) == 'hello'


def test_add_arguments():
    @cmd_args(argument('--config'), argument('--test'))
    def fn(config, test):
        return 'hello'

    assert fn(1, 2) == 'hello'
    mock_parser = MagicMock()
    assert getattr(fn, ATTR_CMD_ARGS)(mock_parser) == mock_parser
    mock_parser.add_argument.assert_has_calls([call('--config'), call('--test')])


def test_add_arguments_class():
    @cmd_args(argument('--config'), argument('--test'))
    class Test:
        def __call__(self, config, test):
            return 'hello'

    test = Test()
    assert test(1, 2) == 'hello'
    mock_parser = MagicMock()
    assert getattr(test, ATTR_CMD_ARGS)(mock_parser) == mock_parser
    mock_parser.add_argument.assert_has_calls([call('--config'), call('--test')])


def test_double_decorated():
    with pytest.raises(RuntimeError) as e:
        @cmd_args(argument('--config'))
        @cmd_args(argument('--test'))
        def fn(config, test):
            return 'hello'  # pragma: no cover

    assert str(e.value).startswith('__pakkr_cmd_args__ has been set on ')


def test_argument_mismatch():
    with pytest.raises(RuntimeError) as e:
        @cmd_args(argument('--x'))
        def fn():
            return 'hello'  # pragma: no cover
    assert str(e.value) == "'x' is not an argument of the Callable."

    with pytest.raises(RuntimeError) as e:
        @cmd_args(argument('--x'))
        def fn(*x):
            return 'hello'  # pragma: no cover
    assert str(e.value) == "'x' should be a positional or keyword argument of the Callable."
