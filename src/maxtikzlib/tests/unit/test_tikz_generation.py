import pytest

from maxtikzlib.figure import TikzFigure


def test_tikz_equivalence():

    tikz = TikzFigure()

    path_actions = ["draw", "rounded corners", "line width=3"]

    # M
    nodes = [[0, 0], [0, 3], [1, 2], [2, 3], [2, 0]]
    for i, node_data in enumerate(nodes):
        tikz.add_node(
            node_data[0],
            node_data[1],
            f"M{i}",
            layer=0,
            color="red",
            content=f"Node {i}",
        )
    tikz.add_path(
        [f"M{i}" for i in range(len(nodes))],
        path_actions=path_actions,
        layer=1,
    )
    t1 = tikz.generate_tikz()

    # Create a new TikzFigure instance based on the generated tikz code
    tikz_2 = TikzFigure(tikz_code=tikz.generate_tikz())
    t2 = tikz_2.generate_tikz()

    # Check that generated code is equivalant
    assert t1 == t2, "Generated tikz code not the same as original"


def test_logo_equivalence():

    tikz = TikzFigure()

    path_actions = ["draw", "rounded corners", "line width=3"]

    # M
    nodes = [[0, 0], [0, 10], [1, 2], [2, 3], [2, 0]]
    for i, node_data in enumerate(nodes):
        tikz.add_node(
            node_data[0],
            node_data[1],
            f"M{i}",
            layer=0,
            color="red",
            content=f"Node {i}",
        )
    tikz.add_path(
        [f"M{i}" for i in range(len(nodes))],
        path_actions=path_actions,
        layer=1,
    )
    t1 = tikz.generate_tikz()

    # Create a new TikzFigure instance based on the generated tikz code
    tikz_2 = TikzFigure(tikz_code=tikz.generate_tikz())
    t2 = tikz_2.generate_tikz()

    # Check that generated code is equivalant
    assert t1 == t2, "Generated tikz code not the same as original"


# Function to manually call all parameterized tests with their first parameter
def call_all_tests():
    # Gather all test functions in the current file
    for name, func in globals().items():
        if callable(func) and name.startswith("test_"):
            # Check if the function has pytest parametrize markers
            parametrize_marker = getattr(func, "pytestmark", None)
            if parametrize_marker:
                for mark in parametrize_marker:
                    if mark.name == "parametrize":
                        # Extract parameter names and values
                        param_names, param_values = mark.args
                        if isinstance(param_names, str):
                            param_names = [param_names]  # Single parameter case
                        # Iterate over each parameter combination
                        for params in param_values:
                            if not isinstance(params, tuple):
                                params = (params,)  # Ensure tuple for single parameter
                            # Create a mapping of parameter names to values
                            kwargs = dict(zip(param_names, params))
                            print(f"Calling {name} with {kwargs}")
                            func(**kwargs)
            else:
                print(f"Calling {name} without args")
                func()


if __name__ == "__main__":
    call_all_tests()
    print("Passed all tests")
