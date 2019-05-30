import sys
from collections import OrderedDict
from pakkr.exception import (exception_context,
                             exception_handler,
                             PakkrError,
                             pakkr_exchandler,
                             summarise_dictionary)
from mock import DEFAULT, patch, MagicMock, PropertyMock


def test_summarise_dictionary():
    ordered_dict = OrderedDict([("a", 1), ("b", "hello"), ("c", {"d": 1}), ("d", [1, 2])])
    actual = summarise_dictionary(ordered_dict)
    assert actual == "{a: <class 'int'>, b: <class 'str'>, c: <class 'dict'>, d: <class 'list'>}"


def test_exception_context():
    assert exception_context('"my_step"<StepClass>',
                             [1, "a"],
                             {"numbers": [1, 2]}, {"dictionary": {"x": 1, "y": 2}}) \
        == \
        ("\tinside \"my_step\"<StepClass> executed with "
         "(<class 'int'>, <class 'str'>, numbers=<class 'list'>)\n"
         "\t\tavailable meta {dictionary: <class 'dict'>}")


def test_exception_handler():
    mock_handler = MagicMock()
    with exception_handler(mock_handler):
        assert sys.excepthook == mock_handler
    assert sys.excepthook == sys.__excepthook__


def test_pakkr_exchandler():
    mock_ex = MagicMock()
    mock_ex.__cause__ = None
    mock_ex.__traceback__ = PropertyMock()

    with patch("pakkr.exception.traceback") as mock_traceback:
        pakkr_exchandler(MagicMock, mock_ex, None)
        mock_traceback.print_exception.assert_called_with(MagicMock,
                                                          mock_ex,
                                                          mock_ex.__traceback__,
                                                          chain=False)

    mock_ex.__cause__ = PropertyMock()
    mock_ex.__cause__.__traceback__ = PropertyMock
    with patch.multiple("pakkr.exception", traceback=DEFAULT,
                                           print=DEFAULT) as mocks:  # noqa: E999
        mock_traceback = mocks['traceback']
        mock_print = mocks['print']

        pakkr_exchandler(MagicMock, mock_ex, None)
        mock_traceback.print_exception.assert_called_with(MagicMock,
                                                          mock_ex.__cause__,
                                                          mock_ex.__cause__.__traceback__,
                                                          chain=False)
        mock_ex.pakkr_stacks.assert_called_once()
        mock_print.assert_called_with(mock_ex.pakkr_stacks.return_value)


def test_pakkr_error():
    error = PakkrError("some error", "stack #1")
    error.append_stack("stack #2")

    assert str(error) == "some error\nstack #1\nstack #2"
