# PAKKR
Python pipeline utility library

# Description
In the process of building machine learning things at Zendesk, we have noticed that a lot of the steps are sequential where later steps rely on outputs of previous steps. Because Python functions only return a single value (`return` with multiple values are returned as a tuple), deconstructing and keeping track of return values becomes tedious for long sequences of steps, especially when inputs are not returned from the immediately previous step.

PAKKR is an utility created to remediate these pain points; it provides the user with a way to specify how return values should be interpreted and optionally caches results and injects them in later steps automatically.

# Install from PyPi
```bash
pip install pakkr
```

# Install from source
```bash
git clone git@github.com:zendesk/pakkr.git
cd pakkr
python setup.py install
```

# Usage
```python
from pakkr import Pipeline, returns

@returns(int, original_num_as_string=str)  # this function returns an integer and insert original_num_as_string into the meta cache
def times_two(n):
  return n*2, {'original_num_as_string': str(n)}

@returns(int, int)  # this functions returns two integers and will be passed on as two arguments
def plus_five_and_three(n):
  return n + 5, n + 3

@returns(str)
def summary(a, b, original_num_as_string):  # a and b are passed in as positional arguments,
                                            # but original_num_as_string would be injected from the meta cache
  return f'Original input was {original_num_as_string} and it became {str(a)} and {str(b)} after processing'

pipeline = Pipeline(times_two, plus_five_and_three, summary, _name='process_int')
print(pipeline(3))
```
Running the above code should print:
```
Original input was 3 and it became 11 and 9 after processing
```

## What's going on?
`returns` is used to indicate how the return values should be interpreted; `@returns(int, str, x=bool)` means the `Callable` should be returning something like `return 10, 'hello', {'x': True}` and the `10` and `'hello'` will be passed as two positional arguments into the next `Callable` while `x` would be cached in the meta space and be injected if any following `Callable`s require `x` but not being given as positional argument from the previous `Callable`.


# Development
This project uses `tox` to manage testing on multiple Python versions assuming the required Python versions are available.
```
git clone git@github.com:zendesk/pakkr.git
cd pakkr
pip install tox
tox
```

Optionally, uses `pyenv` and `pipenv` to manage Python installation and development dependencies.
```
git clone git@github.com:zendesk/pakkr.git
cd pakkr

# Install pyenv, see instructions in https://github.com/pyenv/pyenv
# Install Python versions supported by pakkr if not available locally
# pyenv install 3.6.10
# pyenv install 3.7.6
# pyenv install 3.8.1

# Set available Python verions
pyenv local 3.6.10 3.7.6 3.8.1

# Install pipenv
pip install pipenv
pipenv sync --dev

# Run tests
pipenv run tox
```

# Reporting Bugs
Please [raise an isses](https://github.com/zendesk/pakkr/issues/new) in GitHub.


# Contributing
Improvements are always welcome. Please follow these steps to contribute

1. Submit a Pull Request with a detailed explanation of changes
2. Receive approval from maintainers
3. Maintainers will merge your changes

# License
Use of this software is subject to important terms and conditions as set forth in the [LICENSE](https://github.com/zendesk/pakkr/blob/master/LICENSE) file.
