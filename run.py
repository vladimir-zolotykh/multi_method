#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# PYTHON_ARGCOMPLETE_OK
from types import MethodType
import inspect


class MultiMethod:
    def __init__(self, name: str):
        self.__name = name
        self.methods = {}

    def __get__(self, instance, owner=None):
        if instance is None:
            return self
        return MethodType(self, instance)

    def register(self, method):
        sig = inspect.signature(method)
        types = []
        for name, parm in sig.parameters.items():
            if parm.annotation is inspect.Parameter.empty:
                raise TypeError(f"Annotation of {method.__name__} must not be empty")
            types.append(parm.annotation)
        self.methods[tuple(types)] = method

    def __call__(self, *args):
        types = [type(arg) for arg in args[1:]]
        method = self.methods.get(tuple(types), None)
        if method is None:
            raise TypeError(f"No method for {types}")
        return method(*args[1:])


class _methods:
    def add(x: int, y: int):
        return x + y

    def add(x: str, y: str):  # noqa: F811
        return x + y

    def sub(x: int, y: int):
        return x - y


class MultiDict(dict):
    def __setitem__(self, key, value):
        print(f"{key = }")
        super().__setitem__(key, value)


class IterMeta(type):
    @classmethod
    def __prepare__(cls, clsname, bases):
        return MultiDict()


class MultiDispatch:
    add = MultiMethod("add")
    sub = MultiMethod("sub")

    def __init__(self):
        @self.add.register
        def add(x: int, y: int):
            return x + y

        @self.add.register
        def add(x: str, y: str):  # noqa: F811
            return x + y

        @self.sub.register
        def sub(x: int, y: int):
            return x - y


if __name__ == "__main__":
    dispatch = MultiDispatch()
    print(dispatch.add(2, 5))
    print(dispatch.add("Hello, ", "World!"))
    print(dispatch.sub(5, 2))
