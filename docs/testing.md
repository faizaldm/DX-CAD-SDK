# Running the tests

The suite is some 7,500 tests, too many to run one after another in a sitting:
in one process it takes over half an hour. It runs in parallel instead, with
pytest-xdist (pinned in the `dev` extra and in requirements.txt), in two passes.

## The parallel pass

```
python -m pytest -n 8 --dist loadfile -m "not serial" -q
```

`-n 8` starts eight worker processes (`-n auto` takes one per core, as CI
does); `--dist loadfile` hands each worker whole test files, so a file's
module-scoped fixtures are built once. Every worker is a sandbox of its own:
tests/conftest.py names its settings file, recovery folder, logs and window
channels from the worker's name (`PYTEST_XDIST_WORKER`, `gw0`, `gw1`, ...) and
its process id, and every test writes under its own `tmp_path`. The platform's
own settings store is an INI file in that sandbox too, so a DX-CAD window you
have open while the suite runs can neither be reached by a test nor fail the
run.

## The serial pass

```
python -m pytest -m serial -q
```

A test that touches something machine-wide is marked `@pytest.mark.serial`
and runs here, one at a time, after the parallel pass: file associations and
the Explorer thumbnail provider in the registry, the installer, anything that
reads or writes outside the test's own sandbox. A new test of that kind is
marked serial.

## Slow tests

A test that takes over 20 seconds, the robustness suite and the benchmarks
are marked `@pytest.mark.slow`. While building something, leave them out:

```
python -m pytest -n 8 --dist loadfile -m "not slow and not serial" -q
```

The full parallel pass above includes them. CI leaves them out of its linux
and macos jobs and runs them in a `slow` job of their own, so no job runs
into its time limit. `--durations=20` lists the 20
slowest tests of a run, which is how a test that should be marked slow is
found.

## Time limit

Every phase of every test, setup, call and teardown, runs under the limit
`tests/hang_guard.py` keeps: the `time_limit` setting in pyproject.toml's
pytest section, 600 seconds, which CI's linux and macos jobs lower to 300
through `PYTEST_ADDOPTS` in ci.yml, so a hung test fails with its name in the
summary rather than outliving the job. A test that needs longer is marked
`@pytest.mark.time_limit(seconds)`, and `-o time_limit=30` sets a run's.

## Under load

A test waits for what it tests, never for the clock: every wait on a signal
or a condition has a ceiling of 30 s or more, and `tests/test_steady_waits.py`
fails on one that is shorter. To run the suite as a loaded machine would, with
spinning processes beside it:

```
python tests/busy.py 4 -- python -m pytest -n 8 --dist loadfile -m "not slow and not serial" -q
```

## CI's two Linux halves

The linux job is a matrix of two halves. Each runs every other test file,
in name order, through `tests/halves.py`, so no file runs twice and none is
left out; a worker then grows over half as many files, which is what lost
the runner once. The script samples the test processes' memory while pytest
runs and writes the peak, with the ten slowest tests, into the job's
summary, which is where `-n` for that job is read from:

```
python tests/halves.py --half 1 --of 2 -- python -m pytest -n 3 --dist loadfile -m "not slow and not serial" -q --durations=10
```

`--list` prints a half's files and stops.

## One file

```
python -m pytest tests/test_kernel.py
```

or, for a few files at once in parallel,
`python -m pytest -n 8 --dist loadfile tests/test_kernel.py tests/test_sketch.py`.
A serial test in a file run like this still runs; the markers only choose
when a whole-suite pass is asked for with `-m`.
