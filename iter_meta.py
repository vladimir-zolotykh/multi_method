#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# PYTHON_ARGCOMPLETE_OK
class IterMeta(type):
    def __init__(cls, name, bases, namespace):
        super().__init__(name, bases, namespace)
        # Collect all callables that look like methods
        methods = {
            k: v for k, v in namespace.items() if callable(v) and not k.startswith("__")
        }

        # Call the register() function if it exists
        if hasattr(cls, "register") and callable(cls.register):
            cls.register(methods)
        else:
            raise TypeError(f"{name} must define a 'register' classmethod")


class _methods(metaclass=IterMeta):
    @classmethod
    def register(cls, methods):
        print(f"Registering {len(methods)} methods for {cls.__name__}:")
        for name, fn in methods.items():
            print(f"  {name} -> {fn}")

    def add(x: int, y: int):
        return x + y

    def add(x: str, y: str):
        return x + y

    def sub(x: int, y: int):
        return x - y
