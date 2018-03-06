ambiguous
======
because magic makes life more easy


### Install
```pip install ambiguous```


### Usage
#### thing_or_things: blurring the line between gets and multigets

```
@ambiguous.thing_or_things
def itself(args):
  return { x : x for x in args }

itself(1)
> 1
itself([1, 2])
> { 1 : 1, 2 : 2 }
itself(1, 2, 3)
> { 1 : 1, 2 : 2, 3 : 3 }
  

# also accepts keyword arguments
@ambiguous.thing_or_things
def multiply(args, factor=1):
  return { x : x * factor for x in args }

multiply(2, factor=2)
> 4
multiply(1, 2, factor=3)
> { 1 : 3, 2 : 6 }


# and an offset
@ambiguous.thing_or_things(offset=1)
def prefix(prefix, args):
  return { x : "%s%s" % (prefix, x) for x in args }

prefix('abc', 1, 2)
> { 1 : 'abc1', 2 : 'abc2' }
```

#### what, parentheses optional?!
```
import ambiguous

@ambiguous
def foo():
  return 'foo'

print foo
print foo()
print foo + 'abc'
```

### Caveats
- Does not work with functions returning objects not subclassing `object`.
