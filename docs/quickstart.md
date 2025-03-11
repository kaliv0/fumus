## How to use
### Creating queries
- query from iterable
```python
Query([1, 2, 3])
```

- from variadic arguments
```python
Query.of(1, 2, 3)
```

- empty query
```python
Query.empty()
```

- infinite ordered query
```python
Query.iterate(0, lambda x: x + 1)
```

NB: in similar fashion you can create <i>finite ordered query</i> by providing a <i>condition</i> predicate</i>
```python
Query.iterate(10, operation=lambda x: x + 1, condition=lambda x: x < 15).to_list()
# [10, 11, 12, 13, 14]
```

- infinite unordered query
```python
import random

Query.generate(lambda: random.random())
```

- infinite query with given value
```python
Query.constant(42)
```

- query from range
<br>(from <i>start</i> (inclusive) to <i>stop</i> (exclusive) by an incremental <i>step</i> (defaults to 1))
```python
Query.from_range(0, 10).to_list()
Query.from_range(0, 10, 3).to_list()
Query.from_range(10, -1, -2).to_list()
```
(or from <i>range</i> object)
```python
range_obj = range(0, 10)
Query.from_range(range_obj).to_list()
```

- concat
<br>(concatenate new queries/iterables with the current one)
```python
Query.of(1, 2, 3).concat(Query.of(4, 5)).to_list()
Query([1, 2, 3]).concat([5, 6]).to_list()
```

- prepend
<br>(prepend new query/iterable to the current one)
```python
Query([2, 3, 4]).prepend(0, 1).to_list()
Query.of(3, 4, 5).prepend(Query.of([0, 1], 2)).to_list()
```

NB: creating new query from None raises error.
<br>In cases when the <i>iterable</i> could potentially be None use the <i>of_nullable()</i> method instead;
<br>it returns an <i>empty query</i> if None and a <i>regular</i> one otherwise

--------------------------------------------
### Intermediate operations
- filter
```python
Query([1, 2, 3]).filter(lambda x: x % 2 == 0)
```

- map
```python
Query([1, 2, 3]).map(str).to_list()
Query([1, 2, 3]).map(lambda x: x + 5).to_list()
```

- filter_map
<br>(filter out all None or discard_falsy values (if discard_falsy=True) and applies mapper function to the elements of the query)
```python
Query.of(None, "foo", "", "bar", 0, []).filter_map(str.upper, discard_falsy=True).to_list()
# ["FOO", "BAR"]
```

- flat_map
<br>(map each element of the query and yields the elements of the produced iterators)
```python
Query([[1, 2], [3, 4], [5]]).flat_map(lambda x: Query(x)).to_list()
# [1, 2, 3, 4, 5]
```

- flatten
```python
Query([[1, 2], [3, 4], [5]]).flatten().to_list()
# [1, 2, 3, 4, 5]
```

- reduce 
<br>(returns Optional)
```python
Query([1, 2, 3]).reduce(lambda acc, val: acc + val, identity=3).get()
```

- peek
<br>(perform the provided operation on each element of the query without consuming it)
```python
(Query([1, 2, 3, 4])
    .filter(lambda x: x > 2)
    .peek(lambda x: print(f"{x} ", end=""))
    .map(lambda x: x * 20)
    .to_list())
```

- enumerate
<br>(returns each element of the Query preceded by his corresponding index 
(by default starting from 0 if not specified otherwise))
```python
iterable = ["x", "y", "z"]
Query(iterable).enumerate().to_list()
Query(iterable).enumerate(start=1).to_list()
# [(0, "x"), (1, "y"), (2, "z")]
# [(1, "x"), (2, "y"), (3, "z")]
```

- view
<br>(provides access to a selected part of the query)
```python
Query([1, 2, 3, 4, 5, 6, 7, 8, 9]).view(start=1, stop=-3, step=2).to_list()
# [2, 4, 6]
```

