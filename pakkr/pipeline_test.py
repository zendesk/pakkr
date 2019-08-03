import pytest
from mock import call, MagicMock, Mock, patch
from pakkr import Pipeline, returns
from pakkr.cmd_args.cmd_args import cmd_args
from pakkr.cmd_args.argument import argument
from pakkr.pipeline import _identifier, _get_pakkr_depth
from pakkr.exception import PakkrError
from collections import namedtuple


_FrameInfo = namedtuple('_FrameInfo', ('frame', 'function'))
_Frame = namedtuple('_Frame', ('f_locals'))


def test_pipeline():
    @returns(str)
    def say_hello():
        return "hello"

    @returns(offset=int)
    def meta_offset(s):
        assert s == "hello"
        return {'offset': 1}

    @returns(int)
    def count(s, offset):
        return len(s) + offset

    def with_world(offset):
        return offset, "world"

    @returns(str)
    def second_item(tup):
        return tup[1]

    pipeline = Pipeline(say_hello, meta_offset)
    assert pipeline() is None

    pipeline = Pipeline(meta_offset, say_hello, count)
    assert pipeline("hello") == 6

    pipeline = Pipeline(meta_offset, say_hello, count, with_world)
    assert pipeline("hello") == (6, "world")

    pipeline = Pipeline(with_world, second_item)
    assert pipeline(offset=1) == "world"


def test_pipeline_run_step():
    def say_hello():
        return "hello"

    pipeline = Pipeline(say_hello)

    with patch.object(pipeline, '_run_step', wraps=pipeline._run_step) as spy:
        pipeline()
        spy.assert_called_with(((), {}), say_hello, indent=1)


def test_pipeline_step_exception():
    def throw():
        raise Exception("something is wrong")

    pipeline = Pipeline(throw)
    with pytest.raises(PakkrError) as e:
        pipeline()
    assert str(e.value).startswith("something is wrong")


def test_nested_pipeline():
    inner_step = returns(str, a=bool)(lambda i: ("inner_" + str(i), {'a': True}))
    inner_pipeline = Pipeline(inner_step, _name="inner_pipeline")

    def outer_step(s, a, x=0):
        return (not a, s[::-1], x)

    outer_pipeline = Pipeline(inner_pipeline, outer_step, _name="outer_pipeline")

    assert outer_pipeline(100, x=-1) == (False, "001_renni", -1)


def test_nested_pipeline_step_exception():
    def throw():
        raise Exception("something is wrong")

    pipeline = Pipeline(Pipeline(throw))
    with pytest.raises(PakkrError) as e:
        pipeline()
    assert str(e.value).startswith("something is wrong")


def test_calling_pipeline_inside_a_step():
    @returns(int, x=str)
    def inner_step():
        return 1, {'x': 'hello'}

    callable = Pipeline(inner_step)

    @returns(int)
    def use_callable():
        result = callable()
        assert result == 1
        return result

    pipeline = Pipeline(use_callable)
    assert pipeline() == 1


def test_downcast_pipeline():
    def missing_x(x):
        return "should not work"  # pragma: no cover

    def say_hello(y):
        return "hello and y = " + y

    @returns(bool, x=int, y=str)
    def blah():
        return True, {"x": 1, "y": "abc"}

    inner_pipeline = Pipeline(blah)
    assert inner_pipeline() is True

    downcasted_pipeline = returns(y=str)(inner_pipeline)

    pipeline = Pipeline(downcasted_pipeline, say_hello)
    assert pipeline() == "hello and y = abc"

    pipeline = Pipeline(downcasted_pipeline, missing_x)
    with pytest.raises(Exception) as e:
        pipeline()
    assert type(e.value.__cause__) == RuntimeError
    assert str(e.value.__cause__).startswith("'x' is required but not available.")

    downcasted_pipeline = returns()(inner_pipeline)
    pipeline = Pipeline(downcasted_pipeline, lambda: "hello")
    assert pipeline() == "hello"

    downcasted_pipeline = returns(bool)(inner_pipeline)
    pipeline = Pipeline(downcasted_pipeline, lambda x: not x)
    assert pipeline() == False


