#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# PYTHON_ARGCOMPLETE_OK
class MultiDict(dict):
    def __setitem__(self, key, value):
        print(f"{key = }")
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
