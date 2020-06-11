# Tutorial 

With `lemma9.py`, we provide a rudimentary command line interface for checking and inference of inductive invariants. 
Here, we will give a brief introduction how to use and what to expect from it.
We assume that you installed the required packages and checked out the repository as described in the README.

## Command Line Interface

We assume all commands to be executed on the top folder of this repository.

To run the tests on all the benchmarks and reproduce the results of the paper,
you can run

```bash
pytest -s tests/test_Timing.py
```

The tool can be run on individual models using the `lemma9.py` script which offers a convenient CLI:

```bash
python lemma9.py [-h] path_to_model (-c | -i #iterations)
```
where the option `-h` displays a help page, 
`-c` invokes the check for inductivity of a provided candidate invariant, and
`-i` attempts to infer an invariant with `#iterations` (15 was used for the benchmarks) iterations.

## Protocol Models

The input format is a text file including 4 sections:

```
// Section 1: Global names
#global a b c...;

// Section 2: Process definitions
P1[x,..,y] := TERM;
 ⋮
Pn[x,..,y] := TERM;

// Section 3: Limit definitions
L1 = LIMIT;
 ⋮
Ln = LIMIT;

// Section 4: Initial limit
LIMIT
```

### Section 1: Global names

First, there is a declaration of which names are in the global scope.
This is optional and ensures that typos do not introduce unintentional globally free names; disallowing global names altogether would require tedious inclusion of the global scope in all the process definition variables.

### Section 2: Process definitions

Second, there is a sequence of process definitions.
The body of each definition is a term in an ASCII representation of the variant of π-calculus presented in the paper.
Input prefixes are written `in(x,y... : PATTERN ).TERM`, where `x,y...` is the list of pattern matching variables, and `PATTERN` is a message.
Messages, `M`, `N`, can be single names, pairs `(M,N)`, or encryptions `{M}_N`.
An internal "τ" transition is represented by `in()`.
Pattern matching variables can be optionally annotated with size constraints `(x:size 1)` in the input prefix containing them, e.g. `in( y,(x:size 1) : {(x,y)}_k )`.
Output is asynchronous and represented by a process `<M>`.
The term `STOP` is the terminated process.
Restrictions are written `new x.TERM`.
Terms can be composed in parallel with `||`, or in a choice with `+`.
Terms can be grouped together with round parenthesis.
Each process identifier can be defined only once.
The identifiers `Secret` and `Leak` have built-in definitions.

### Section 3: Limit definitions