def test_step_instance_method():
    @returns(str, a=bool)
    class Step:
        def __call__(self, x):
            return str(x), {'a': False}

    pipeline = Pipeline(Step())
    assert pipeline(x=100) == "100"
    assert pipeline(100) == "100"

    class Step:
        @returns(str, a=bool)
        def some_func(self, x):
            return str(x), {'a': False}

    pipeline = Pipeline(Step().some_func)
    assert pipeline(x=100) == "100"
    assert pipeline(100) == "100"

def test_step_class_method():
    class Step:
        @classmethod
        @returns(str, a=bool)
        def some_func(cls, x):
            return str(x), {'a': False}

    pipeline = Pipeline(Step.some_func)
    assert pipeline(x=100) == "100"
    assert pipeline(100) == "100"


def test_step_static_method():
    class Step:
        @staticmethod
        @returns(str, a=bool)
        def some_func(x):
            return str(x), {'a': False}

    pipeline = Pipeline(Step.some_func)
    assert pipeline(x=100) == "100"
    assert pipeline(100) == "100"


def test_no_return():
    pipeline = returns()(Pipeline(lambda: "hello"))
    assert pipeline() is None

    pipeline = returns()(Pipeline(returns(x=int)(lambda: {'x': 1})))
    assert pipeline() is None


def test_identifier_name():
    class PrivateName:
        def __init__(self, _name):
            super().__init__()
            self._name = _name

    private_name = PrivateName(_name="secret_name")
    assert _identifier(private_name) == '"secret_name"<PrivateName>'


def test_identifier_attr():
    pipeline = Pipeline(lambda: 1, _name="cool_pipeline")
    assert _identifier(pipeline) == '"cool_pipeline"<Pipeline>'


def test_identifier__name():
    def normal_func():
        pass  # pragma: no cover
    assert _identifier(normal_func) == '"normal_func"<function>'


def test_identifier_unnamed():
    d = dict()
    assert _identifier(d) == '"unnamed_{}"<dict>'.format(id(d))


def test_add_arguments():
    @cmd_args(argument('--config'))
    def test(config):
        return f'config: {config}'

    pipeline = Pipeline(test)
    mock_parser = MagicMock()
    parser = pipeline.add_arguments(mock_parser)
    assert parser is mock_parser
    mock_parser.add_argument.assert_called_once_with('--config')
    result = pipeline(config='some_file')
    assert result == 'config: some_file'


@patch('pakkr.pipeline.inspect')
def test_get_pakkr_depth_0(mock_inspect):
    pipeline_1 = Mock(spec=Pipeline)

    mock_stack = [_FrameInfo(_Frame({'self': pipeline_1}), '__call__'),
                  _FrameInfo(_Frame({}), 'some_external_func_1'),
                  _FrameInfo(_Frame({'self': Mock()}), 'some_method'),
                  _FrameInfo(_Frame({}), 'some_external_func_2')]
    mock_inspect.stack.return_value = mock_stack
    depth, used_as_step = _get_pakkr_depth(pipeline_1)
    assert depth == 0
    assert used_as_step is False


@patch('pakkr.pipeline.inspect')
def test_get_pakkr_depth_2_as_step(mock_inspect):
    pipeline_1 = Mock(spec=Pipeline)
    pipeline_2 = Mock(spec=Pipeline)
    pipeline_3 = Mock(spec=Pipeline)

    mock_stack = [_FrameInfo(_Frame({'self': pipeline_1}), '__call__'),
                  _FrameInfo(_Frame({'self': pipeline_2}), '_run_step'),
                  _FrameInfo(_Frame({'self': pipeline_2}), '__call__'),
                  _FrameInfo(_Frame({'self': pipeline_3}), '_run_step'),
                  _FrameInfo(_Frame({'self': pipeline_3}), '__call__'),
                  _FrameInfo(_Frame({}), 'some_external_func_1')]
    mock_inspect.stack.return_value = mock_stack

    depth, used_as_step = _get_pakkr_depth(pipeline_1)
    assert depth == 2
    assert used_as_step is True


