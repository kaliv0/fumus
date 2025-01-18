from functools import wraps

from fumus.utils import Optional, Result

# Naive implementations -> one could do better than this


def returns_optional(func):
    @wraps(func)
    def wrapper(*args, **kw):
        return Optional.of_nullable(func(*args, *kw))

    return wrapper


def returns_result(*err_list):
    def handle_errors(func):
        exceptions = tuple(set(err_list).union((Exception,)))

        @wraps(func)
        def invoke_func(*args, **kw):
            try:
                result = func(*args, *kw)
            except exceptions as err:
                return Result.failure(err)
            return Result.success(result)

        return invoke_func

    return handle_errors
