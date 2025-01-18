import io
import json
from contextlib import redirect_stdout
from operator import itemgetter

import pytest

from fumus import Query
from fumus.utils import Optional, DictItem
from fumus.exceptions.exception import IllegalStateError, UnsupportedTypeError, NoneTypeError


def test_query():
    assert Query([1, 2, 3])._iterable == [1, 2, 3]


def test_query_from_none():
    with pytest.raises(NoneTypeError) as e:
        Query(None)
    assert str(e.value) == "Cannot create Query from None"


def test_query_of():
    assert Query.of(1, 2, 3)._iterable == (1, 2, 3)


def test_query_of_nullable():
    assert Query.of_nullable(None).count() == 0

    nonempty_query = Query.of_nullable([1, 2, 3])
    assert nonempty_query.count() != 0
    assert nonempty_query._iterable == [1, 2, 3]


def test_empty_query():
    assert Query.empty().count() == 0


def test_iterate():
    assert Query.iterate(0, lambda x: x + 1).limit(5).to_list() == [0, 1, 2, 3, 4]


def test_iterate_skip():
    assert Query.iterate(0, lambda x: x + 1).skip(5).limit(5).to_list() == [5, 6, 7, 8, 9]


def test_iterate_with_predicate():
    assert Query.iterate(0, lambda x: x + 1, lambda x: x < 5).to_list() == [0, 1, 2, 3, 4]
    assert Query.iterate(0, lambda x: x + 1, lambda x: x < 0).to_list() == []


def test_generate():
    assert Query.generate(lambda: 42).limit(3).to_list() == [42, 42, 42]


def test_constant():
    assert Query.constant(8).limit(3).to_list() == [8, 8, 8]


