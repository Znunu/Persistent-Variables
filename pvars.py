
import pathlib
import shutil
import inspect
import typing
import atexit
import signal
import pickle
import json
import enum
import csv
import os
import re


_contexts = []


class Format(enum.Enum):
    PICKLE = enum.auto()
    JSON = enum.auto()
    CSV = enum.auto()


class PersistentDict(dict):

    def __init__(self, filename, fileformat=Format.PICKLE, dump_args=None):
        if dump_args is None:
            self.dump_args = {}
        else:
            self.dump_args = dump_args
        self.file_format = fileformat
        self.file_name = filename
        if os.access(filename, os.F_OK):
            self.load(filename)
        dict.__init__(self)

    def sync(self):
        filename = self.file_name
        tempname = filename + ".tmp"
        try:
            with open(tempname, 'wb' if self.file_format is Format.PICKLE else 'w', newline='' if self.file_format is Format.CSV else None) as fileobj:
                self.dump(fileobj)
        except Exception:
            os.remove(tempname)
            raise
        finally:
            fileobj.close()
        shutil.move(tempname, self.file_name)    # atomic commit

    def __enter__(self):
        return self

    def __exit__(self, *exc_info):
        self.sync()

    def dump(self, fileobj):
        if self.file_format == Format.CSV:
            csv.writer(fileobj).writerows(self.items(), **self.dump_args)
        elif self.file_format == Format.JSON:
            json.dump(dict(self), fileobj, **self.dump_args)
        elif self.file_format == Format.PICKLE:
            pickle.dump(dict(self), fileobj, 5, **self.dump_args)
        else:
            raise NotImplementedError("Unknown format: " + repr(self.file_format.name))

    def load(self, filename):
        # try formats from most restrictive to least restrictive
        for loader in (pickle.load, json.load, csv.reader):
            for mode in ("r", "rb"):
                try:
                    with open(filename, mode) as fileobj:
                        return self.update(loader(fileobj))
                except Exception:
                    pass
        raise ValueError("File not in a supported format")


class PVar:

    def __init__(self, name, value):
        self.name = name
        self._callback = value

    def value(self):
        return self._callback()


class ModuleContext:

    def __init__(self, path):
        self.auto_save = True
        self.path = path
        self.db = PersistentDict(path, Format.PICKLE)
        self.pvar_index = {}

    def make_var(self, default, callback: typing.Callable):
        code = inspect.getsource(callback)
        if "def" in code:
            match = re.search(r"return\s*(\w+)", code)
        elif "lambda" in code:
            match = re.search(r":\s*(\w+)", code)
        else:
            raise TypeError("Improper function passed")
        if not match:
            raise TypeError("Improper function passed")
        var_name = match.group(1)
        pvar = PVar(var_name, callback)
        self.pvar_index[pvar.name] = pvar
        if pvar.name not in self.db:
            return default
        else:
            return self.db[pvar.name]

    def clear(self) -> None:
        for var in self.db: del self.db[var]
        self.db.sync()

    def all(self) -> PersistentDict:
        return self.db

    def save(self) -> None:
        for name, pvar in self.pvar_index.items(): self.db[name] = pvar.value()
        self.db.sync()

    def configure(self, *, auto_save: bool = None, file_format: Format = None, extra_param: dict = None) -> None:
        if auto_save:
            self.auto_save = auto_save
        if file_format:
            self.db.file_format = file_format
        if extra_param:
            self.db.dump_args = extra_param


def get_context(extra_path: typing.Union[str, os.PathLike] = "", **config_params):
    global _contexts
    frame = inspect.stack()[1]
    module = inspect.getmodule(frame[0])
    module_path = pathlib.Path(module.__file__)
    db_dir = pathlib.Path(module.__file__).parent / os.fspath(extra_path)
    db_dir.mkdir(parents=True, exist_ok=True)
    db_path = (db_dir / (module_path.stem + ".pydb")).resolve().__str__()
    if not db_dir.parent.exists(): raise Exception(f"{db_path} is not valid")
    for ctx in _contexts:
        if db_path == ctx.path:
            return ctx
    ctx = ModuleContext(db_path)
    ctx.configure(**config_params)
    _contexts.append(ctx)
    return ctx


def _clean_up():
    for context in _contexts:
        try:
            if context.auto_save:
                context.save()
        except Exception:
            raise RuntimeError(f"Failed saving to {context.path}")


atexit.register(_clean_up)
signal.signal(signal.SIGINT, lambda x, y: exit())


if __name__ == "__main__":
    pass
