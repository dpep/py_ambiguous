import inspect

from .decorator import _name, decorator

__all__ = ["thing_or_things"]


@decorator
def thing_or_things(fn, arg_name=None):
    """
    Let a function that maps many things take just one, eg. get vs multiget.

    The wrapped function always receives a list and must return a dict keyed
    by exactly those things, or None. Called with a single thing (anything
    but a list, set or tuple), the caller gets back just that thing's value.

    The thing is the only parameter, or the only one without a default.
    Otherwise name it, eg. @thing_or_things("ids").
    """
    name = _name(fn)
    sig = inspect.signature(fn)
    params = sig.parameters.values()
    varargs = [p.name for p in params if p.kind is p.VAR_POSITIONAL]
    varkw = [p.name for p in params if p.kind is p.VAR_KEYWORD]
    named = [p for p in params if p.kind not in (p.VAR_POSITIONAL, p.VAR_KEYWORD)]

    if arg_name:
        if arg_name in varargs + varkw:
            stars = "*" if arg_name in varargs else "**"
            raise NotImplementedError(
                f"{name}(): {stars}{arg_name} can't be the thing, take a list instead"
            )

        if arg_name not in [p.name for p in named]:
            raise ValueError(f"{name}() has no parameter {arg_name!r}")
    else:
        if varargs:
            raise NotImplementedError(
                f"{name}() takes *{varargs[0]}, so name the thing, "
                "eg. @thing_or_things('<arg_name>')"
            )

        if not named:
            raise TypeError(f"{name}() takes no arguments, so has no thing")

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
            # on methods, the first param is self / cls, never the thing
            hint = next(
                (p.name for p in candidates if p.name not in ("self", "cls")),
                candidates[0].name,
            )
            raise ValueError(
                f"{name}(): can't tell which parameter is the thing, "
                f"name it, eg. @thing_or_things({hint!r})"
            )

    def wrapper(*args, **kwargs):
        # bind like a real call, so the thing can be passed by keyword or default
        try:
            bound = sig.bind(*args, **kwargs)
        except TypeError as e:
            raise TypeError(f"{name}(): {e}") from None
        bound.apply_defaults()

        arg = bound.arguments[arg_name]
        single_thing = not isinstance(arg, (list, set, tuple))
        things = [arg] if single_thing else list(arg)

        bound.arguments[arg_name] = things
        res = fn(*bound.args, **bound.kwargs)

        if res is None:
            return

        if not isinstance(res, dict):
            raise TypeError(
                f"{name}() must return a dict or None, got {type(res).__name__}"
            )

        thing_set = set(things)
        key_set = set(res)

        missing = thing_set - key_set
        if missing:
            raise KeyError(f"{name}() result is missing things: {list(missing)}")

        extra = key_set - thing_set
        if extra:
            raise KeyError(f"{name}() result has extra keys: {list(extra)}")

        if single_thing:
            res = res[things[0]]

        return res

    return wrapper
