from functools import wraps

from fumus.exceptions.exception import IllegalStateError

TERMINAL_FUNCTIONS = [
    "for_each",
    "reduce",
    "count",
    "min",
    "max",
    "sum",
    "average",
    "find_first",
    "find_any",
    "take_first",
    "take_last",
    "take_nth",
    "any_match",
    "all_match",
    "none_match",
    "compare_with",
    "all_equal",
    "quantify",
    "group_by",
    "collect",
    "to_list",
    "to_tuple",
    "to_set",
    "to_dict",
    "to_string",
]


def pre_call(function_decorator):
    def decorator(cls):
        for name, obj in vars(cls).items():
            if callable(obj):
                setattr(cls, name, function_decorator(obj))
        return cls

    return decorator


def handle_consumed(func):
    @wraps(func)
    def wrapper(*args, **kw):
        from fumus.queries.query import Query

        query = args[0] if args else None
        if not (query and isinstance(query, Query)):
            return func(*args, **kw)

        is_consumed = getattr(query, "_is_consumed", None)
        if is_consumed and func.__name__ != "close":
            raise IllegalStateError("Query object already consumed")

        result = func(*args, **kw)
        if not is_consumed and func.__name__ in TERMINAL_FUNCTIONS:
            query.close()
        return result

    return wrapper
