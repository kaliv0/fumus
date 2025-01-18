import functools
import io
import operator
from contextlib import redirect_stdout

import pytest

from fumus.utils import Optional
from fumus.decorators import returns_optional
from fumus.exceptions.exception import NoSuchElementError, NoneTypeError


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
    assert Optional.of(3).is_empty is False
    assert Optional.of_nullable(None).is_empty


def test_get():
    assert Optional.of(3).get() == 3


def test_is_present():
    assert Optional.of(3).is_present


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


def test_map():
    assert Optional.of([6, 8, 10]).map(lambda x: functools.reduce(operator.mul, x)).get() == 480
    assert Optional.of([6, 8, 10]).map(lambda x: Optional.of(max(x))).get() == 10
    assert Optional.of(42).map(lambda x: None).is_empty
    # map never gest called
    assert Optional.empty().map(lambda x: functools.reduce(operator.mul, x)).is_empty


def test_filter():
    assert Optional.of([1, 2, 3]).filter(lambda x: max(x) % 2 != 0).get() == [1, 2, 3]
    assert Optional.of([1, 2, 3, 4, 5, 6]).filter(lambda x: max(x) % 5 == 0).is_empty
    # filter never gets called
    assert Optional.empty().filter(lambda x: max(x) % 5 == 0).is_empty


def test_equality():
    assert Optional.of(1) == Optional.of(1)
    assert Optional.of(1) != Optional.of(2)
    assert Optional.of(1) != Optional.empty()
    assert Optional.empty() == Optional.empty()


# ### decorator ###
def test_returns_optional_decorator():
    @returns_optional
    def fizz(x, y):
        return None if x == y else x + y

    num1 = 1
    num2 = 2
    result = fizz(num1, num2)
    assert isinstance(result, Optional)
    assert result.is_present
    assert result.get() == 3

    num1 = num2 = 0
    result = fizz(num1, num2)
    assert result.is_empty
