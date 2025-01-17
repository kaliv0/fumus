from fumus.utils import Optional


class Result:
    __slots__ = (
        "value",
        "error",
    )

    def __init__(self, value, error):
        self.value = value
        self.error = error

    @property
    def is_successful(self):
        return self.error is None

    @classmethod
    def success(cls, value):
        return cls(value, None)

    @classmethod
    def failure(cls, error):
        return cls(None, error)

    def map_success(self, func):
        if self.is_successful:
            return Optional.of_nullable(self.value).map(func)
        return Optional.empty()

    def map_failure(self, func):
        if not self.is_successful:
            return Optional.of_nullable(self.error).map(func)
        return Optional.empty()

    def map(self, success_func, failure_func):
        if self.is_successful:
            return success_func(self.value)
        return failure_func(self.error)

    def if_success(self, consumer):
        if self.is_successful:
            consumer(self.value)

    def if_failure(self, consumer):
        if not self.is_successful:
            consumer(self.error)

    def handle(self, success_func, failure_func):
        if self.is_successful:
            success_func(self.value)
        failure_func(self.error)

    def or_else(self, other):
        return self.value if self.is_successful else other

    def or_else_get(self, supplier):
        return self.value if self.is_successful else supplier()

    def or_else_raise(self, supplier=None):
        if self.is_successful:
            return self.value
        if supplier:
            supplier(self.error)
        raise self.error

    def __str__(self):
        return f"Result[value={self.value}, error={self.error}]"

    def __eq__(self, other):
        if self.is_successful and other.is_successful:
            return self.value == other.value
        return False

    def __hash__(self):
        return hash(self.value) if self.is_successful else 0