- distinct
<br>(returns a query with the distinct elements of the current one)
```python
Query([1, 1, 2, 2, 2, 3]).distinct().to_list()
```

- skip
<br>(discards the first n elements of the query and returns a new query with the remaining ones)
```python
Query.iterate(0, lambda x: x + 1).skip(5).limit(5).to_list()
```

- limit / head
<br>(returns a query with the first n elements, or fewer if the underlying iterator ends sooner)
```python
Query([1, 2, 3, 4, 5, 6, 7, 8, 9, 10]).limit(3).to_tuple()
Query([1, 2, 3, 4, 5, 6, 7, 8, 9, 10]).head(3).to_tuple()
```

- tail
<br>(returns a query with the last n elements, or fewer if the underlying iterator ends sooner)
```python
Query([1, 2, 3, 4, 5, 6, 7, 8, 9, 10]).tail(3).to_tuple()
```

- take_while
<br>(returns a query that yields elements based on a predicate)
```python
Query.of(1, 2, 3, 4, 5, 6, 7, 2, 3).take_while(lambda x: x < 5).to_list()
# [1, 2, 3, 4]
```

- drop_while
<br>(returns a query that skips elements based on a predicate and yields the remaining ones)
```python
Query.of(1, 2, 3, 5, 6, 7, 2).drop_while(lambda x: x < 5).to_list()
# [5, 6, 7, 2]
```

- sort
<br>(sorts the elements of the current query according to natural order or based on the given comparator;
<br>if 'reverse' flag is True, the elements are sorted in descending order)
```python
(Query.of((3, 30), (2, 30), (2, 20), (1, 20), (1, 10))
    .sort(lambda x: (x[0], x[1]), reverse=True)
    .to_list())
# [(3, 30), (2, 30), (2, 20), (1, 20), (1, 10)]
```

- reverse
<br>(sorts the elements of the current query in reverse order;
<br>alias for <i>'sort(collector, reverse=True)'</i>)
```python
(Query.of((3, 30), (2, 30), (2, 20), (1, 20), (1, 10))
    .reverse(lambda x: (x[0], x[1]))
    .to_list())
# [(3, 30), (2, 30), (2, 20), (1, 20), (1, 10)]
```

<br>NB: in case of query of dicts all key-value pairs are represented internally as <i>DictItem</i> objects 
<br>(including recursively for nested Mapping structures)
<br>to provide more convenient intermediate operations syntax e.g.
```python
first_dict = {"a": 1, "b": 2}
second_dict = {"x": 3, "y": 4}
(Query(first_dict).concat(second_dict)
    .filter(lambda x: x.value % 2 == 0)
    .map(lambda x: x.key)
    .to_list()) 
```

- on_close
<br>(returns an equivalent Query with an additional <i>close handler</i> to be invoked automatically by the <i>terminal operation</i>)
```python
(Query([1, 2, 3, 4])
    .on_close(lambda: print("Sorry Montessori"))
    .peek(lambda x: print(f"{'$' * x} ", end=""))
    .map(lambda x: x * 2)
    .to_list())
# "$ $$ $$$ $$$$ Sorry Montessori"
# [2, 4, 6, 8]
```
--------------------------------------------
### Terminal operations
#### Collectors
- collecting result into list, tuple, set
```python
Query([1, 2, 3]).to_list()
Query([1, 2, 3]).to_tuple()
Query([1, 2, 3]).to_set()
```

- into dict
```python
class Foo:
    def __init__(self, name, num):
        self.name = name
        self.num = num
        
Query([Foo("fizz", 1), Foo("buzz", 2)]).to_dict(lambda x: (x.name, x.num))
# {"fizz": 1, "buzz": 2}
```

In the case of a collision (duplicate keys) the 'merger' functions indicates which entry should be kept
```python
collection = [Foo("fizz", 1), Foo("fizz", 2), Foo("buzz", 2)]
Query(collection).to_dict(collector=lambda x: (x.name, x.num), merger=lambda old, new: old)
# {"fizz": 1, "buzz": 2}
```

