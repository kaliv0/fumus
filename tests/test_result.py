from fumus.decorators import returns_result
from fumus.utils import Result


# ### decorator ###
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

    @returns_result
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