@patch('pakkr.pipeline.inspect')
def test_get_pakkr_depth_1_as_callable(mock_inspect):
    pipeline_1 = Mock(spec=Pipeline)
    pipeline_2 = Mock(spec=Pipeline)

    mock_stack = [_FrameInfo(_Frame({'self': pipeline_1}), '__call__'),
                  _FrameInfo(_Frame({}), 'some_external_func_1'),
                  _FrameInfo(_Frame({'self': pipeline_2}), '_run_step'),
                  _FrameInfo(_Frame({'self': pipeline_2}), '__call__'),
                  _FrameInfo(_Frame({}), 'some_external_func_2')]
    mock_inspect.stack.return_value = mock_stack

    depth, used_as_step = _get_pakkr_depth(pipeline_1)
    assert depth == 1
    assert used_as_step is False


@patch('pakkr.pipeline.inspect')
def test_get_pakkr_depth_not_found_no_pipeline(mock_inspect):
    pipeline_1 = Mock(spec=Pipeline)

    mock_stack = [_FrameInfo(_Frame({}), 'some_external_func_1'),
                  _FrameInfo(_Frame({}), 'some_external_func_2')]
    mock_inspect.stack.return_value = mock_stack

    depth, used_as_step = _get_pakkr_depth(pipeline_1)
    assert depth == -1
    assert used_as_step is None


@patch('pakkr.pipeline.inspect')
def test_get_pakkr_depth_not_found_with_pipeline(mock_inspect):
    pipeline_1 = Mock(spec=Pipeline)
    pipeline_2 = Mock(spec=Pipeline)

    mock_stack = [_FrameInfo(_Frame({}), 'some_external_func_1'),
                  _FrameInfo(_Frame({}), 'some_external_func_2'),
                  _FrameInfo(_Frame({'self': pipeline_2}), '_run_step'),
                  _FrameInfo(_Frame({'self': pipeline_2}), '__call__')]
    mock_inspect.stack.return_value = mock_stack

    depth, used_as_step = _get_pakkr_depth(pipeline_1)
    assert depth == -1
    assert used_as_step is None


@patch('pakkr.pipeline.inspect')
def test_get_pakkr_depth_1_as_step_in_between(mock_inspect):
    pipeline_1 = Mock(spec=Pipeline)
    pipeline_2 = Mock(spec=Pipeline)
    pipeline_3 = Mock(spec=Pipeline)

    mock_stack = [_FrameInfo(_Frame({'self': pipeline_1}), '__call__'),
                  _FrameInfo(_Frame({'self': pipeline_2}), '_run_step'),
                  _FrameInfo(_Frame({'self': pipeline_2}), '__call__'),
                  _FrameInfo(_Frame({'self': pipeline_3}), '_run_step'),
                  _FrameInfo(_Frame({'self': pipeline_3}), '__call__'),
                  _FrameInfo(_Frame({}), 'some_external_func_1')]
    mock_inspect.stack.return_value = mock_stack

    depth, used_as_step = _get_pakkr_depth(pipeline_2)
    assert depth == 1
    assert used_as_step is True


@patch('pakkr.pipeline.inspect')
def test_get_pakkr_depth_1_as_callable_in_between(mock_inspect):
    pipeline_1 = Mock(spec=Pipeline)
    pipeline_2 = Mock(spec=Pipeline)
    pipeline_3 = Mock(spec=Pipeline)

    mock_stack = [_FrameInfo(_Frame({'self': pipeline_1}), '__call__'),
                  _FrameInfo(_Frame({'self': pipeline_2}), '_run_step'),
                  _FrameInfo(_Frame({'self': pipeline_2}), '__call__'),
                  _FrameInfo(_Frame({}), 'some_external_func_1'),
                  _FrameInfo(_Frame({'self': pipeline_3}), '_run_step'),
                  _FrameInfo(_Frame({'self': pipeline_3}), '__call__'),
                  _FrameInfo(_Frame({}), 'some_external_func_2')]
    mock_inspect.stack.return_value = mock_stack

    depth, used_as_step = _get_pakkr_depth(pipeline_2)
    assert depth == 1
    assert used_as_step is False
