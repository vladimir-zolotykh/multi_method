#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# PYTHON_ARGCOMPLETE_OK
from inspect import signature, Parameter


class MultiDict(dict):
    def __setitem__(self, key, value):
        types = []
        if callable(value):
            sig = signature(value)
            for name, a in sig.parameters.items():
                if a.annotation is Parameter.empty:
                    raise TypeError(f"parameter {name} shall have annotation")
                types.append(a.annotation)
        if types:
            print(f"{types = }")
        super().__setitem__(key, value)


class IterMeta(type):
    @classmethod
    def __prepare__(cls, clsname, bases):
        return MultiDict()


class _methods(metaclass=IterMeta):
    def add(x: int, y: int):
        return x + y

    def add(x: str, y: str):  # noqa F811
        return x + y

    def sub(x: int, y: int):
        return x - y


# prints:
# key = '__module__'
# key = '__qualname__'
# key = 'add'
# key = 'add'
# key = 'sub'
#
