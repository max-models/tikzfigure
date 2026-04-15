# Tutorial node path chaining example design

## Problem

The node path chaining feature is documented in the README, but the tutorials do
not yet show the fluent `A.to(B).to(C, options=[...])` authoring style in the
main paths guide. Readers learning paths from the tutorials should be able to
discover the new syntax where path construction and per-segment styling are
already explained.

## Goals

- Add one tutorial example for fluent node path chaining.
- Place it where it naturally extends the existing path tutorial.
- Show that `.to(..., options=...)` applies segment-local styling to a single
  hop while `fig.draw(...)` still owns path-wide styling.
- Keep the example concise and beginner-friendly.

## Non-goals

- Creating a new tutorial file.
- Adding a long comparison between chaining and manual `segment_options`.
- Expanding the feature beyond the existing node-only chaining API.
- Changing any library behavior.

## Recommended approach

Add a short subsection to `tutorials/tutorial_03_paths.qmd` immediately after
the per-segment styling examples. The subsection should introduce the chaining
syntax with three named nodes and a single `fig.draw(...)` call built from
`A.to(B).to(C, options=[...])`.

This placement keeps the new example close to the material it builds on:
readers first learn that individual path segments can be styled, then see the
more fluent way to express the same idea for node-to-node paths.

## Tutorial content

The new subsection should:

- use three existing-style named nodes created with `fig.add_node(...)`
- show one plain hop and one styled hop
- keep the path-wide arrow and stroke options on `fig.draw(...)`
- apply a simple segment option only to the second hop, such as
  `options=["bend left"]`
- end with `fig.show()` like the surrounding examples

The example should be visually simple and should not introduce extra concepts
such as custom inline segment nodes, comparison blocks, or multi-paragraph API
discussion.

## Narrative

The explanatory text should make one point clearly: chaining is a convenience
API over the same per-segment path machinery already introduced above. A short
sentence is enough, for example that options passed to `.to(...)` affect only
that connector.

## Compatibility

- The tutorial remains in `tutorial_03_paths.qmd`.
- Existing examples in the file remain unchanged unless a nearby sentence needs
  a minor wording tweak for flow.
- No code, API, or rendering semantics change.

## Validation

- The example should be syntactically consistent with the implemented
  `Node.to(...).to(...)` API.
- The prose should align with the existing behavior that segment-specific
  options are already supported by `TikzPath`.
- Because this is a documentation change, normal repository verification is only
  needed once implementation begins.