<i>to_dict</i> method also supports creating dictionaries from dict DictItem objects
```python
first_dict = {"x": 1, "y": 2}
second_dict = {"p": 33, "q": 44, "r": None}
Query(first_dict).concat(Query(second_dict)).to_dict(lambda x: DictItem(x.key, x.value or 0)) 
# {"x": 1, "y": 2, "p": 33, "q": 44, "r": 0}
```
e.g. you could combine queries of dicts by writing:
```python
Query(first_dict).concat(Query(second_dict)).to_dict() 
```
(simplified from <i>'.to_dict(lambda x: x)'</i>)

- into string
```python
Query({"a": 1, "b": [2, 3]}).to_string()
# "Query(DictItem(key=a, value=1), DictItem(key=b, value=[2, 3]))"
```
```python
Query({"a": 1, "b": [2, 3]}).map(lambda x: {x.key: x.value}).to_string(delimiter=" | ")
# "Query({'a': 1} | {'b': [2, 3]})"
```

- alternative for working with collectors is using the <i>collect</i> method
```python
Query([1, 2, 3]).collect(tuple)
Query.of(1, 2, 3).collect(list)
Query.of(1, 1, 2, 2, 2, 3).collect(set)
Query.of(1, 2, 3, 4).collect(dict, lambda x: (str(x), x * 10))
Query.of("x", "y", "z").collect(str, str_delimiter="->")
```

- grouping
```python
Query("AAAABBBCCD").group_by(collector=lambda key, grouper: (key, len(grouper)))
# {"A": 4, "B": 3, "C": 2, "D": 1}
```

```python
coll = [Foo("fizz", 1), Foo("fizz", 2), Foo("fizz", 3), Foo("buzz", 2), Foo("buzz", 3), Foo("buzz", 4), Foo("buzz", 5)]
Query(coll).group_by(
    classifier=lambda obj: obj.name,
    collector=lambda key, grouper: (key, [(obj.name, obj.num) for obj in list(grouper)]))
# {"fizz": [("fizz", 1), ("fizz", 2), ("fizz", 3)],
#  "buzz": [("buzz", 2), ("buzz", 3), ("buzz", 4), ("buzz", 5)]}
```
#### Other terminal operations
- for_each
```python
Query([1, 2, 3, 4]).for_each(lambda x: print(f"{'#' * x} ", end=""))
```

- count
<br>(returns the count of elements in the query)
```python
Query([1, 2, 3, 4]).filter(lambda x: x % 2 == 0).count()
```

- sum
```python
Query.of(1, 2, 3, 4).sum() 
```

- min
<br>(returns Optional with the minimum element of the query)
```python
Query.of(2, 1, 3, 4).min().get()
```

- max
<br>(returns Optional with the maximum element of the query)
```python
Query.of(2, 1, 3, 4).max().get()
```

- average
<br>(returns the average value of elements in the query)
```python
Query.of(1, 2, 3, 4, 5).average()
```

- find_first
<br>(search for an element of the query that satisfies a predicate,
returns an Optional with the first found value, if any, or None)
```python
Query.of(1, 2, 3, 4).filter(lambda x: x % 2 == 0).find_first().get()
```

- find_any
<br>(search for an element of the query that satisfies a predicate,
returns an Optional with some of the found values, if any, or None)
```python
Query.of(1, 2, 3, 4).filter(lambda x: x % 2 == 0).find_any().get()
```

- any_match
<br>(returns whether any elements of the query match the given predicate)
```python
Query.of(1, 2, 3, 4).any_match(lambda x: x > 2)
```

- all_match
<br>(returns whether all elements of the query match the given predicate)
```python
Query.of(1, 2, 3, 4).all_match(lambda x: x > 2)
```

