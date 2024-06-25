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
  '''take function results and raise to an exponent'''
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

#### thing_or_things: combine gets and multigets

```python
from ambiguous import thing_or_things

@thing_or_things
def itself(args):
  return { x : x for x in args }

itself(1)
> 1
itself([1, 2])
> { 1 : 1, 2 : 2 }


# specify which argument
@thing_or_things('args')
def prefix(prefix, args):
  return { x : "%s_%s" % (prefix, x) for x in args }

prefix('abc', [1, 2])
> { 1 : 'abc_1', 2 : 'abc_2' }
```


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
```

----
[![installs](https://img.shields.io/pypi/dm/ambiguous.svg?label=installs)](https://pypi.org/project/ambiguous)
