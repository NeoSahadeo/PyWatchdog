# PyWatchdog

A dead-simple watchdog Python library. No bloat, no need to "learn this" - just
a library to get things done.

## Getting Started

__Installing__

```bash
uv add git+https://github.com/NeoSahadeo/PyWatchdog
```

```bash
pip install git+https://github.com/NeoSahadeo/PyWatchdog
```

To run the watchdog you need to:

1. `monitor` a file(s)/folder(s)
2. `subscribe` a callback
3. `watch` for changes

See, dead-simple!

__Example:__

```python
from PyWatchdog import PyWatchdog

if __name__ == "__main__":

    def callback():
        print("something changed!")

    PyWatchdog().monitor(["README.md", "./src"]) # Monitor README.md and src

    PyWatchdog().subscribe(callback) # Do something when something happens

    PyWatchdog().watch() # Start watching
```

__Example2:__

```python
from PyWatchdog import PyWatchdog

def callback():
    print("something changed!")

def callback2():
    print("something2 changed!")

def callback3():
    print("something3 changed!")

PyWatchdog().monitor(["README.md", "./src"]) # Monitor README.md and src

PyWatchdog().subscribe(callback) # Do something when something happens
PyWatchdog().subscribe(callback2) # Do something2 when something happens
PyWatchdog().subscribe(callback3) # Do something3 when something happens

PyWatchdog().watch() # Start watching

sleep(3)
PyWatchdog().unmonitor(["README.md"]) # Stop monitoring README.md
PyWatchdog().unsubscribe(callback3) # Remove callback3

sleep(3)
PyWatchdog().stop() # Stop watching
```

### API Reference

#### For you

`subscribe`

Register a callback to be called on a file change

`unsubscribe`

Unregister a callback to be called on a file change

`monitor`

Add the path to the watchlist. Can be used while already watching. Can be called
multiple times to keep adding paths to watch. If the path is a duplicated it
will only match one.

For example:

```python
# This will only monitor is once
monitor(["./src"])
monitor(["./src"])
monitor(["./src"])
monitor(["./src"])
```

`unmonitor`

Removes a path from the watchlist. Can be used while already watching. Can be
called multiple times.

`watch`

Start watching for changes, default poll-rate is 1sec.

To change it:

```python
watch(poll=5)
```

`stop`

Stop watching for changes



#### Internal

`dispatch`

Dispatch an event. The default event name is "file_change".
Can be passed *args and **kwargs.

__other__

- `_hash` generates an MD5 hash for a given string.
- `_cache_hash` hashes a file name and stores that in the cache along with the
  last modified time 
- `_scan_dirs` starts scanning directories in the `__dirs__` list


## CLI

To use the CLI clone the repo and then run the `main.py` file in 
`src/PyWatchdog/main.py`.

```
usage: Watchdog [-h] [--poll POLL] [--paths PATHS] [--command COMMAND]
                [--callbacks CALLBACKS]

Watch for file changes

options:
  -h, --help            show this help message and exit
  --poll POLL           Set the polling rate
  --paths PATHS         List of paths
  --command COMMAND     A single command to run
  --callbacks CALLBACKS
                        Callback scripts
```

Paths should be a comma seperated string. `"path1,src/path2,../../path3"`

Callbacks are script files. Should be a commad seperated string.
`"script1.sh,script2.sh"`

__Example__

```
(~🐧):python src/PyWatchdog/main.py --command "echo Hello world" --paths "../,."
```
