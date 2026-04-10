"""Example: Creating 2D plots with pgfplots axes."""

from tikzfigure import TikzFigure

# Create a figure
fig = TikzFigure()

# Add a 2D axis with labels and limits
ax = fig.axis2d(xlabel="X Axis", ylabel="Y Axis", xlim=(0, 10), ylim=(0, 25), grid=True)

# Add data plots
ax.add_plot([0, 2, 4, 6, 8, 10], [0, 1, 4, 9, 16, 25], label="y = x²", color="red")

ax.add_plot([0, 2, 4, 6, 8, 10], [0, 2, 4, 6, 8, 10], label="y = x", color="blue")

# Configure legend
ax.set_legend(position="north west")

# Display or save
fig.show(use_web_compilation=True)
# fig.savefig("plot.png")
