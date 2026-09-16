# TikZ catalogue

A set of TikZ documents used to evaluate `tikzfigure`'s TikZ parser
(`TikzFigure.from_tikz_code` / `tikzfigure.parser.parse_tikz`).

Each statement in a `tikzpicture` is either **mapped** to a tikzfigure object
(`Node`, `TikzPath`, `Circle`, `Scope`, `Loop`, ...) or kept as **raw TikZ**
together with the reason. A statement is only mapped if the object renders
back to equivalent TikZ, so a parsed figure always produces the same picture.

## Report

```bash
python -m tikzfigure.parser.catalogue tikz_catalogue            # summary
python -m tikzfigure.parser.catalogue tikz_catalogue --details  # every raw statement
```

The *Unsupported constructs* table ranks what forces raw fallbacks across the
catalogue. Use it to decide what to wrap next.

## Tests

`src/tikzfigure/tests/test_tikz_catalogue.py` checks every entry:

- it parses without errors;
- parsing the generated code again gives exactly the same code;
- coverage does not drop below the entry's `min-coverage`;
- (marked `latex`) the original and the regenerated document compile with
  `pdflatex` to pixel-identical output.

## Adding an entry

1. Add `NN_short_name.tex`. Use a complete standalone document with the same
   preamble as `TikzFigure.generate_standalone()` so both versions render the
   same (see any existing entry), plus the `\usetikzlibrary` it needs.
2. Add the metadata lines at the top:

   ```latex
   % catalogue: title = What this example shows
   % catalogue: min-coverage = 0.75
   ```

   Set `min-coverage` to the coverage the report shows, rounded down. Raise
   it when parser or library support improves.
3. Run `pytest src/tikzfigure/tests/test_tikz_catalogue.py`.
