#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# PYTHON_ARGCOMPLETE_OK
from types import MethodType
from typing import Callable, Any
from inspect import signature, Parameter


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
        for name, annotation in sig.parameters.items():
            if name == "self":
                continue
            if annotation is Parameter.empty:
                raise TypeError(f"{name} must have annotation")
            types.append(annotation)
            self._methods[tuple(types)] = method

    def __call__(self, *args):
        types = [type(arg) for arg in args[1:]]
        method = self._methods.get(tuple(types), None)
        if not method:
            raise TypeError(f"No method {self._name} for {types!r}")
        return method(*args)


class MultiDict(dict):
    def __setitem__(self, key, value):
        mm: MultiMethod
        if key in self:
            mm = self[key]
            mm.register(value)
        else:
            mm = MultiMethod(key)
        super().__setitem__(key, mm)


class MultiMeta(type):
    @classmethod
    def __prepare__(cls, clsname, bases):
        return MultiDict()


class Dispatch(metaclass=MultiMeta):
    def add(x: int, y: int) -> int:
        return x + y

    def add(x: str, y: str) -> str:  # noqa F811
        return x + y


if __name__ == "__main__":
    d = Dispatch()
    print(d.add(3, 5))
    print(d.add("Hi, ", "there!"))
