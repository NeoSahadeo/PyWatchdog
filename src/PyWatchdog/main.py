import subprocess
import os
import threading
import time
import sys
import hashlib
import json
from dataclasses import dataclass
from typing import Callable, ClassVar, Dict, List


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class PyWatchdog(metaclass=Singleton):
    __dirs__: list[str] = []
    __events__: ClassVar[Dict[str, List[Callable]]] = {}

    _poll = 0
    _id = ""
    _cache = {}

    def __init__(self):
        self._stop_event = threading.Event()
        self._thread = None

    def subscribe(self, callback: Callable) -> None:
        events = self.__events__.get("file_change")
        if events:
            events.append(callback)
        else:
            self.__events__["file_change"] = []
            self.__events__["file_change"].append(callback)

    def unsubscribe(self, callback: Callable) -> None:
        events = self.__events__.get("file_change")
        if not events:
            return
        events.remove(callback)
        if events.__len__() == 0:
            self.__events__.pop("file_change")

    def dispatch(self, event_name: str, *args, **kwargs):
        for event in self.__events__.get(event_name, []):
            event(*args, **kwargs)

    def watch(self, poll=1):
        self._poll = poll
        if self._thread and self._thread.is_alive():
            self.stop()

        self._stop_event.clear()
        self._thread = threading.Thread(target=self._scan_dirs)
        self._thread.start()

    def stop(self):
        self._stop_event.set()
        if self._thread:
            self._thread.join()

    def monitor(self, dirs: list[str] = []):
        for x in dirs:
            if x not in self.__dirs__:
                self.__dirs__.append(x)
        self._cache = {}

    def unmonitor(self, dirs: list[str] = []):
        for x in dirs:
            if x in self.__dirs__:
                self.__dirs__.remove(x)
        self._cache = {}

    def _hash(self, string: str) -> str:
        return hashlib.md5(bytes(string, "utf-8")).hexdigest()

    def _cache_hash(self, file: str) -> None:
        _hash = self._hash(file)
        try:
            if not self._cache.get(_hash):
                self._cache[_hash] = os.stat(file).st_mtime
            else:
                if self._cache.get(_hash) != os.stat(file).st_mtime:
                    self._cache[_hash] = os.stat(file).st_mtime
        except FileNotFoundError:
            return

    def _scan_dirs(self):
        while not self._stop_event.is_set():
            for x in self.__dirs__:
                if not os.path.exists(x):
                    continue

                if not os.path.isdir(x):
                    self._cache_hash(x)
                    continue

                for root, dirs, files in os.walk(x):
                    for p in files:
                        self._cache_hash(os.path.join(root, p))

            _new_hash = hashlib.md5(bytes(json.dumps(self._cache), "utf-8")).hexdigest()
            if _new_hash != self._id:
                self.dispatch("file_change")
                self._id = _new_hash

            time.sleep(self._poll)


if __name__ == "__main__":

    import argparse

    parser = argparse.ArgumentParser(
        prog="Watchdog", description="Watch for file changes"
    )

    parser.add_argument("--poll", help="Set the polling rate", type=float, default=1)
    parser.add_argument("--paths", help="List of paths", type=str, default="")
    parser.add_argument(
        "--command", help="A single command to run", type=str, default=""
    )
    parser.add_argument("--callbacks", help="Callback scripts", type=str, default="")

    args = sys.argv[1:]
    if len(args) == 0:
        parser.print_help()
        sys.exit(1)

    poll = 0
    paths = []
    callbacks_funcs = []

    namespace = parser.parse_args(args)._get_kwargs()
    for x in namespace:
        match x[0]:
            case "poll":
                poll = x[1]
            case "paths":
                paths = x[1].split(",")
            case "command":
                if x[1] == "":
                    continue

                def make_func(value):
                    def func():
                        subprocess.run(value.split(" "))

                    return func

                callbacks_funcs.append(make_func(x[1]))

            case "callbacks":
                if x[1] == "":
                    continue

                for cb in x[1].split(","):

                    def make_func(value):
                        def func():
                            subprocess.run(value)

                        return func

                    callbacks_funcs.append(make_func(cb))
            case _:
                pass

    for x in callbacks_funcs:
        PyWatchdog().subscribe(x)

    PyWatchdog().monitor(paths)
    PyWatchdog().watch(poll)
