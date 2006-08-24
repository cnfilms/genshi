# -*- coding: utf-8 -*-
#
# Copyright (C) 2006 Edgewall Software
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution. The terms
# are also available at http://markup.edgewall.org/wiki/License.
#
# This software consists of voluntary contributions made by many
# individuals. For the exact contribution history, see the revision
# history and logs, available at hhttp://markup.edgewall.org/log/.

import doctest
import sys
import unittest

from markup.eval import Expression, Undefined


class ExpressionTestCase(unittest.TestCase):

    def test_name_lookup(self):
        self.assertEqual('bar', Expression('foo').evaluate({'foo': 'bar'}))
        self.assertEqual(id, Expression('id').evaluate({}, nocall=True))
        self.assertEqual('bar', Expression('id').evaluate({'id': 'bar'}))
        self.assertEqual(None, Expression('id').evaluate({'id': None},
                                                         nocall=True))

    def test_str_literal(self):
        self.assertEqual('foo', Expression('"foo"').evaluate({}))
        self.assertEqual('foo', Expression('"""foo"""').evaluate({}))
        self.assertEqual('foo', Expression("'foo'").evaluate({}))
        self.assertEqual('foo', Expression("'''foo'''").evaluate({}))
        self.assertEqual('foo', Expression("u'foo'").evaluate({}))
        self.assertEqual('foo', Expression("r'foo'").evaluate({}))

    def test_str_literal_non_ascii(self):
        expr = Expression(u"u'\xfe'")
        self.assertEqual(u'þ', expr.evaluate({}))
        expr = Expression("u'\xfe'")
        self.assertEqual(u'þ', expr.evaluate({}))
        expr = Expression("'\xc3\xbe'")
        self.assertEqual(u'þ', expr.evaluate({}))

    def test_num_literal(self):
        self.assertEqual(42, Expression("42").evaluate({}))
        self.assertEqual(42L, Expression("42L").evaluate({}))
        self.assertEqual(.42, Expression(".42").evaluate({}))
        self.assertEqual(07, Expression("07").evaluate({}))
        self.assertEqual(0xF2, Expression("0xF2").evaluate({}))
        self.assertEqual(0XF2, Expression("0XF2").evaluate({}))

    def test_dict_literal(self):
        self.assertEqual({}, Expression("{}").evaluate({}))
        self.assertEqual({'key': True},
                         Expression("{'key': value}").evaluate({'value': True}))

    def test_list_literal(self):
        self.assertEqual([], Expression("[]").evaluate({}))
        self.assertEqual([1, 2, 3], Expression("[1, 2, 3]").evaluate({}))
        self.assertEqual([True],
                         Expression("[value]").evaluate({'value': True}))

    def test_tuple_literal(self):
        self.assertEqual((), Expression("()").evaluate({}))
        self.assertEqual((1, 2, 3), Expression("(1, 2, 3)").evaluate({}))
        self.assertEqual((True,),
                         Expression("(value,)").evaluate({'value': True}))

    def test_unaryop_pos(self):
        self.assertEqual(1, Expression("+1").evaluate({}))
        self.assertEqual(1, Expression("+x").evaluate({'x': 1}))

    def test_unaryop_neg(self):
        self.assertEqual(-1, Expression("-1").evaluate({}))
        self.assertEqual(-1, Expression("-x").evaluate({'x': 1}))

    def test_unaryop_not(self):
        self.assertEqual(False, Expression("not True").evaluate({}))
        self.assertEqual(False, Expression("not x").evaluate({'x': True}))

    def test_unaryop_inv(self):
        self.assertEqual(-2, Expression("~1").evaluate({}))
        self.assertEqual(-2, Expression("~x").evaluate({'x': 1}))

    def test_binop_add(self):
        self.assertEqual(3, Expression("2 + 1").evaluate({}))
        self.assertEqual(3, Expression("x + y").evaluate({'x': 2, 'y': 1}))

    def test_binop_sub(self):
        self.assertEqual(1, Expression("2 - 1").evaluate({}))
        self.assertEqual(1, Expression("x - y").evaluate({'x': 1, 'y': 1}))

    def test_binop_sub(self):
        self.assertEqual(1, Expression("2 - 1").evaluate({}))
        self.assertEqual(1, Expression("x - y").evaluate({'x': 2, 'y': 1}))

    def test_binop_mul(self):
        self.assertEqual(4, Expression("2 * 2").evaluate({}))
        self.assertEqual(4, Expression("x * y").evaluate({'x': 2, 'y': 2}))

    def test_binop_pow(self):
        self.assertEqual(4, Expression("2 ** 2").evaluate({}))
        self.assertEqual(4, Expression("x ** y").evaluate({'x': 2, 'y': 2}))

    def test_binop_div(self):
        self.assertEqual(2, Expression("4 / 2").evaluate({}))
        self.assertEqual(2, Expression("x / y").evaluate({'x': 4, 'y': 2}))

    def test_binop_floordiv(self):
        self.assertEqual(1, Expression("3 // 2").evaluate({}))
        self.assertEqual(1, Expression("x // y").evaluate({'x': 3, 'y': 2}))

    def test_binop_mod(self):
        self.assertEqual(1, Expression("3 % 2").evaluate({}))
        self.assertEqual(1, Expression("x % y").evaluate({'x': 3, 'y': 2}))

    def test_binop_and(self):
        self.assertEqual(0, Expression("1 & 0").evaluate({}))
        self.assertEqual(0, Expression("x & y").evaluate({'x': 1, 'y': 0}))

    def test_binop_or(self):
        self.assertEqual(1, Expression("1 | 0").evaluate({}))
        self.assertEqual(1, Expression("x | y").evaluate({'x': 1, 'y': 0}))

    def test_binop_contains(self):
        self.assertEqual(True, Expression("1 in (1, 2, 3)").evaluate({}))
        self.assertEqual(True, Expression("x in y").evaluate({'x': 1,
                                                              'y': (1, 2, 3)}))

    def test_binop_not_contains(self):
        self.assertEqual(True, Expression("4 not in (1, 2, 3)").evaluate({}))
        self.assertEqual(True, Expression("x not in y").evaluate({'x': 4,
                                                                  'y': (1, 2, 3)}))

    def test_binop_is(self):
        self.assertEqual(True, Expression("1 is 1").evaluate({}))
        self.assertEqual(True, Expression("x is y").evaluate({'x': 1, 'y': 1}))
        self.assertEqual(False, Expression("1 is 2").evaluate({}))
        self.assertEqual(False, Expression("x is y").evaluate({'x': 1, 'y': 2}))

    def test_binop_is_not(self):
        self.assertEqual(True, Expression("1 is not 2").evaluate({}))
        self.assertEqual(True, Expression("x is not y").evaluate({'x': 1,
                                                                  'y': 2}))
        self.assertEqual(False, Expression("1 is not 1").evaluate({}))
        self.assertEqual(False, Expression("x is not y").evaluate({'x': 1,
                                                                   'y': 1}))

    def test_boolop_and(self):
        self.assertEqual(False, Expression("True and False").evaluate({}))
        self.assertEqual(False, Expression("x and y").evaluate({'x': True,
                                                                'y': False}))

    def test_boolop_or(self):
        self.assertEqual(True, Expression("True or False").evaluate({}))
        self.assertEqual(True, Expression("x or y").evaluate({'x': True,
                                                              'y': False}))

    def test_compare_eq(self):
        self.assertEqual(True, Expression("1 == 1").evaluate({}))
        self.assertEqual(True, Expression("x == y").evaluate({'x': 1, 'y': 1}))

    def test_compare_ne(self):
        self.assertEqual(False, Expression("1 != 1").evaluate({}))
        self.assertEqual(False, Expression("x != y").evaluate({'x': 1, 'y': 1}))
        self.assertEqual(False, Expression("1 <> 1").evaluate({}))
        self.assertEqual(False, Expression("x <> y").evaluate({'x': 1, 'y': 1}))

    def test_compare_lt(self):
        self.assertEqual(True, Expression("1 < 2").evaluate({}))
        self.assertEqual(True, Expression("x < y").evaluate({'x': 1, 'y': 2}))

    def test_compare_le(self):
        self.assertEqual(True, Expression("1 <= 1").evaluate({}))
        self.assertEqual(True, Expression("x <= y").evaluate({'x': 1, 'y': 1}))

    def test_compare_gt(self):
        self.assertEqual(True, Expression("2 > 1").evaluate({}))
        self.assertEqual(True, Expression("x > y").evaluate({'x': 2, 'y': 1}))

    def test_compare_ge(self):
        self.assertEqual(True, Expression("1 >= 1").evaluate({}))
        self.assertEqual(True, Expression("x >= y").evaluate({'x': 1, 'y': 1}))

    def test_compare_multi(self):
        self.assertEqual(True, Expression("1 != 3 == 3").evaluate({}))
        self.assertEqual(True, Expression("x != y == y").evaluate({'x': 1,
                                                                   'y': 3}))

    def test_call_function(self):
        self.assertEqual(42, Expression("foo()").evaluate({'foo': lambda: 42}))
        data = {'foo': 'bar'}
        self.assertEqual('BAR', Expression("foo.upper()").evaluate(data))
        data = {'foo': {'bar': range(42)}}
        self.assertEqual(42, Expression("len(foo.bar)").evaluate(data))

    def test_call_keywords(self):
        self.assertEqual(42, Expression("foo(x=bar)").evaluate({'foo': lambda x: x,
                                                                'bar': 42}))

    def test_call_function_without_params(self):
        self.assertEqual(42, Expression("foo").evaluate({'foo': lambda: 42}))
        data = {'foo': 'bar'}
        self.assertEqual('BAR', Expression("foo.upper").evaluate(data))
        data = {'foo': {'bar': range(42)}}

    def test_lambda(self):
        # Define a custom `sorted` function cause the builtin isn't available
        # on Python 2.3
        def sorted(items, compfunc):
            items.sort(compfunc)
            return items
        data = {'items': [{'name': 'b', 'value': 0}, {'name': 'a', 'value': 1}],
                'sorted': sorted}
        expr = Expression("sorted(items, lambda a, b: cmp(a.name, b.name))")
        self.assertEqual([{'name': 'a', 'value': 1}, {'name': 'b', 'value': 0}],
                         expr.evaluate(data))

    def test_list_comprehension(self):
        expr = Expression("[n for n in numbers if n < 2]")
        self.assertEqual([0, 1], expr.evaluate({'numbers': range(5)}))

        expr = Expression("[(i, n + 1) for i, n in enumerate(numbers)]")
        self.assertEqual([(0, 1), (1, 2), (2, 3), (3, 4), (4, 5)],
                         expr.evaluate({'numbers': range(5)}))

        expr = Expression("[offset + n for n in numbers]")
        self.assertEqual([2, 3, 4, 5, 6],
                         expr.evaluate({'numbers': range(5), 'offset': 2}))

    def test_list_comprehension_with_getattr(self):
        items = [{'name': 'a', 'value': 1}, {'name': 'b', 'value': 2}]
        expr = Expression("[i.name for i in items if i.value > 1]")
        self.assertEqual(['b'], expr.evaluate({'items': items}))

    def test_list_comprehension_with_getitem(self):
        items = [{'name': 'a', 'value': 1}, {'name': 'b', 'value': 2}]
        expr = Expression("[i['name'] for i in items if i['value'] > 1]")
        self.assertEqual(['b'], expr.evaluate({'items': items}))

    # generator expressions only supported in Python 2.4 and up
    if sys.version_info >= (2, 4):
        def test_generator_expression(self):
            expr = Expression("list(n for n in numbers if n < 2)")
            self.assertEqual([0, 1], expr.evaluate({'numbers': range(5)}))

            expr = Expression("list((i, n + 1) for i, n in enumerate(numbers))")
            self.assertEqual([(0, 1), (1, 2), (2, 3), (3, 4), (4, 5)],
                             expr.evaluate({'numbers': range(5)}))

            expr = Expression("list(offset + n for n in numbers)")
            self.assertEqual([2, 3, 4, 5, 6],
                             expr.evaluate({'numbers': range(5), 'offset': 2}))

        def test_generator_expression_with_getattr(self):
            items = [{'name': 'a', 'value': 1}, {'name': 'b', 'value': 2}]
            expr = Expression("list(i.name for i in items if i.value > 1)")
            self.assertEqual(['b'], expr.evaluate({'items': items}))

        def test_generator_expression_with_getitem(self):
            items = [{'name': 'a', 'value': 1}, {'name': 'b', 'value': 2}]
            expr = Expression("list(i['name'] for i in items if i['value'] > 1)")
            self.assertEqual(['b'], expr.evaluate({'items': items}))

    def test_error_access_undefined(self):
        expr = Expression("nothing", filename='index.html', lineno=50)
        self.assertEqual(Undefined, type(expr.evaluate({})))

    def test_error_call_undefined(self):
        expr = Expression("nothing()", filename='index.html', lineno=50)
        try:
            expr.evaluate({})
            self.fail('Expected NameError')
        except NameError, e:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            frame = exc_traceback.tb_next
            frames = []
            while frame.tb_next:
                frame = frame.tb_next
                frames.append(frame)
            self.assertEqual('<Expression "nothing()">',
                             frames[-3].tb_frame.f_code.co_name)
            self.assertEqual('index.html',
                             frames[-3].tb_frame.f_code.co_filename)
            self.assertEqual(50, frames[-3].tb_lineno)

    def test_error_getattr_undefined(self):
        expr = Expression("nothing.nil", filename='index.html', lineno=50)
        try:
            expr.evaluate({})
            self.fail('Expected NameError')
        except NameError, e:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            frame = exc_traceback.tb_next
            frames = []
            while frame.tb_next:
                frame = frame.tb_next
                frames.append(frame)
            self.assertEqual('<Expression "nothing.nil">',
                             frames[-3].tb_frame.f_code.co_name)
            self.assertEqual('index.html',
                             frames[-3].tb_frame.f_code.co_filename)
            self.assertEqual(50, frames[-3].tb_lineno)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ExpressionTestCase, 'test'))
    suite.addTest(doctest.DocTestSuite(Expression.__module__))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='suite')
