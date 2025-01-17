from functools import wraps

from fumus.utils import Optional, Result

# Naive implementations -> one could do better than this


def returns_optional(func):
    @wraps(func)
    def wrapper(*args, **kw):
        return Optional.of_nullable(func(*args, *kw))

    return wrapper


def returns_result(func):
    @wraps(func)
    def wrapper(*args, **kw):
        # TODO do we need BaseException
        try:
            result = func(*args, *kw)
        except (Exception, BaseException) as err:
            return Result.failure(err)
        return Result.success(result)

    return wrapper
