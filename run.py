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


class MultiDispatch:
    add = MultiMethod()
    sub = MultiMethod()

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
