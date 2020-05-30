ambiguous
======
A little flexibility makes life way easier.


### Install
```bash
pip install ambiguous
```


### Usage

#### decorator: because decorators should accept args too
```python
@decorator
def suffix(fn, str_='xyz'):
    '''add a suffix to the result of the wrapped fn'''
    def wrapper(*args, **kwargs):
        return '%s_%s' % (fn(*args, **kwargs), str_)
    return wrapper

@suffix
def abc(): return 'abc'

abc()
> 'abc_xyz'


@suffix('123')
def count(repeat=1): return '0' * repeat

count()
> '0_123'
count(3)
> '000_123'
```

#### thing_or_things: merges gets and multigets

```python
@thing_or_things
def itself(args):
  return { x : x for x in args }

itself(1)
> 1
itself([1, 2])
> { 1 : 1, 2 : 2 }


# specified argument
@thing_or_things('args')
def prefix(prefix, args):
  return { x : "%s_%s" % (prefix, x) for x in args }

prefix('abc', [1, 2])
> { 1 : 'abc_1', 2 : 'abc_2' }


# works with default args
@thing_or_things
def multiply(args, factor=1):
  return { x : x * factor for x in args }

multiply(2)
> 2
multiply(2, factor=2)
> 4
multiply([1, 2], factor=3)
> { 1 : 3, 2 : 6 }
```


#### what, parentheses optional?!   (warning: still highly experimental)
```python
import ambiguous

@ambiguous
def foo():
  return 'foo'

foo
> 'foo'
foo()
> 'foo'
foo + 'abc'
> 'fooabc'
```

----
[![installs](https://img.shields.io/pypi/dm/ambiguous.svg?label=installs)](https://pypi.org/project/ambiguous)
