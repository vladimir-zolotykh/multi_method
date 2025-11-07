#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# PYTHON_ARGCOMPLETE_OK
from types import MethodType
from typing import Callable, Any
from inspect import signature, Parameter
import unittest
import time
import io
import contextlib


class MultiMethod:
    def __init__(self, name=None):
        self._name = name
        self._methods: dict[tuple[Any, ...], Callable] = {}

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return MethodType(self, instance)

    def register(self, method):
        sig = signature(method)
        types = []
        for name, param in sig.parameters.items():
            if name == "self":
                continue
            if param.annotation is Parameter.empty:
                raise TypeError(f"{name} must have annotation")
            if param.default is not Parameter.empty:
                self._methods[tuple(types)] = method
            types.append(param.annotation)
        self._methods[tuple(types)] = method

    def __call__(self, *args):
        types = [type(arg) for arg in args[1:]]
        method = self._methods.get(tuple(types), None)
        if not method:
            raise TypeError(f"No method {self._name} for {tuple(types)!r}")
        return method(*args)


class MultiDict(dict):
    def __setitem__(self, key, value):
        if key.startswith("__") and not callable(value):
            return super().__setitem__(key, value)
        if key in self:
            mm = self[key]
            if isinstance(mm, MultiMethod):
                mm.register(value)
            else:
                mm = MultiMethod(key)
                mm.register(value)
        else:
            mm = MultiMethod(key)
            mm.register(value)
        super().__setitem__(key, mm)


class MultiMeta(type):
    def __new__(cls, clsname, bases, clsdict):
        return super().__new__(cls, clsname, bases, dict(clsdict))

    @classmethod
    def __prepare__(cls, clsname, bases):
        return MultiDict()


class Dispatch(metaclass=MultiMeta):
    def add(self, x: int, y: int) -> int:
        return x + y

    def add(self, x: str, y: str) -> str:  # noqa F811
        return x + y

    def mul(self, x: float, y: float) -> float:
        return x * y

    def mul(self, x: float, factor: float = 10.0) -> float:  # noqa F811
        return x * factor


class Spam(metaclass=MultiMeta):
    def bar(self, x: int, y: int):
        print("Bar 1: ", x, y)

    def bar(self, s: str, n: int = 0):  # noqa F811
        print("Bar 2: ", s, n)


class Date(metaclass=MultiMeta):
    def __init__(self, year: int, month: int, day: int):
        self.year = year
        self.month = month
        self.day = day

    def __init__(self):  # noqa F811
        t = time.localtime()
        self.__init__(t.tm_year, t.tm_mon, t.tm_mday)


class TestMultiMethod(unittest.TestCase):
    def setUp(self):
        self.d = Dispatch()

    def test_add(self):
        self.assertEqual(self.d.add(3, 5), 8)
        self.assertEqual(self.d.add("Hi, ", "there!"), "Hi, there!")

    def test_mul(self):
        self.assertEqual(self.d.mul(3.0), 30.0)
        self.assertEqual(self.d.mul(3.0, 2.5), 7.5)


class RunBeazleyTest(unittest.TestCase):
    def setUp(self):
        self.spam = Spam()

    def test_10_spam(self):
        with contextlib.redirect_stdout(io.StringIO()) as f:
            self.spam.bar(2, 3)
            self.assertEqual(f.getvalue(), "Bar 1:  2 3\n")

    def test_12_spam(self):
        with contextlib.redirect_stdout(io.StringIO()) as f:
            self.spam.bar("hello")
            self.assertEqual(f.getvalue(), "Bar 2:  hello 0\n")

    def test_14_spam(self):
        with contextlib.redirect_stdout(io.StringIO()) as f:
            self.spam.bar("hello", 5)
            self.assertEqual(f.getvalue(), "Bar 2:  hello 5\n")

    def test_16_spam(self):
        with contextlib.redirect_stdout(io.StringIO()) as f:
            self.spam.bar("hello", 5)
            self.assertEqual(f.getvalue(), "Bar 2:  hello 5\n")

    def test_18_spam(self):
        with self.assertRaises(TypeError):
            self.spam.bar(2, "hello")

    def test_20_date(self):
        tup = (2012, 12, 21)
        d = Date(*tup)
        self.assertEqual((d.year, d.month, d.day), tup)

    def test_30_date(self):
        e = Date()
        t = time.localtime()
        self.assertEqual((e.year, e.month, e.day), (t.tm_year, t.tm_mon, t.tm_mday))


if __name__ == "__main__":
    unittest.main()
