"""Example: drawing without creating a TikzFigure.

The module-level functions operate on an implicit "current figure" that is
created the first time one of them is called, much like matplotlib.pyplot.
"""

import tikzfigure as tf

# No TikzFigure() needed: the first call creates the current figure.
a = tf.node(0, 0, content="A", shape="circle", fill="cyan!40")
b = tf.node(3, 0, content="B", shape="circle", fill="cyan!40")
c = tf.node(0, -2, content="C", shape="circle", fill="cyan!40")

tf.draw([a, b], arrows="->")
tf.draw([b, c], arrows="->")

print(tf.generate_tikz())

# Display or save
tf.show()
# tf.savefig("pyplot_style.png")

# tf.gcf() hands back the figure if you need the object-oriented API,
# and tf.figure() starts a fresh one.
fig = tf.gcf()
print(f"{len(fig.layers.get_nodes())} nodes on the current figure")
