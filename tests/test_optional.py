import io
from contextlib import redirect_stdout

import pytest

from fumus import Optional, Result
from fumus.decorators import returns_optional, returns_result
from fumus.exceptions import NoSuchElementError, NoneTypeError


def test_optional_get_raises():
    with pytest.raises(NoSuchElementError) as e:
        Optional.empty().get()
    assert str(e.value) == "Optional is empty"


def test_optional_of_none_raises():
    with pytest.raises(NoneTypeError) as e:
        Optional.of(None)
    assert str(e.value) == "Value cannot be None"


def test_print_optional():
    assert str(Optional.of(2)) == "Optional[2]"
    assert str(Optional.of_nullable(None)) == "Optional.empty"


def test_is_empty():
    assert Optional.of(3).is_empty() is False
    assert Optional.of_nullable(None).is_empty()


def test_get():
    assert Optional.of(3).get() == 3


def test_is_present():
    assert Optional.of(3).is_present()


def test_if_present():
    f = io.StringIO()
    with redirect_stdout(f):
        Optional.of(3).if_present(action=lambda x: print(f"{x}", end=""))
    assert f.getvalue() == "3"


def test_if_present_or_else():
    f = io.StringIO()
    with redirect_stdout(f):
        Optional.of(3).if_present_or_else(
            action=lambda x: print(f"{x}", end=""), empty_action=lambda: print("BANG!", end="")
        )
    assert f.getvalue() == "3"


def test_if_present_or_else_empty_action():
    f = io.StringIO()
    with redirect_stdout(f):
        Optional.empty().if_present_or_else(
            action=lambda x: print(f"{x}", end=""), empty_action=lambda: print("BANG!", end="")
        )
    assert f.getvalue() == "BANG!"


def test_or_else():
    assert Optional.of(3).or_else(4) == 3
    assert Optional.empty().or_else(4) == 4


def test_or_else_get(Foo):
    foo = Foo(name="Foo", num=43)
    assert Optional.empty().or_else_get(supplier=lambda: foo) is foo


def test_or_else_raise(Foo):
    with pytest.raises(NoSuchElementError) as e:
        Optional.empty().or_else_raise()
    assert str(e.value) == "Optional is empty"


def test_or_else_raise_custom_supplier(Foo):
    err_msg = "Yo Mr. White...!"

    class DamnItError(Exception):
        pass

    def damn_it_supplier():
        raise DamnItError(err_msg)

    with pytest.raises(DamnItError) as e:
        Optional.empty().or_else_raise(damn_it_supplier)
    assert str(e.value) == err_msg


def test_equality():
    assert Optional.of(1) == Optional.of(1)
    assert Optional.of(1) != Optional.of(2)
    assert Optional.of(1) != Optional.empty()
    assert Optional.empty() == Optional.empty()


####### decorators ####
# TODO: extract tests
def test_returns_optional_decorator():
    @returns_optional
    def fizz(x, y):
        return None if x == y else x + y

    num1 = 1
    num2 = 2
    result = fizz(num1, num2)
    assert isinstance(result, Optional)
    assert result.is_present()
    assert result.get() == 3

    num1 = num2 = 0
    result = fizz(num1, num2)
    assert result.is_empty()


def test_returns_result():
    @returns_result
    def buzz(x, y):
        if x == y:
            raise ValueError("x == y")
        return x + y

    # success
    num1 = 1
    num2 = 2
    result = buzz(num1, num2)
    assert isinstance(result, Result)
    assert result._is_successful  # TODO: make public
    assert result._value == 3  # TODO: same

    # failure
    num1 = num2 = 0
    result = buzz(num1, num2)
    assert not result._is_successful
    assert isinstance(result._error, ValueError)
    assert str(result._error) == "x == y"

    # error chaining
    @returns_result
    def burr(x, y, z):
        def bar(x, y, z):
            if x == y == z:
                raise ValueError("all vars equal")
            return (x + y) * z

        try:
            return bar(x, y, z)
        except ValueError as e:
            raise ArithmeticError("all gone sideways") from e

    num1 = num2 = num3 = 0
    result = burr(num1, num2, num3)
    # assert isinstance(result, Result)
    assert not result._is_successful
    assert isinstance(result._error, ArithmeticError)
    assert str(result._error) == "all gone sideways"
    assert isinstance(result._error.__cause__, ValueError)
    assert str(result._error.__cause__) == "all vars equal"

    # TODO: add __context__ and __cause__ in Result??
