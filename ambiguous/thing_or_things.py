import inspect

from .decorator import decorator

__all__ = ["thing_or_things"]


@decorator
def thing_or_things(fn, arg_name=None):
    sig = inspect.signature(fn)
    params = sig.parameters.values()
    varargs = [p.name for p in params if p.kind is p.VAR_POSITIONAL]
    named = [p for p in params if p.kind not in (p.VAR_POSITIONAL, p.VAR_KEYWORD)]

    if arg_name:
        if arg_name in varargs:
            raise NotImplementedError("can not use varargs")

        if arg_name not in [p.name for p in named]:
            raise ValueError(f"arg_name not in function signature: {arg_name}")
    else:
        # no args given, determine defaults

        if varargs:
            raise NotImplementedError(
                "please specify which arg to use, eg. @thing_or_things(<arg_name>)"
            )

        if not named:
            raise TypeError("function does not take arguments")

        # prefer positional args, falling back to keyword-only ones
        candidates = [p for p in named if p.kind is not p.KEYWORD_ONLY] or named
        required = [p for p in candidates if p.default is p.empty]

        if len(candidates) == 1:
            # grab first and only arg
            arg_name = candidates[0].name
        elif len(required) == 1:
            # if all args have defaults except one
            arg_name = required[0].name
        else:
            raise ValueError(
                "please specify which arg to use, eg. @thing_or_things(<arg_name>)"
            )

    def wrapper(*args, **kwargs):
        # bind like a real call, so the thing can be passed by keyword or default
        try:
            bound = sig.bind(*args, **kwargs)
        except TypeError as e:
            raise TypeError(f"{fn.__name__}(): {e}") from None
        bound.apply_defaults()

        thing_or_things = bound.arguments[arg_name]
        single_thing = not isinstance(thing_or_things, (list, set, tuple))
        things = [thing_or_things] if single_thing else list(thing_or_things)

        # replace thing_or_things arg and make function call
        bound.arguments[arg_name] = things
        res = fn(*bound.args, **bound.kwargs)

        if res is None:
            return

        # check return type
        if not isinstance(res, dict):
            raise TypeError(f"expected {dict}, found {type(res)}")

        thing_set = set(things)
        key_set = set(res.keys())

        # ensure all things are mapped
        missing = thing_set - key_set
        if missing:
            raise KeyError(f"missing things: {list(missing)}")

        # ensure there's no extra things
        extra = key_set - thing_set
        if extra:
            raise KeyError(f"extra things: {list(extra)}")

        # unpack as needed
        if single_thing:
            res = res[things[0]]

        return res

    return wrapper
