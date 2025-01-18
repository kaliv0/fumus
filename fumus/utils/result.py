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
        """Returns bool whether the Result is successful and an error is not present"""
        return self.error is None

    @classmethod
    def success(cls, value):
        """Creates Result describing given value"""
        return cls(value)

    @classmethod
    def failure(cls, error):
        """Creates Result describing given error"""
        return cls(error=error)

    def map_success(self, mapper):
        """
        If a value is present, apply the provided mapping function to it,
        and if the result is non-null, return an Optional describing the result.
        Otherwise return an empty Optional.
        (NB: if the provided mapper returns an Optional,
        the result isn't wrapped-up in an additional one)
        """
        if self.is_successful:
            return self._map_result(mapper, self.value)
        return Optional.empty()

    def map_failure(self, mapper):
        """
        If an error is present, apply the provided mapping function to it,
        and if the result is non-null, return an Optional describing the result.
        Otherwise return an empty Optional
        """
        if not self.is_successful:
            return self._map_result(mapper, self.error)
        return Optional.empty()

    def map(self, on_success, on_failure):
        """Combines map_success() and map_failure()"""
        if self.is_successful:
            return self._map_result(on_success, self.value)
        return self._map_result(on_failure, self.error)

    def if_success(self, consumer):
        """Performs given action with the value if the Result is successful"""
        if self.is_successful:
            consumer(self.value)

    def if_failure(self, consumer):
        """Performs given action with the error if the Result is not successful"""
        if not self.is_successful:
            consumer(self.error)

    def handle(self, on_success, on_failure):
        """Combines if_success() and if_failure()"""
        if self.is_successful:
            on_success(self.value)
        else:
            on_failure(self.error)

    def or_else(self, other):
        """
        Returns the value if successful, or a provided argument otherwise
        """
        return self.value if self.is_successful else other

    def or_else_get(self, supplier):
        """
        Returns the value if present, or calls a 'supplier' function otherwise
        """
        return self.value if self.is_successful else supplier()

    def or_else_raise(self, supplier=None):
        """
        Returns the value if successful,
        otherwise throws an exception produced by the exception supplying function
        (if such is provided by the user) or re-raises original Exception
        """
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

    # ### helpers ###
    @staticmethod
    def _map_result(mapper, arg):
        result = mapper(arg)
        if isinstance(result, Optional):
            return result
        return Optional.of_nullable(result)
