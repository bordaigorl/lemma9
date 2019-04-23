# Lemma9 #

**Verification of Cryptographic Protocols with Unbounded Sessions**

An implementation of inductive invariants checking and inference for depth-bounded protocols.

The name comes from a "Lemma 9" which was the internal name of a cornerstone component of the verification method,
now called "Absorption Lemma".

## Contacts

- Emanuele D'Osualdo (e.dosualdo@ic.ac.uk)
- Felix M. Stutz (fstutz@mpi-inf.mpg.de)


**How to install**
We recommend the following steps using *pip* for *Python 2.7* after cloning and entering the repository:

* `# pip install virtualenv` to install the tool to build a virtual environment
* `# virtualenv venv` to build an environment called venv
* `# source venv/bin/activate` to activate it
* `# pip install enum pytest antlr4-python2-runtime z3-solver` to install the required packages
* `# cd /tests` and `# pytest test_Timing.py`



