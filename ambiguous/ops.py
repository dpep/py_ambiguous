"""
Special methods that AmbiguousFunction delegates to the wrapped result
"""

_excluded = {
    # owned by AmbiguousFunction itself
    "__call__",
    "__class__",
    "__doc__",
    "__new__",
    # each access yields a fresh result, so there is nothing to mutate in
    # place; without these, `x += y` falls back to `x = x + y`
    "__iadd__",
    "__imul__",
    "__ior__",
}

ops = {
    op
    for obj in (complex, dict, float, int, list, object, str)
    for op in dir(obj)
    if op.startswith("__") and op.endswith("__") and op not in _excluded
}

# protocols that no builtin type above implements
ops |= {"__fspath__", "__matmul__", "__rmatmul__"}
