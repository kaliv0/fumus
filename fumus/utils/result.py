from fumus.utils import Optional


class Result:
    __slots__ = (
        "value",
        "error",
    )

    def __init__(self, value=None, error=None):
        if value is None and error is None:
            raise ValueError("Result's Value and Error cannot both be None")
        self.value = value
        self.error = error

    @property
    def is_successful(self):
        return self.error is None

    @classmethod
    def success(cls, value):
        return cls(value)

    @classmethod
    def failure(cls, error):
        return cls(error=error)

    def map_success(self, func):
        if self.is_successful:
            return Optional.of_nullable(self.value).map(func)
        return Optional.empty()

    def map_failure(self, func):
        if not self.is_successful:
            return Optional.of(self.error).map(func)
        return Optional.empty()

    def map(self, on_success, on_failure):
        if self.is_successful:
            return on_success(self.value)
        return on_failure(self.error)

    def if_success(self, consumer):
        if self.is_successful:
            consumer(self.value)

    def if_failure(self, consumer):
        if not self.is_successful:
            consumer(self.error)

    def handle(self, on_success, on_failure):
        if self.is_successful:
            on_success(self.value)
        else:
            on_failure(self.error)

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
