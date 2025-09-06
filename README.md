# maxtikzlib

Python interface to generate (readable) Tikz figures.

Documentation: https://max-models.github.io/maxtikzlib/

# Install

Create and activate python environment

```
python -m venv env
source env/bin/activate
pip install --upgrade pip
```

Install the code and requirements with pip

```
pip install -e .
```

To install optional dependencies:

```
pip install -e ".[test]" # For pytest
pip install -e ".[dev]" For developers
```

# Build docs


```
# https://medium.com/@pratikdomadiya123/build-project-documentation-quickly-with-the-sphinx-python-2a9732b66594
sphinx-apidoc -o docs/ src/app/
cd docs/
make clean
make html
cd ../
open docs/build/html/index.html
```
