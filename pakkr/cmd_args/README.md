## Experimental feature
Sometimes, arguments of a deeply nested Callable might need to come from the command line, but the argument parser is usually built outside of the pipelines, thus losing the direct link between the Callable's definition and the command line argument parser.
What if the command line arguments are specified along with the Callable? E.g.
```python
from argparse import ArgumentParser
from pakkr import Pipeline, returns
from pakkr.cmd_args.argument import argument
from pakkr.cmd_args.cmd_args import cmd_args


parser = ArgumentParser(prog="some_pipeline")

@cmd_args(argument('--config', help="config file to use"))
def read_config(config):
    return f'config: {config}'

pipeline = Pipeline(read_config)
pipeline.add_arguments(parser)

parser.parse_args(['-h'])
```
should print
```
usage: some_pipeline [-h] [--config CONFIG]

optional arguments:
  -h, --help       show this help message and exit
  --config CONFIG  config file to use
```