- none_match
<br>(returns whether no elements of the query match the given predicate)
```python
Query.of(1, 2, 3, 4).none_match(lambda x: x < 0)
```

- take_first
<br>(returns Optional with the first element of the query or a default value)
```python
Query({"a": 1, "b": 2}).take_first().get()
Query([]).take_first(default=33).get() 
# DictItem(key="a", value=1)
# 33
```

- take_last
<br>(returns Optional with the last element of the query or a default value)
```python
Query({"a": 1, "b": 2}).take_last().get()
Query([]).take_last(default=33).get() 
```

- compare_with
<br>(compares linearly the contents of two queries based on a given comparator)
```python
fizz = Foo("fizz", 1)
buzz = Foo("buzz", 2)
Query([buzz, fizz]).compare_with(Query([fizz, buzz]), lambda x, y: x.num == y.num)
```

- quantify
<br>(count how many of the elements are Truthy or evaluate to True based on a given predicate)
```python
Query([2, 3, 4, 5, 6]).quantify(predicate=lambda x: x % 2 == 0)
```

NB: although the Query is closed automatically by the <i>terminal operation</i>
<br> you can still close it by hand (if needed) invoking the <i>close()</i> method.
<br> In turn that will trigger the <i>close_handler</i> (if such was provided)

--------------------------------------------
### Itertools integration
Invoke <i>use</i> method by passing the itertools function and it's arguments as **kwargs
```python
import itertools
import operator

Query([1, 2, 3, 4, 5, 6, 7, 8, 9, 10]).use(itertools.islice, start=3, stop=8)
Query.of(1, 2, 3, 4, 5).use(itertools.accumulate, func=operator.mul).to_list()
Query(range(3)).use(itertools.permutations, r=3).to_list()

```
#### Itertools 'recipes'
Invoke the 'recipes' described [here](https://docs.python.org/3/library/itertools.html#itertools-recipes) as query methods and pass required key-word arguments
```python
Query([1, 2, 3]).ncycles(count=2).to_list()
Query.of(2, 3, 4).take_nth(10, default=66).get()
Query(["ABC", "D", "EF"]).round_robin().to_list()
```

--------------------------------------------
### Intermezzo
As a truly self-respecting functional-style libary <b>fumus</b> supports
<br><i>Option</i> (modeled after Java) and <i>Result</i> patterns (inspired by Rust and Scala).
<br>Feel free to explore those features as well...

--------------------------------------------
### How far can we actually push it?
<p align="center">
  <img src="https://github.com/kaliv0/fumus/blob/main/assets/drago.jpg?raw=true" width="400" alt="Drago">
</p>

- ...some leetcode maybe?
```python
#  check if given string is palindrome; string length is guaranteed to be > 0
def validate_str(string):    
    stop = len(string) // 2 if len(string) > 1 else 1
    return Query.from_range(0, stop).none_match(lambda x: string[x] != string[x - 1])

validate_str("a1b2c3c2b1a")
validate_str("abc321")
validate_str("x")

# True
# False
# True
```
- ...and another one?
```python
# count vowels and constants in given string
def process_str(string):
    ALL_VOWELS = "AEIOUaeiou"
    return (Query(string)
        .filter(lambda ch: ch.isalpha())
        .partition(lambda ch: ch in ALL_VOWELS)  # Partitions entries into true and false ones
        .map(lambda p: tuple(p))
        .enumerate()
        .map(lambda x: ("Vowels" if x[0] == 0 else "Consonants", [len(x[1]), x[1]]))
        .to_dict()
    )

process_str("123Ab5oc-E6db#bCi9<>")
    
# {'Vowels': [4, ('A', 'o', 'E', 'i')], 'Consonants': [6, ('b', 'c', 'd', 'b', 'b', 'C')]}
```

How hideous can it get?
<p align="center">
  <img src="https://github.com/kaliv0/fumus/blob/main/assets/chubby.jpg?raw=true" width="400" alt="Chubby">
</p>