Third, there is a sequence of limit definitions `L = LIMIT`.
This section is optional.
Here `L` is a limit identifier (i.e. a meta-variable denoting the limit).
Limits are terms extended with expressions of the form `LIM^w` (here `w` is a poor's man omega, not the name `w`) which denote an arbitrary number of parallel instantiations of the limit `LIM`.
Each limit identifier can be used in defining limits in subsequent definitions (so cyclic definitions are not allowed).

### Section 4: Initial limit

Finally, there is a limit defining the set of initial configurations.
This can be a process term, in which case it designates a single initial configuration.
This limit expression can use limit identifiers defined in the previous section.



You can find many example models in the `benchmarks` folder.
The formal grammar for the input format can be found in `parser/Pi.g4`.


## Methodology

The tool can be run in two modes: **check** and **inference**.

In **check** mode, the tool will assume the initial limit is presumed to be inductive (and thus an over-approximation of the reachable configurations).
The tool will check whether this is the case.
In case this is not true, the tool produces a list of transitions that start from a process in the limit and take you to a process outside the limit (i.e. counterexamples of inductivity).


In **inference** mode, the tool will start from the initial limit and run a widening-based inference for an inductive limit that includes the initial one.

The intended use of the tool is as follows.
One first writes the process definitions corresponding to the protocol of interest.
Here's an example `model-widen.pi`:

```
#global a b kab;

A1[x, y, kxy]        := in().(new nx.(<x> || <{nx}_kxy> || A2[x, y, kxy, nx]));
A2[x, y, kxy, nx]    := in(k : {(nx, (k, y))}_kxy).(<{nx}_k>);
B1[x, y, kxy]        := in((nx : size 1) : {nx}_kxy).(new k.(<{(nx, (k, y))}_kxy> || B2[x, y, kxy, nx, k]));
B2[x, y, kxy, nx, k] := in({nx}_k).(Secret[k]);

<a> || B1[a, b, kab] || A1[a, b, kab]
```

The initial configuration `<a> || B1[a, b, kab] || A1[a, b, kab]` is a single process.
If we run the tool in check mode with:

```
python lemma9.py model-widen.pi -c
```

the tool will as expected complain: the initial term is not an inductive invariant.

We then proceed to run the tool in inference mode:

```
python lemma9.py model-widen.pi -i 5
```

We call the file with a `-widen` suffix to suggest that this file is meant to be fed to the inference mode.
The tool would in this case succeed printing an inductive limit:

```
L2 = new k.( <{(nx, (k, b))}_kab> || <{nx}_k> || B2[a, b, kab, nx, k] || Secret[k]^w );
L1 = new nx.( <{nx}_kab> || A2[a, b, kab, nx] || L2^w );

( <a> || A1[a, b, kab] || B1[a, b, kab] || L1^w )
```

we can then double-check this is indeed inductive by creating a second file `model-invariant.pi` with the limit substituted for the initial term:

```
#global a b kab;

A1[x, y, kxy]        := in().(new nx.(<x> || <{nx}_kxy> || A2[x, y, kxy, nx]));
A2[x, y, kxy, nx]    := in(k : {(nx, (k, y))}_kxy).(<{nx}_k>);
B1[x, y, kxy]        := in((nx : size 1) : {nx}_kxy).(new k.(<{(nx, (k, y))}_kxy> || B2[x, y, kxy, nx, k]));
B2[x, y, kxy, nx, k] := in({nx}_k).(Secret[k]);

L2 = new k.( <{(nx, (k, b))}_kab> || <{nx}_k> || Secret[k]^w || B2[a, b, kab, nx, k] );
L1 = new nx.( <{nx}_kab> || A2[a, b, kab, nx] || L2^w);

<a> || B1[a, b, kab] || A1[a, b, kab] || L1^w
```

We used the `-invariant` suffix in the filename to indicate that it should be fed to the checker, which should succeed.
Now if we run

```
python lemma9.py model-invariant.pi -c
```

the tool will indeed confirm the limit is inductive.

Sometimes the inference is inconclusive or runs for too long.
In such cases it may be useful to direct the tool with some manual interaction.
In a typical scenario, the inference mode runs for the indicated number of iterations but could not converge to an inductive limit.
The tool would in that case output the current limit candidate and a list of transitions witnessing it is not inductive.
Alternatively, one might have worked out a candidate limit by hand and run the check mode on it discovering it is not inductive.

For illustration, imagine we manually wrote the candidate invariant above,
with the omission of the replication `^w` of `Secret[k]` in `L2`:

```
L2 = new k.( <{(nx, (k, b))}_kab> || <{nx}_k> || B2[a, b, kab, nx, k] || Secret[k] );
L1 = new nx.( <{nx}_kab> || A2[a, b, kab, nx] || L2^w );

( <a> || A1[a, b, kab] || B1[a, b, kab] || L1^w )
```

The tool in check mode would report counterexamples for inductivity including the following:

```
Process Call B2[a0, b2, kab1, nx8, k7]
has the following continuation ( Secret[k7] )
which does not seem to be included in this invariant: 
[...]
```

The names are renamed to ensure uniqueness across unfoldings.
Indeed in this example the `B2` process in `L2` can take a step by inputting `{nx}_k` and produce a second copy of `Secret`; if we modified `L2` to just include two copies

```
L2 = new k.( <{(nx, (k, b))}_kab> || <{nx}_k> || B2[a, b, kab, nx, k] || Secret[k] || Secret[k] );
```

the same problem would occur: `B2` can spawn a third copy of `Secret`.
The right fix is thus to generalise the fix to

```
L2 = new k.( <{(nx, (k, b))}_kab> || <{nx}_k> || B2[a, b, kab, nx, k] || Secret[k]^w );
```

which is now inductive, as the tool would confirm.
This kind of "invariant repair and generalisation" is the intuition behind the widening applied by inference mode.

In general one would want to exploit the inference as much as possible;
if the widening takes too many iterations or does not seem to converge,
one would examine the current candidate and the counterexamples, provide a generalised candidate and run the inference from there.
If the new limit is inductive, or could be repaired by inference to be inductive we are done; otherwise we can repeat the process and try again.

Although widenings that are guaranteed to terminate exist, their complexity is very high. We found that, for a prototype at least, the interactive approach strikes a good balance of performance and precision.



