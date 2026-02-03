# tikzpics

Python interface to generate (readable) Tikz figures.

# Install

Create and activate python environment, then install `tikzpics` with

```
pip install tikzpics
```

# Examples

## Generate tikz-figures with Python API

```python
fig = TikzFigure()

n1 = fig.add_node(0, 0, shape="circle", color="white", fill="blue", content="Hello!")
n2 = fig.add_node(5, 0, shape="circle", color="white", fill="red", content="Hi!")

fig.draw([n1, n2], options=["->", "line width=2"], color="gray")

fig.show()
print(fig.generate_tikz())
```

## IPython Magic Commands

tikzpics includes IPython magic commands for compiling TikZ figures directly in Jupyter notebooks!

Load the extension:
```python
%load_ext tikzpics.ipython
```

Then use the `%%tikz` cell magic:
```python
%%tikz
\begin{tikzpicture}
\draw[thick, blue] (0,0) circle (2cm);
\node at (0,0) {Hello TikZ!};
\end{tikzpicture}
```

See [tutorials/tutorial_07_ipython_magic.ipynb](tutorials/tutorial_07_ipython_magic.ipynb) for more examples!
