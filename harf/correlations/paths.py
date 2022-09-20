from dataclasses import dataclass
from typing import TypeVar, Protocol, Generic, Union

A = TypeVar("A")
B = TypeVar("B")


class Path(Protocol):
    next_: "Path"

    def __len__(self) -> int:
        ...


@dataclass
class IntPath(Generic[A]):
    index: int
    next_: A

    def __str__(self):
        return f"[{self.index}]{self.next_}"

    def __len__(self):
        return 1 + len(self.next_)


@dataclass
class StrPath(Generic[A]):
    key: str
    next_: A

    def __str__(self):
        return f".{self.key}{self.next_}"

    def __len__(self):
        return 1 + len(self.next_)


@dataclass
class EndPath:
    def __str__(self):
        return ""

    def __len__(self):
        return 1


DataPath = Union[IntPath[A], StrPath[A], EndPath]["DataPath"]  # type: ignore[index]


class UrlPath(IntPath[DataPath]):
    def __str__(self):
        return f".url{super().__str__()}"


class QueryPath(StrPath[DataPath]):
    def __str__(self):
        return f".queryString{super().__str__()}"


class HeaderPath(StrPath[DataPath]):
    def __str__(self):
        return f".header{super().__str__()}"


class CookiePath(StrPath[DataPath]):
    def __str__(self):
        return f".cookie{super().__str__()}"


@dataclass
class BodyPath:
    next_: DataPath

    def __str__(self):
        return f".body{self.next_}"

    def __len__(self):
        return 1 + len(self.next_)


@dataclass
class RequestPath:
    next_: Union[UrlPath, QueryPath, BodyPath, HeaderPath]

    def __str__(self):
        return f".request{self.next_}"

    def __len__(self):
        return 1 + len(self.next_)


@dataclass
class ResponsePath:
    next_: Union[HeaderPath, BodyPath]

    def __str__(self):
        return f".response{self.next_}"

    def __len__(self):
        return 1 + len(self.next_)


@dataclass
class EntryPath:
    index: int
    next_: Union[RequestPath, ResponsePath]

    def __str__(self):
        return f"entry_{self.index}{self.next_}"

    def __len__(self):
        return 1 + len(self.next_)
