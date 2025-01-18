import io
from contextlib import redirect_stdout

import pytest

from fumus.decorators import returns_result
from fumus.utils import Result, Optional


def test_is_successful():
    assert Result(42).is_successful
    assert not Result(None, ValueError("Oops")).is_successful


def test_success():
    res = Result.success(42)
    assert res.is_successful
    assert res.value == 42
    assert res.error is None


def test_failure():
    res = Result.failure(ValueError("Oops"))
    assert not res.is_successful
    assert res.value is None
    assert isinstance(res.error, ValueError)
    assert str(res.error) == "Oops"


def test_map_success():
    res = Result.success(42)
    assert res.map_success(lambda x: x + 3).get() == 45
    assert res.map_success(lambda x: Optional.of(x + 3)).get() == 45
    assert res.map_success(lambda x: None).is_empty
    # mapper isn't called
    assert Result.failure(ValueError("Oops")).map_success(lambda x: str(x)).is_empty


def test_map_failure():
    res = Result.failure(ValueError("Oops"))
    assert res.map_failure(lambda err: str(err)).get() == "Oops"
    assert res.map_failure(lambda err: Optional.of(str(err))).get() == "Oops"

    sad_msg = "We regret to inform you..."
    assert res.map_failure(lambda _: sad_msg).get() == sad_msg
    # mapper isn't called
    assert Result.success(42).map_failure(lambda: sad_msg).is_empty


def test_map():
    res = Result.success(42)
    assert (
        res.map(on_success=lambda x: x + 3, on_failure=lambda err: print(err, end="")).get() == 45
    )

    fail = Result.failure(ValueError("Oops"))
    f = io.StringIO()
    with redirect_stdout(f):
        fail.map(on_success=lambda x: x + 3, on_failure=lambda err: print(err, end=""))
    assert f.getvalue() == "Oops"


def test_if_success():
    res = Result.success(42)
    f = io.StringIO()
    with redirect_stdout(f):
        res.if_success(lambda x: print(x + 3, end=""))
    assert f.getvalue() == "45"


def test_if_failure():
    res = Result.failure(ValueError("Oops"))
    f = io.StringIO()
    with redirect_stdout(f):
        res.if_failure(lambda err: print(err, end=""))
    assert f.getvalue() == "Oops"


def test_handle():
    res = Result.success(42)
    f = io.StringIO()
    with redirect_stdout(f):
        res.handle(
            on_success=lambda x: print(f"value={x}", end=""),
            on_failure=lambda err: print(err, end=""),
        )
    assert f.getvalue() == "value=42"


def test_handle_failure():
    fail = Result.failure(ValueError("Oops"))
    f = io.StringIO()
    with redirect_stdout(f):
        fail.handle(
            on_success=lambda x: print(f"{x}", end=""), on_failure=lambda err: print(err, end="")
        )
    assert f.getvalue() == "Oops"


def test_or_else():
    assert Result.success(3).or_else(4) == 3
    assert Result.failure(ValueError("Oops")).or_else(4) == 4


def test_or_else_get():
    assert Result.success(3).or_else_get(lambda: 4) == 3
    assert Result.failure(ValueError("Oops")).or_else_get(supplier=lambda: 4) == 4


def test_or_else_raise():
    with pytest.raises(ValueError) as e:
        Result.failure(ValueError("Oops")).or_else_raise()
    assert str(e.value) == "Oops"


def test_or_else_raise_custom_supplier():
    class DamnItError(Exception):
        pass

    def damn_it_supplier(error):
        raise DamnItError("Boo") from error

    with pytest.raises(DamnItError) as e:
        Result.failure(ValueError("Oops")).or_else_raise(damn_it_supplier)
    assert isinstance(e.value, DamnItError)
    assert str(e.value) == "Boo"
    assert isinstance(e.value.__cause__, ValueError)
    assert str(e.value.__cause__) == "Oops"


# ### decorator ###
def test_returns_result():
    @returns_result()
    def buzz(x, y):
        if x == y:
            raise ValueError("x == y")
        return x + y

    # success
    num1 = 1
    num2 = 2
    result = buzz(num1, num2)
    assert isinstance(result, Result)
    assert result.is_successful
    assert result.value == 3

    # failure
    num1 = num2 = 0
    result = buzz(num1, num2)
    assert not result.is_successful
    assert isinstance(result.error, ValueError)
    assert str(result.error) == "x == y"


def test_returns_result_error_chaining():
    def bar(a, b, c):
        if a == b == c:
            raise ValueError("all vars equal")
        return (a + b) * c

    @returns_result()
    def burr(x, y, z):
        try:
            return bar(x, y, z)
        except ValueError as e:
            raise ArithmeticError("all gone sideways") from e

    num1 = num2 = num3 = 0
    result = burr(num1, num2, num3)
    assert not result.is_successful
    assert isinstance(result.error, ArithmeticError)
    assert str(result.error) == "all gone sideways"
    assert isinstance(result.error.__cause__, ValueError)
    assert str(result.error.__cause__) == "all vars equal"


def test_returns_result_user_exception():
    @returns_result(TypeError, ZeroDivisionError)
    def buzz(x, y):
        return x / y

    # success
    num1 = 6
    num2 = 3
    result = buzz(num1, num2)
    assert isinstance(result, Result)
    assert result.is_successful
    assert result.value == 2

    # failure
    num1 = 2
    num2 = "x"
    result = buzz(num1, num2)
    assert not result.is_successful
    assert isinstance(result.error, TypeError)
    assert str(result.error) == "unsupported operand type(s) for /: 'int' and 'str'"

    num1 = num2 = 0
    result = buzz(num1, num2)
    assert not result.is_successful
    assert isinstance(result.error, ZeroDivisionError)
    assert str(result.error) == "division by zero"
