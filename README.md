ambiguous
======

#### Install
```pip install ambiguous```


#### Usage
```
import ambiguous

@ambiguous
def foo():
  return 'foo'


print foo
print foo()
print foo + 'abc'

```

#### Caveats
- Does not work with functions returning objects not subclassing `object`.
