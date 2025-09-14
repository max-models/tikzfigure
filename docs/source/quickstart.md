# Quickstart

Clone the repo

```
git clone ...
```

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

Run the code with

```
template-python
```

# Build docs

```
make html
cd ../
open docs/_build/html/index.html
```

```{toctree}
:maxdepth: 1