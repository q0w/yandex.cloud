from typing import Any, Callable, TypeVar

_T = TypeVar('_T')
_P = TypeVar('_P')
_F = TypeVar('_F')


def tap(f: Callable[[_T], Any]) -> Callable[[_T], _T]:
    def inner(arg: _T) -> _T:
        f(arg)
        return arg

    return inner


def untap(f: Callable[[_T], Any]) -> Callable[[_T], None]:
    def inner(arg: _T) -> None:
        f(arg)

    return inner


def identity(v: _T) -> _T:
    return v


def compose(f1: Callable[[_T], _P], f2: Callable[[_P], _F]) -> Callable[[_T], _F]:
    return lambda a: f2(f1(a))
