import maxtikzlib.logo

fig = maxtikzlib.logo.generate_logo()
print(fig.generate_tikz())
fig.compile_pdf(filename="mtl_logo.pdf")
