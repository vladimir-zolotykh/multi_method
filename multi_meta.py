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
        for name, param in sig.parameters.items():
            if name == "self":
                continue
            if param.annotation is Parameter.empty:
                raise TypeError(f"{name} must have annotation")
            types.append(param.annotation)
            self._methods[tuple(types)] = method

    def __call__(self, *args):
        types = [type(arg) for arg in args[1:]]
        method = self._methods.get(tuple(types), None)
        if not method:
            raise TypeError(f"No method {self._name} for {types!r}")
        return method(*args)


class MultiDict(dict):
    def __setitem__(self, key, value):
        if key.startswith("__"):
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

    def mul(self, x: float, factor: float = 10.0) -> float:
        return x * factor


if __name__ == "__main__":
    d = Dispatch()
    print(d.add(3, 5))
    print(d.add("Hi, ", "there!"))
    print(d.mul(3.0))
