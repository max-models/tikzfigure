# template-python

Template repository for python projects

Documentation: https://max-models.github.io/template-python/

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

Run the code with

```
template-python
```

# Build docs


```
# https://medium.com/@pratikdomadiya123/build-project-documentation-quickly-with-the-sphinx-python-2a9732b66594
sphinx-apidoc -o docs/ src/app/
cd docs/
make clean
make html
cd ../
open docs/_build/html/index.html
```
