from fumus.exceptions import NoSuchElementError, NoneTypeError


class Optional:
    """Container object which may (or may not) contain a non-null value"""

    def __init__(self, element):
        self._element = element

    @classmethod
    def empty(cls):
        """Creates empty Optional"""
        return cls(None)

    @classmethod
    def of(cls, element):
        """Creates Optional describing given non-null value"""
        if element is None:
            raise NoneTypeError("Value cannot be None")
        return cls(element)

    @classmethod
    def of_nullable(cls, element):
        """
        Returns an Optional describing the given value, if non-null,
        otherwise returns an empty Optional
        """
        return cls(element)

    def get(self):
        """If a value is present, returns the value, otherwise raises an Exception"""
        if self.is_empty():
            raise NoSuchElementError("Optional is empty")
        return self._element

    def is_present(self):
        """Returns bool whether a value is present"""
        return not self.is_empty()

    def is_empty(self):
        """Returns bool whether the Optional is empty"""
        return self._element is None

    def if_present(self, action):
        """Performs given action with the value if the Optional is not empty"""
        if self.is_present():
            action(self.get())

    def if_present_or_else(self, action, empty_action):
        """Performs given action with the value if the Optional is not empty,
        otherwise calls fallback 'empty_action'
        """
        if self.is_present():
            action(self.get())
        else:
            empty_action()

    def or_else(self, value):
        """
        Returns the value if present, or a provided argument otherwise.
        Safe alternative to get() method
        """
        return self._element if self.is_present() else value

    def or_else_get(self, supplier):
        """
        Returns the value if present, or calls a 'supplier' function otherwise.
        Safe alternative to get() method
        """
        return self._element if self.is_present() else supplier()

    def or_else_raise(self, supplier=None):
        """
        Returns the value if present,
        otherwise throws an exception produced by the exception supplying function
        (if such is provided by the user) or NoSuchElementError
        """
        if self.is_present():
            return self._element
        if supplier:
            supplier()
        raise NoSuchElementError("Optional is empty")

    def map(self, mapper):
        if self.is_present():
            return Optional.of_nullable(mapper(self._element))
        return self

    def flat_map(self, mapper):
        if self.is_present():
            result = mapper(self._element)
            if isinstance(result, Optional):
                return result
            return Optional.of_nullable(mapper(self._element))
        return self

    def filter(self, predicate):
        if self.is_present:
            if predicate(self._element):
                return self
            return Optional.empty()
        return self

    def __repr__(self):
        if self.is_present():
            return f"Optional[{self._element}]"
        return "Optional.empty"

    def __eq__(self, other):
        if self.is_present() and other.is_present():
            return self.get() == other.get()
        return self.is_empty() and other.is_empty()

    def __hash__(self):
        return hash(self._element) if self.is_present() else 0
