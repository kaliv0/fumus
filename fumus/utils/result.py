from fumus import Optional


class Result:
    def __init__(self, value, error, is_successful):
        # TODO: use slots?, or dataclass
        self._value = value
        self._error = error
        self._is_successful = is_successful

    def __str__(self):
        return (
            f"Result[value={self._value}, error={self._error}, is_successful={self._is_successful}]"
        )

    @classmethod
    def success(cls, value):
        return cls(value, None, True)

    @classmethod
    def failure(cls, error):
        return cls(None, error, False)

    def map_success(self, func):
        if self._is_successful:
            return Optional.of_nullable(self._value).map(func)
        return Optional.empty()

    def map_failure(self, func):
        if not self._is_successful:
            return Optional.of_nullable(self._error).map(func)
        return Optional.empty()

    def map(self, success_func, failure_func):
        if self._is_successful:
            return success_func(self._value)
        return failure_func(self._error)

    # TODO: rename consumer to action/func?
    def if_success(self, consumer):
        if self._is_successful:
            consumer(self._value)

    def if_failure(self, consumer):
        if not self._is_successful:
            consumer(self._error)

    def handle(self, success_func, failure_func):
        if self._is_successful:
            success_func(self._value)
        failure_func(self._error)

    def or_else(self, other):
        return self._value if self._is_successful else other

    def or_else_get(self, supplier):
        return self._value if self._is_successful else supplier()

    def or_else_raise(self, supplier=None):
        if self._is_successful:
            return self._value
        if supplier:
            supplier(self._error)
        raise self._error
