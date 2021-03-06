from pipetools import X, sort_by, take_first, foreach, where, select_first, group_by
from pipetools import unless, flatten, take_until, as_kwargs, drop_first


class TestPipeUtil:

    def test_pipability(self):
        f = xrange | foreach(X) | sum

        result = f(4)
        assert result == 6

    def test_input(self):
        result = xrange(5) > where(X % 2) | list
        assert result == [1, 3]


class TestSortBy:

    def test_x(self):

        result = sort_by(-X[1])(zip('what', [1, 2, 3, 4]))

        assert result == [
            ('t', 4),
            ('a', 3),
            ('h', 2),
            ('w', 1),
        ]

    def test_descending(self):

        result = zip('what', [1, 2, 3, 4]) > sort_by(X[1]).descending

        assert result == [
            ('t', 4),
            ('a', 3),
            ('h', 2),
            ('w', 1),
        ]


class TestTakeFirst:

    def test_take_first(self):
        assert [0, 1, 2] == list(take_first(3)(xrange(10)))


class TestTupleMaker:

    def test_make_tuple(self):
        result = [1, 2, 3] > foreach((X, X % 2)) | list
        assert result == [(1, 1), (2, 0), (3, 1)]


class TestListMaker:

    def test_make_list(self):
        result = [1, 2, 3] > foreach([X, X % 2]) | list
        assert result == [[1, 1], [2, 0], [3, 1]]


class TestDictMaker:

    def test_make_dict(self):
        result = [1, 2] > foreach({'num': X, 'str': str}) | list
        assert result == [{'num': 1, 'str': '1'}, {'num': 2, 'str': '2'}]


class TestSelectFirst:

    def test_select_first(self):
        result = select_first(X % 2 == 0)([3, 4, 5, 6])
        assert result == 4

    def test_select_first_none(self):
        result = select_first(X == 2)([0, 1, 0, 1])
        assert result is None

    def test_select_first_empty(self):
        assert select_first(X)([]) is None


class TestAutoStringFormatter:

    def test_foreach_format(self):
        result = [1, 2] > foreach("Number {0}") | list
        assert result == ['Number 1', 'Number 2']


class TestUnless:

    def test_ok(self):
        f = unless(AttributeError, foreach(X.lower())) | list
        assert f("ABC") == ['a', 'b', 'c']

    def test_with_exception(self):
        f = unless(AttributeError, foreach(X.lower()) | list)
        assert f(['A', 'B', 37]) is None

    def test_with_exception_in_foreach(self):
        f = foreach(unless(AttributeError, X.lower())) | list
        assert f(['A', 'B', 37]) == ['a', 'b', None]

    def test_partial_ok(self):
        f = unless(TypeError, enumerate, start=3) | list
        assert f('abc') == [(3, 'a'), (4, 'b'), (5, 'c')]

    def test_partial_exc(self):
        f = unless(TypeError, enumerate, start=3)
        assert f(42) is None

    def test_X_ok(self):
        f = unless(TypeError, X * 'x')
        assert f(3) == 'xxx'

    def test_X_exception(self):
        f = unless(TypeError, X * 'x')
        assert f('x') is None


class TestFlatten:

    def test_flatten(self):
        assert (list(flatten([1, [2, 3], (4, ('five', 6))]))
            == [1, 2, 3, 4, 'five', 6])

    def test_flatten_args(self):
        assert (list(flatten(1, [2, 3], (4, ('five', 6))))
            == [1, 2, 3, 4, 'five', 6])


class TestTakeUntil:

    def test_basic(self):
        f = take_until(X > 5)
        assert list(f([1, 2, 3, 1, 6, 1, 3])) == [1, 2, 3, 1]


class TestAsKwargs:

    def test_as_kwargs(self):
        d = {'foo': 4, 'bar': 2}
        assert as_kwargs(lambda **kw: kw)(d) == d


class TestRegexCondidion:

    def test_where_regex(self):
        data = [
            'foo bar',
            'boo far',
            'foolproof',
        ]
        assert (data > where(r'^foo') | list) == [
            'foo bar',
            'foolproof',
        ]

    def test_select_first_regex(self):
        data = [
            'foo bar',
            'boo far',
            'foolproof',
        ]
        assert (data > select_first(r'^b.*r$')) == 'boo far'


class TestGroupBy:

    def test_basic(self):
        src = [1, 2, 3, 4, 5, 6]
        assert (src > group_by(X % 2) | dict) == {0: [2, 4, 6], 1: [1, 3, 5]}


class TestDropFirst:

    def test_list(self):
        src = [1, 2, 3, 4, 5, 6]
        assert (src > drop_first(3) | list) == [4, 5, 6]

    def test_iterable(self):
        assert (xrange(10000) > drop_first(9999) | list) == [9999]
