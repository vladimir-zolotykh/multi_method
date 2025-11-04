#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# PYTHON_ARGCOMPLETE_OK
import inspect


class MultiMethod:
    def __init__(self):
        self.methods = {}

    def register(self, method):
        sig = inspect.signature(method)
        types = []
        for name, parm in sig.parameters.items():
            if parm.annotation is inspect.Parameter.empty:
                raise TypeError(f"Annotation of {method.__name__} must not be empty")
            types.append(parm.annotation)
        self.methods[tuple(types)] = method

    def __call__(self, *args):
        types = [type(arg) for arg in args]
        method = self.methods.get(tuple(types), None)
        if method is None:
            raise TypeError(f"No method for {types}")
        return method(*args)


mm = MultiMethod()


@mm.register
def add(x: int, y: int):  # noqa: F811
    return x + y


@mm.register
def add(x: str, y: str):  # noqa: F811
    return x + y


if __name__ == "__main__":
    print(mm.add(2, 5))
    print(mm.add("hello", "world"))
