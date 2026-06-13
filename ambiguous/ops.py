#!/usr/bin/env python

"""
Generage a list of object methods that can be overridden
"""


import operator


op_exceptions = set([
  '__call__',
  '__class__',
  '__doc__',
  '__name__',
  '__new__',

  # module attributes that leak in from scanning the `operator` module below,
  # not actual operators
  '__all__',
  '__builtins__',
  '__cached__',
  '__file__',
  '__loader__',
  '__package__',
  '__spec__',
])

objs = [
  dict,
  float,
  int,
  list,
  object,
  operator,
  str,
]


ops = set()
for obj in objs:
  for op in dir(obj):
    if op.startswith('__') and op.endswith('__') and op not in op_exceptions:
      ops.add(op)


if __name__ == '__main__':
    for op in sorted(ops):
      print(op)
