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


# works on methods too
@ambiguous
class Greeter:
  def __init__(self, name):
    self.name = name

  def hello(self, greeting='hello'):
    return '%s %s' % (greeting, self.name)

Greeter('bob').hello
> 'hello bob'
Greeter('bob').hello('hi')
> 'hi bob'

# or pick individual methods
# (stack above @classmethod / @staticmethod)
class Dog:
  @ambiguous
  def speak(self):
    return 'woof'

  @ambiguous
  @classmethod
  def species(cls):
    return cls.__name__.lower()

Dog().speak
> 'woof'
Dog.species
> 'dog'
```

Each access calls the function again, so changes to its result don't stick (appending to a returned list mutates a throwaway copy), and stateful results like iterators and context managers aren't supported.

`@decorator` treats a callable first positional argument as the function to decorate, so pass callable options by keyword, eg. `@on_error(handler=log)`.

----
[![installs](https://img.shields.io/pypi/dm/ambiguous.svg?label=installs)](https://pypi.org/project/ambiguous)
