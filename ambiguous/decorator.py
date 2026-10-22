from functools import update_wrapper, wraps
from inspect import isfunction

__all__ = ["decorator"]


def _name(fn):
    # callable objects and partials have no __name__
    return getattr(fn, "__name__", None) or repr(fn)


def decorator(decorator_fn):
    """
    Let a decorator be used bare or with arguments.

    `decorator_fn` takes the target first, then its own options:

        @decorator
        def power(fn, exponent=2): ...

        @power                  # power(f)
        @power(3)               # power(f, 3)
        @power(exponent=3)      # power(f, exponent=3)

    The first positional arg being callable is what marks it as the target.
    """

    @wraps(decorator_fn)
    def wrapper(*args, **kwargs):
        if args and callable(args[0]):
            decorated = decorator_fn(*args, **kwargs)

            # mask signature, unless the target was returned as-is, which
            # would make it its own __wrapped__
            if isfunction(decorated) and decorated is not args[0]:
                update_wrapper(decorated, args[0])

            return decorated

        # no target yet: accumulate args and kwargs until it arrives
        @wraps(decorator_fn)
        def collect(*more_args, **more_kwargs):
            if more_args and callable(more_args[0]):
                if args and len(more_args) > 1:
                    raise ValueError(
                        f"{_name(decorator_fn)}(): ambiguous arg order, pass "
                        "all args in one call and then the function alone"
                    )

                # the target goes first, ahead of the args collected so far
                new_args = more_args + args
            else:
                new_args = args + more_args

            return wrapper(*new_args, **{**kwargs, **more_kwargs})

        return collect

    return wrapper