def test_range():
    assert Query.from_range(0, 10).to_list() == [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    assert Query.from_range(0, 10, 3).to_list() == [0, 3, 6, 9]
    assert Query.from_range(10, -1, -2).to_list() == [10, 8, 6, 4, 2, 0]


def test_range_with_range_obj():
    range_obj = range(0, 10)
    assert Query.from_range(range_obj).to_list() == [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]


def test_iterable_from_string():
    json_str = '{"Name": "Jennifer Smith", "Phone": "555-123-4568", "Email": "jen123@gmail.com"}'
    json_map = json.loads(json_str)
    assert Query(json_map).filter(lambda x: len(x.key) < 6).map(lambda x: x.key).to_tuple() == (
        "Name",
        "Phone",
        "Email",
    )
    assert Query(json_map).map(lambda x: f"***{x.value}***").to_tuple() == (
        "***Jennifer Smith***",
        "***555-123-4568***",
        "***jen123@gmail.com***",
    )


def test_empty_json_from_string():
    empty_json = "{}"
    assert Query(json.loads(empty_json)).to_tuple() == ()


def test_filter():
    assert Query([1, 2, 3, 4, 5, 6]).filter(lambda x: x % 2 == 0).to_list() == [2, 4, 6]


def test_map():
    assert Query([1, 2, 3]).map(str).to_list() == ["1", "2", "3"]


def test_map_lambda():
    assert Query([1, 2, 3]).map(lambda x: x + 5).to_list() == [6, 7, 8]


def test_map_dict():
    assert Query({"x": 1, "y": 2}).map(lambda x: x.key + str(x.value)).to_list() == ["x1", "y2"]


def test_filter_map():
    assert Query([None, "foo", "", "bar"]).filter_map(str.upper).to_list() == ["FOO", "", "BAR"]


def test_filter_map_discard_falsy():
    assert Query.of(None, "foo", "", "bar", 0, []).filter_map(
        str.upper, discard_falsy=True
    ).to_list() == [
        "FOO",
        "BAR",
    ]


def test_reduce():
    assert Query([1, 2, 3]).reduce(lambda acc, val: acc + val, identity=3).get() == 9


def test_reduce_no_identity_provided():
    assert Query([1, 2, 3]).reduce(lambda acc, val: acc + val).get() == 6


def test_reduce_empty_collection():
    assert Query([]).reduce(lambda acc, val: acc + val).is_empty


def test_for_each():
    f = io.StringIO()
    with redirect_stdout(f):
        Query([1, 2, 3, 4]).for_each(lambda x: print(f"{'#' * x} ", end=""))
    assert f.getvalue() == "# ## ### #### "


def test_enumerate():
    iterable = ["x", "y", "z"]
    assert Query(iterable).enumerate().to_list() == [(0, "x"), (1, "y"), (2, "z")]
    assert Query(iterable).enumerate(start=1).to_list() == [(1, "x"), (2, "y"), (3, "z")]


def test_peek():
    f = io.StringIO()
    with redirect_stdout(f):
        result = (
            Query([1, 2, 3, 4])
            .filter(lambda x: x > 2)
            .peek(lambda x: print(f"{x} ", end=""))
            .map(lambda x: x * 20)
            .to_list()
        )
    assert f.getvalue() == "3 4 "
    assert result == [60, 80]


# ### skip ###
def test_skip():
    assert Query([1, 2, 3, 4, 5, 6, 7, 8, 9, 10]).skip(7).to_tuple() == (8, 9, 10)


def test_skip_empty():
    assert Query.empty().skip(3).to_tuple() == ()


def test_skip_bigger_than_query_count():
    assert Query([1, 2]).skip(5).to_tuple() == ()


def test_skip_negative_count():
    with pytest.raises(ValueError) as e:
        Query([1, 2]).skip(-5).to_tuple()
    assert str(e.value) == "Skip count cannot be negative"


# ### limit ###
def test_limit():
    assert Query([1, 2, 3, 4, 5, 6, 7, 8, 9, 10]).limit(3).to_tuple() == (1, 2, 3)


def test_limit_empty():
    assert Query.empty().limit(3).to_tuple() == ()


def test_limit_bigger_than_query_count():
    assert Query([1, 2]).limit(5).to_tuple() == (1, 2)


def test_limit_negative_count():
    with pytest.raises(ValueError) as e:
        Query([1, 2]).limit(-5).to_tuple()
    assert str(e.value) == "Limit count cannot be negative"


def test_head():
    assert (
        Query([1, 2, 3, 4, 5, 6, 7, 8, 9, 10]).limit(3).to_tuple()
        == Query([1, 2, 3, 4, 5, 6, 7, 8, 9, 10]).head(3).to_tuple()
    )


# ### tail ###
def test_tail():
    assert Query.of(1, 2, 3, 4).tail(2).to_list() == [3, 4]


def test_tail_empty():
    assert Query.empty().tail(3).to_tuple() == ()


def test_tail_bigger_than_query_count():
    assert Query([1, 2]).tail(5).to_tuple() == (1, 2)


def test_tail_negative_count():
    with pytest.raises(ValueError) as e:
        Query([1, 2]).tail(-5).to_tuple()
    assert str(e.value) == "Tail count cannot be negative"


# ### concat ###
def test_concat():
    assert Query.of(1, 2, 3).concat(Query.of(4, 5, 6)).to_list() == [1, 2, 3, 4, 5, 6]
    assert Query([1, 2, 3]).concat([4, 5]).to_list() == [1, 2, 3, 4, 5]


def test_concat_empty():
    assert Query.empty().concat(Query.of(1, 2, 3)).to_list() == [1, 2, 3]
    assert Query.concat(Query.empty(), Query.empty()).to_list() == []


def test_concat_linear_collections():
    assert Query((1, 2, 3)).concat([5, 6]).to_list() == [1, 2, 3, 5, 6]
    assert Query([1, 2, 3]).concat([(5, 6), [8]]).to_list() == [1, 2, 3, (5, 6), [8]]
    assert Query([1, 2, 3]).concat([(5, 6), [8]]).flatten().to_list() == [1, 2, 3, 5, 6, 8]
    # hacky but works as Query.of() is passed as self
    assert Query.concat(Query.of(1, 2, 3)).concat((5, 6), {7}).to_list() == [1, 2, 3, 5, 6, 7]


def test_concat_dicts_to_query():
    first_dict = {"x": 1, "y": 2}
    second_dict = {"p": 33, "q": 44, "r": 55}
    items_list = [
        DictItem(key="x", value=1),
        DictItem(key="y", value=2),
        DictItem(key="p", value=33),
        DictItem(key="q", value=44),
        DictItem(key="r", value=55),
    ]
    assert Query.empty().concat(first_dict, second_dict).to_list() == items_list
    assert Query(first_dict).concat(Query(second_dict)).to_list() == items_list
    assert Query(first_dict).concat(second_dict).to_list() == items_list

    assert Query.concat(Query.empty(), second_dict).to_list() == [
        DictItem(key="p", value=33),
        DictItem(key="q", value=44),
        DictItem(key="r", value=55),
    ]
    assert Query(first_dict).concat(Query(second_dict)).to_dict(lambda x: (x.key, x.value)) == {
        "x": 1,
        "y": 2,
        "p": 33,
        "q": 44,
        "r": 55,
    }
    assert Query(first_dict).concat(Query(second_dict)).to_dict(lambda x: x) == {
        "x": 1,
        "y": 2,
        "p": 33,
        "q": 44,
        "r": 55,
    }


def test_concat_raises_non_iterable():
    with pytest.raises(TypeError) as e:
        Query([1, 2, 3]).concat(5).to_list()
    assert str(e.value) == "'int' object is not iterable"


# ### prepend ###
def test_prepend_collection():
    assert Query([2, 3, 4]).prepend([1]).to_list() == [1, 2, 3, 4]
    assert Query([2, 3, 4]).prepend((0, 1)).to_list() == [0, 1, 2, 3, 4]
    assert Query([3, 4, 5]).prepend(([0, 1], 2)).to_list() == [[0, 1], 2, 3, 4, 5]
    assert Query([3, 4, 5]).prepend(Query.of([0, 1], 2)).to_list() == [[0, 1], 2, 3, 4, 5]


def test_prepend_dict():
    second_dict = {"x": 3, "y": 4}
    first_dict = {"a": 1, "b": 2}
    items_list = [
        DictItem(key="a", value=1),
        DictItem(key="b", value=2),
        DictItem(key="x", value=3),
        DictItem(key="y", value=4),
    ]
    # two queries of dicts
    assert Query(second_dict).prepend(Query(first_dict)).to_list() == items_list
    # dict to query of dict
    assert Query(second_dict).prepend(first_dict).to_list() == items_list

    assert Query(second_dict).prepend(first_dict).filter(lambda x: x.value % 2 == 0).map(
        lambda x: x.key
    ).to_list() == ["b", "y"]


# ### flat ###
def test_flat_map():
    assert Query([[1, 2], [3, 4], [5]]).flat_map(lambda x: Query(x)).to_list() == [1, 2, 3, 4, 5]


def test_flat_map_raises():
    with pytest.raises(TypeError) as e:
        assert Query([[1, 2], 3]).flat_map(lambda x: Query(x)).to_list()
    assert str(e.value) == "'int' object is not iterable"


def test_flatten():
    assert Query([[1, 2], [3, 4], [5]]).flatten().to_list() == [1, 2, 3, 4, 5]


def test_flatten_empty():
    assert Query([[], [1, 2]]).flatten().to_list() == [1, 2]


def test_flatten_no_nested_levels():
    assert Query([1, 2]).flatten().to_list() == [1, 2]


def test_flatten_multiple_levels():
    assert Query([[[1, 2], [3, 4]], [5, 6], [7]]).flatten().to_list() == [1, 2, 3, 4, 5, 6, 7]


def test_flatten_strings():
    assert Query([["abc"], "x", "y", "z"]).flatten().to_list() == ["abc", "x", "y", "z"]


# ### ###
def test_distinct():
    assert Query([1, 1, 2, 2, 2, 3]).distinct().to_list() == [1, 2, 3]


def test_count():
    assert Query([1, 2, 3, 4]).filter(lambda x: x % 2 == 0).count() == 2


def test_count_empty_collection():
    assert Query([]).count() == 0
    assert Query.empty().count() == 0


def test_sum():
    assert Query.of(1, 2, 3, 4).sum() == 10


def test_sum_empty_collection():
    assert Query([]).sum() == 0
    assert Query.empty().sum() == 0


def test_sum_non_number_elements():
    with pytest.raises(ValueError) as e:
        Query.of("a", "b").sum()
    assert str(e.value) == "Cannot apply sum on non-number elements"


def test_average():
    assert Query.of(1, 2, 3, 4, 5).average() == 3.0


def test_average_empty_collection():
    assert Query([]).average() == 0
    assert Query.empty().average() == 0


def test_average_non_number_elements():
    with pytest.raises(ValueError) as e:
        Query.of("a", "b").average()
    assert str(e.value) == "Cannot apply sum on non-number elements"


def test_take_while():
    assert Query.of("adam", "aman", "ahmad", "hamid", "muhammad", "aladdin").take_while(
        lambda x: x[0] == "a"
    ).to_list() == ["adam", "aman", "ahmad"]


def test_take_while_no_elements():
    assert (
        Query.of("adam", "aman", "ahmad", "hamid", "muhammad", "aladdin")
        .take_while(lambda x: x[0] == "xyz")
        .to_list()
        == []
    )


def test_drop_while():
    assert Query.of("adam", "aman", "ahmad", "hamid", "muhammad", "aladdin").drop_while(
        lambda x: x[0] == "a"
    ).to_list() == ["hamid", "muhammad", "aladdin"]


def test_drop_while_no_elements():
    assert Query.of("adam", "aman", "ahmad", "hamid", "muhammad", "aladdin").drop_while(
        lambda x: x[0] == "xyz"
    ).to_list() == ["adam", "aman", "ahmad", "hamid", "muhammad", "aladdin"]


def test_take_first():
    assert Query.of(1, 2, 3, 4, 5).take_first().get() == 1
    assert Query({"a": 1, "b": 2}).take_first().get() == DictItem(key="a", value=1)

    assert Query.empty().take_first().is_empty
    assert Query([]).take_first().is_empty

    assert Query([]).take_first(default=33).get() == 33


def test_take_last():
    assert Query.of(1, 2, 3, 4, 5).take_last().get() == 5
    assert Query({"a": 1, "b": 2}).take_last().get() == DictItem(key="b", value=2)

    assert Query.empty().take_last().is_empty
    assert Query([]).take_last().is_empty

    assert Query([]).take_last(default=33).get() == 33


# ### sort ###
def test_sort():
    assert Query.of(3, 5, 2, 1).map(lambda x: x * 10).sort().to_list() == [10, 20, 30, 50]


def test_sort_reverse():
    assert Query.of(3, 5, 2, 1).map(lambda x: x * 10).sort(reverse=True).to_list() == [
        50,
        30,
        20,
        10,
    ]


def test_sort_comparator_function():
    assert Query.of(3, 5, 2, 1).map(lambda x: (str(x), x * 10)).sort(itemgetter(1)).to_list() == [
        ("1", 10),
        ("2", 20),
        ("3", 30),
        ("5", 50),
    ]


def test_sort_multiple_keys():
    assert Query.of((3, 30), (2, 30), (2, 20), (1, 20), (1, 10)).sort(
        lambda x: (x[0], x[1])
    ).to_list() == [
        (1, 10),
        (1, 20),
        (2, 20),
        (2, 30),
        (3, 30),
    ]


def test_sort_comparator_and_reverse():
    assert Query.of(3, 5, 2, 1).map(lambda x: (str(x), x * 10)).sort(
        itemgetter(1), reverse=True
    ).to_list() == [
        ("5", 50),
        ("3", 30),
        ("2", 20),
        ("1", 10),
    ]


# ### reverse ###
def test_reverse():
    assert Query.of(3, 5, 2, 1).map(lambda x: x * 10).reverse().to_list() == [
        50,
        30,
        20,
        10,
    ]


def test_reverse_with_custom_comparator():
    assert Query.of(3, 5, 2, 1).map(lambda x: (str(x), x * 10)).reverse(
        itemgetter(1)
    ).to_list() == [
        ("5", 50),
        ("3", 30),
        ("2", 20),
        ("1", 10),
    ]


# ### ###
def test_complex_pipeline():
    assert Query.of(3, 5, 2, 1).map(lambda x: (str(x), x * 10)).sort(
        itemgetter(1), reverse=True
    ).to_dict(lambda x: (x[0], x[1])) == {"5": 50, "3": 30, "2": 20, "1": 10}


def test_reusing_query():
    query = Query.of(1, 2, 3)
    assert query._is_consumed is False

    result = query.map(str).to_list()
    assert result == ["1", "2", "3"]
    assert query._is_consumed

    with pytest.raises(IllegalStateError) as e:
        query.map(lambda x: x * 10).to_list()
    assert str(e.value) == "Query object already consumed"


def test_query_close():
    query = Query.of(1, 2, 3)
    assert query._is_consumed is False

    query.close()
    assert query._is_consumed


def test_query_on_close_callback():
    f = io.StringIO()
    with redirect_stdout(f):
        result = (
            Query([1, 2, 3, 4])
            .on_close(lambda: print("It was an honor", end=""))
            .peek(lambda x: print(f"{'#' * x} ", end=""))
            .map(lambda x: x * 2)
            .to_list()
        )
    assert result == [2, 4, 6, 8]
    assert f.getvalue() == "# ## ### #### It was an honor"


def test_query_on_close_callback_using_pointer_to_self():
    flag = False

    def flip():
        nonlocal flag
        flag = True

    result = Query([1, 2, 3, 4]).on_close(flip).map(lambda x: x * 2).to_list()
    assert result == [2, 4, 6, 8]
    assert flag is True


def test_compare_with():
    assert Query([1, 2]).compare_with(Query([1, 2]))
    assert Query([1, 2]).compare_with(Query([2, 1])) is False
    assert Query([1, 2]).compare_with(Query([3, 4])) is False


def test_compare_with_custom_key(Foo):
    fizz = Foo("fizz", 1)
    buzz = Foo("buzz", 2)
    comparator = lambda x, y: x.num == y.num  # noqa

    assert Query([fizz, buzz]).compare_with(Query([fizz, buzz]), comparator)
    assert Query([buzz, fizz]).compare_with(Query([fizz, buzz]), comparator) is False
    assert Query([fizz, buzz]).compare_with(Query([buzz]), comparator) is False


def test_quantify():
    assert Query([2, 3, 4, 5, 6]).quantify(predicate=lambda x: x % 2 == 0) == 3


def test_quantify_default_predicate():
    assert Query([None, 1, "", 3, 0]).quantify() == 2


# ### find ###
def test_find_first():
    assert Query.of(1, 2, 3, 4).filter(lambda x: x % 2 == 0).find_first().get() == 2


def test_find_first_with_predicate():
    assert Query.of(1, 2, 3, 4).find_first(lambda x: x % 2 == 0).get() == 2


def test_find_first_in_empty_query():
    result = Query.empty().find_first()
    assert isinstance(result, Optional)
    assert result.is_empty


def test_find_any():
    assert Query.of(1, 2, 3, 4).filter(lambda x: x % 2 == 0).find_any().get() in (2, 4)


def test_find_any_with_predicate():
    assert Query.of(1, 2, 3, 4).find_any(lambda x: x % 2 == 0).get() in (2, 4)


def test_find_any_in_empty_query():
    result = Query.empty().find_any()
    assert isinstance(result, Optional)
    assert result.is_empty


# ### match ###
def test_any_match():
    assert Query.of(1, 2, 3, 4).any_match(lambda x: x > 2)


def test_any_match_false():
    assert Query.of(1, 2, 3, 4).any_match(lambda x: x > 10) is False


def test_any_match_empty():
    assert Query.empty().any_match(lambda x: x > 10) is False


def test_all_match():
    assert Query.of(1, 2, 3, 4).all_match(lambda x: x > 0)


def test_all_match_false():
    assert Query.of(1, 2, 3, 4).all_match(lambda x: x > 10) is False


def test_all_match_empty():
    assert Query.empty().all_match(lambda x: x > 10)


def test_none_match():
    assert Query.of(1, 2, 3, 4).none_match(lambda x: x < 0)


def test_none_match_false():
    assert Query.of(1, 2, 3, 4).none_match(lambda x: x < 10) is False


def test_none_match_empty():
    assert Query.empty().none_match(lambda x: x > 10) is False


# ### min ###
def test_min():
    assert Query.of(2, 1, 3, 4).min().get() == 1


def test_min_comparator():
    assert Query.of("20", "101", "50").min(comparator=int).get() == "20"


def test_min_empty():
    result = Query.empty().min()
    assert isinstance(result, Optional)
    assert result.is_empty


def test_min_default_value():
    assert Query.empty().min(default="foo").get() == "foo"
    assert Query.empty().min(default="foo").get() == Query.empty().min().or_else("foo")


def test_min_objects(Foo):
    fizz = Foo("fizz", 1)
    buzz = Foo("buzz", 2)
    coll = [fizz, buzz]
    assert Query(coll).min(lambda x: x.num).get() is fizz


# ### max ###
def test_max():
    assert Query.of(2, 1, 3, 4).max().get() == 4


def test_max_comparator():
    assert Query.of("20", "101", "50").max(comparator=int).get() == "101"


def test_max_empty():
    result = Query.empty().max()
    assert isinstance(result, Optional)
    assert result.is_empty


def test_max_default_value():
    assert Query.empty().max(default="foo").get() == "foo"
    assert Query.empty().max(default="foo").get() == Query.empty().max().or_else("foo")


def test_max_objects(Foo):
    fizz = Foo("fizz", 1)
    buzz = Foo("buzz", 2)
    coll = [fizz, buzz]
    assert Query(coll).max(lambda x: x.num).get() is buzz


# ### collectors ###
def test_to_list():
    result = Query((1, 2, 3)).to_list()
    assert result == [1, 2, 3]
    assert type(result) is list


def test_to_tuple():
    result = Query([1, 2, 3]).to_tuple()
    assert result == (1, 2, 3)
    assert type(result) is tuple


def test_to_set():
    result = Query([1, 2, 2, 3, 3, 3]).to_set()
    assert result == {1, 2, 3}
    assert type(result) is set


def test_to_dict(Foo):
    coll = [Foo("fizz", 1), Foo("buzz", 2)]
    assert Query(coll).to_dict(lambda x: (x.name, x.num)) == {"fizz": 1, "buzz": 2}


def test_to_dict_via_dict_items(Foo):
    first_dict = {"x": 1, "y": 2}
    second_dict = {"p": 33, "q": 44, "r": None}
    assert Query(first_dict).concat(Query(second_dict)).to_dict(
        lambda x: DictItem(x.key, x.value or 0)
    ) == {
        "x": 1,
        "y": 2,
        "p": 33,
        "q": 44,
        "r": 0,
    }

    coll = [Foo("jazz", 11), Foo("mambo", 22)]
    assert Query(coll).to_dict(lambda x: DictItem(x.name, x.num)) == {"jazz": 11, "mambo": 22}


def test_to_dict_merger(Foo):
    coll = [Foo("fizz", 1), Foo("fizz", 2), Foo("buzz", 2)]
    assert Query(coll).to_dict(
        collector=lambda x: (x.name, x.num), merger=lambda old, new: old
    ) == {
        "fizz": 1,
        "buzz": 2,
    }


def test_to_dict_duplicate_key_no_merger_raises(Foo):
    coll = [Foo("fizz", 1), Foo("fizz", 2), Foo("buzz", 2)]
    with pytest.raises(IllegalStateError) as e:
        Query(coll).to_dict(
            collector=lambda x: (x.name, x.num),
        )
    assert str(e.value) == "Key 'fizz' already exists"


def test_to_dict_raises():
    with pytest.raises(UnsupportedTypeError, match="Cannot create dict items from 'int' type"):
        Query.of(("x", 1), ("b", 2)).to_dict(lambda x: x[1])


def test_collect():
    assert Query([1, 2, 3]).collect(tuple) == (1, 2, 3)
    assert Query.of(1, 2, 3).collect(list) == [1, 2, 3]
    assert Query.of(1, 1, 2, 2, 2, 3).collect(set) == {1, 2, 3}
    assert Query.of(1, 2, 3, 4).collect(dict, lambda x: (str(x), x * 10)) == {
        "1": 10,
        "2": 20,
        "3": 30,
        "4": 40,
    }
    assert Query([1, 2, 3, 4, 5]).collect(str) == "1, 2, 3, 4, 5"
    assert Query([1, 2, 3, 4, 5]).collect(str, str_delimiter=" | ") == "1 | 2 | 3 | 4 | 5"
    assert Query(["x", "y", "z"]).collect(str, str_delimiter="") == "xyz"


def test_to_dict_no_collector(Foo):
    first_dict = {"x": 1, "y": 2}
    second_dict = {"p": 33, "q": 44, "r": None}
    assert Query(first_dict).concat(Query(second_dict)).collect(dict) == {
        "x": 1,
        "y": 2,
        "p": 33,
        "q": 44,
        "r": None,
    }

    coll = [Foo("jazz", 11), Foo("mambo", 22)]
    assert Query(coll).to_dict(lambda x: DictItem(x.name, x.num)) == {"jazz": 11, "mambo": 22}


def test_collect_to_dict_raises(Foo):
    coll = [Foo("fizz", 1), Foo("fizz", 2), Foo("buzz", 2)]
    with pytest.raises(UnsupportedTypeError) as e:
        Query(coll).collect(dict)
    assert str(e.value) == "Cannot create dict items from 'Foo' type"

    with pytest.raises(UnsupportedTypeError) as e:
        Query(coll).collect(dict, lambda x: "invalid")
    assert str(e.value) == "Cannot create dict items from 'str' type"


def test_collect_invalid_type(Foo):
    coll = [Foo("fizz", 1), Foo("fizz", 2), Foo("buzz", 2)]
    with pytest.raises(ValueError) as e:
        Query(coll).collect(33)
    assert str(e.value) == "Invalid collection type"


def test_group_by():
    assert Query("AAAABBBCCD").group_by() == {
        "A": ["A", "A", "A", "A"],
        "B": ["B", "B", "B"],
        "C": ["C", "C"],
        "D": ["D"],
    }


def test_group_by_custom_collector():
    assert Query("AAAABBBCCD").group_by(collector=lambda k, g: (k, len(g))) == {
        "A": 4,
        "B": 3,
        "C": 2,
        "D": 1,
    }


def test_group_by_objects(Foo):
    coll = [
        Foo("fizz", 1),
        Foo("fizz", 2),
        Foo("fizz", 3),
        Foo("buzz", 2),
        Foo("buzz", 3),
        Foo("buzz", 4),
        Foo("buzz", 5),
    ]

    assert Query(coll).group_by(
        classifier=lambda obj: obj.name,
        collector=lambda k, g: (k, [(obj.name, obj.num) for obj in list(g)]),
    ) == {
        "fizz": [("fizz", 1), ("fizz", 2), ("fizz", 3)],
        "buzz": [("buzz", 2), ("buzz", 3), ("buzz", 4), ("buzz", 5)],
    }


def test_to_string(nested_json):
    assert Query([1, (2, 3), {4, 5, 6}]).to_string() == "1, (2, 3), {4, 5, 6}"
    assert (
        Query({"a": 1, "b": [2, 3]}).map(lambda x: {x.key: x.value}).to_string(delimiter=" | ")
        == "{'a': 1} | {'b': [2, 3]}"
    )
    assert Query(["x", "y", "z"]).to_string(delimiter="") == "xyz"
    assert Query(json.loads(nested_json)).collect(str) == Query(json.loads(nested_json)).to_string()


def test_repr(nested_json):
    assert str(Query.of(1, 2, 3)) == "Query.of(1, 2, 3)"
    assert str(Query([1, 2, 3])) == "Query.of(1, 2, 3)"
    assert (
        str(Query({"a": 1, "b": [2, 3], "c": {"x": "yz"}}))
        == "Query.of(DictItem(key='a', value=1), DictItem(key='b', value=[2, 3]), DictItem(key='c', value=(DictItem(key='x', value='yz'),)))"
    )

    assert str(Query(json.loads(nested_json))) == (
        "Query.of("
        "DictItem(key='user', value=(DictItem(key='Name', value='John'), DictItem(key='Phone', value='555-123-4568'), DictItem(key='Security Number', value='3450678'))), "
        "DictItem(key='super_user', value=(DictItem(key='Name', value='sudo'), DictItem(key='Email', value='admin@sudo.su'), DictItem(key='Some Other Number', value='000-0011'))), "
        "DictItem(key='fraud', value=(DictItem(key='Name', value='Freud'), DictItem(key='Email', value='ziggy@psycho.au'))))"
    )


# ### nested queries ###
def test_nested_json_from_string(nested_json):
    assert (
        Query(json.loads(nested_json))
        .filter(lambda outer: "user" in outer.key)
        .flat_map(
            lambda outer: (
                Query(outer.value)
                .filter(lambda inner: len(inner.key) < 6)
                .map(lambda inner: inner.value)
                .to_list()
            )
        )
        .to_tuple()
    ) == ("John", "555-123-4568", "sudo", "admin@sudo.su")


def test_nested_json_querying_nested_dict_items(nested_json):
    assert (
        Query(json.loads(nested_json))
        .flat_map(lambda x: x.value)
        .filter(lambda x: x.key == "Name" and "F" in x.value)
        .map(lambda x: x.value)
        .find_first()
        .get()
        == "Freud"
    )


# ### hacker-rank ###
def test_hackerrank():
    from curses.ascii import isalpha
    from enum import Enum

    # count vowels and constants in given string
    string = "123Ab5oc-E6db#bCi9<>"
    all_vowels = "AEIOUaeiou"

    class CharType(Enum):
        VOWELS = "vowels"
        CONSONANTS = "consonants"

    assert (
        Query(string)
        .filter(lambda ch: isalpha(ch))
        .partition(lambda ch: ch in all_vowels)
        .enumerate()
        .map(lambda x: (CharType.VOWELS if x[0] == 0 else CharType.CONSONANTS, len(tuple(x[1]))))
        .to_dict()
    ) == {CharType.CONSONANTS: 6, CharType.VOWELS: 4}


@pytest.mark.parametrize(
    "string, expected", [("a1b2c3c2b1a", True), ("abc321", False), ("x", True)]
)
def test_leetcode(string, expected):
    # check if given string is palindrome; string length is guaranteed to be > 0
    stop = len(string) // 2 if len(string) > 1 else 1
    assert Query.from_range(0, stop).none_match(lambda x: string[x] != string[x - 1]) is expected
