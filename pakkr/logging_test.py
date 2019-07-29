from mock import MagicMock, patch, call
from pakkr.logging import IndentationAdapter, log_timing


def test_indentAdapter():
    adapter = IndentationAdapter(None, {'indent': 1,
                                        'identifier': "some_obj"})

    kwargs = {'x': 1}
    assert adapter.process("hello", kwargs) == ("    some_obj - hello", kwargs)


@patch('pakkr.logging.time')
def test_log_timing(mock_time):
    mock_time.time.side_effect = [1.0, 9.0]
    mock_logger = MagicMock()
    mock_step = MagicMock()
    with log_timing(mock_logger):
        mock_step.run(x=1)

    mock_step.run.assert_called_with(x=1)
    mock_logger.info.assert_has_calls([call("starting"), call("finished (took 8.000s)")])


def test_log_timing_suppressed():
    mock_logger = MagicMock()
    mock_step = MagicMock()
    with log_timing(mock_logger, True):
        mock_step.run(x=1)
    mock_step.run.assert_called_with(x=1)
    mock_logger.assert_not_called()
