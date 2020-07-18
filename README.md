# Lemma9 #

**Verification of Cryptographic Protocols with Unbounded Sessions**

An implementation of inductive invariants checking and inference for depth-bounded protocols.

The name comes from a "Lemma 9" which was the internal name of a cornerstone component of the verification method,
now called "Absorption Lemma".

## Contacts

- Emanuele D'Osualdo (e.dosualdo@ic.ac.uk)
- Felix M. Stutz (fstutz@mpi-sws.org)

## Reproducing the results

The benchmark models can be found in `benchmarks`.

To reproduce the results on the benchmarks, first you need to install all the dependencies as explained in the next section.
Then by running `pytest -s tests/test_Timing.py` from the root directory
the solver will check each benchmark and produce a table of timings and results.

Running the tests to completion takes approximately 15 minutes on a standard laptop.
To select a subset of the benchmarks for testing, open `tests/test_Timing.py`
and comment the entries of the benchmarks you want to exclude in the main ordered dictionary, then run `pytest -s tests/test_Timing.py` from the root directory.

## How to install and run benchmarks

The program is written in **Python 2.7**.
We recommend using [`pyenv`][pyenv] and `pip` to setup the right environment and install dependencies, as detailed below.
A Dockerfile is provided and can be used to create a container running the tool with all the dependencies installed.
For details on usage of the tool, please look at the `tutorial/TUTORIAL.md` file.

### Installing with `pyenv`

```bash
# ASSUMES this repo has been cloned into "lemma9"
cd lemma9
# OPTIONAL STEPS
pyenv virtualenv lemma9 # creates a new "lemma9" virtualenv
pyenv local lemma9      # sets virtualenv for this project
pyenv activate lemma9   # activate virtualenv
# END OPTIONAL STEPS
# Install the dependencies:
pip install -r requirements.txt
# Run the tests displaying the results table:
pytest -s tests/test_Timing.py
```

### Installing with `virtualenv`

If you don't like [`pyenv`][pyenv] you can use `virtualenv` directly:

```bash
# If virtualenv is not installed:
pip install virtualenv
pip virtualenv venv # create new virtualenv in venv
source venv/bin/activate
# Install the dependencies:
pip install -r requirements.txt
# Run the tests displaying the results table:
pytest -s tests/test_Timing.py
```

### Installing globally

If you don't like `virtualenv` either, you can always install the dependencies globally and, provided there is no dependency conflict, run the tests:

```bash
pip install -r requirements.txt
pytest -s tests/test_Timing.py
```

### Using Docker

With Docker installed, you can build an image with

    docker build -t lemma9 .

from the root folder of the repo.
Then you can run the benchmarks using

    docker run lemma9

If you want to experiment with Lemma9's CLI and tutorial, run

    docker run -it --entrypoint /bin/bash lemma9

which will give you an interactive shell within the container.

[pyenv]: https://github.com/pyenv/pyenv#table-of-contents