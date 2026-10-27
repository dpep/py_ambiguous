ambiguous
======
flexibility when you need it


### Install
```bash
pip install ambiguous
```


### Usage

#### decorator: allow decorators to accept arguments
```python
from ambiguous import decorator


@decorator
def power(fn, exponent=2):
    """raise the wrapped function's result to an exponent"""
    return lambda x: fn(x) ** exponent


@power
def squared(x): return x

squared(2)
> 4


@power(exponent=3)
def cubed(x): return x

cubed(2)
> 8
```

The first positional arg being callable is what marks it as the target, so options can't be callables.

#### thing_or_things: combine gets and multigets

```python
from ambiguous import thing_or_things

@thing_or_things
def itself(args):
    return {x: x for x in args}

itself(1)
> 1
itself([1, 2])
> {1: 1, 2: 2}


# specify which argument
@thing_or_things('args')
def prefix(prefix, args):
    return {x: f"{prefix}_{x}" for x in args}

prefix('abc', [1, 2])
> {1: 'abc_1', 2: 'abc_2'}
```

A list, tuple, set or frozenset is many things; anything else, including a string, is one. The function must return a value for every thing, else KeyError. On methods, `self` / `cls` is never the thing.


#### optional parentheses  (warning: still experimental)
```python
import ambiguous

@ambiguous
def foo():
    return 'foo'

# the usual
foo()
> 'foo'

# ?!?
foo
> 'foo'
foo + 'abc'
> 'fooabc'


# works on classes too
@ambiguous
class Greeter:
    def __init__(self, name):
        self.name = name

    def hello(self, greeting='hello'):
        return f'{greeting} {self.name}'

Greeter('bob').hello
> 'hello bob'
Greeter('bob').hello('hi')
> 'hi bob'


# or on individual methods, stacked above @classmethod / @staticmethod
class Config:
    @ambiguous
    @classmethod
    def name(cls):
        return cls.__name__

Config.name
> 'Config'
```

An ambiguous function is a stand-in that acts like its result, not the result itself. Code that checks the type, eg. `json.dumps(foo)` or `datetime.fromtimestamp(now)`, needs the call: `foo()`.

----
[![installs](https://img.shields.io/pypi/dm/ambiguous.svg?label=installs)](https://pypi.org/project/ambiguous)
