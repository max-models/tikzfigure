// @ts-check
import { defineConfig } from "astro/config";
import starlight from "@astrojs/starlight";
import remarkMath from "remark-math";
import rehypeKatex from "rehype-katex";

// https://astro.build/config
export default defineConfig({
  site: "https://max-models.github.io/tikzfigure",
  base: "/tikzfigure",
  markdown: {
    remarkPlugins: [remarkMath],
    rehypePlugins: [rehypeKatex],
  },
  integrations: [
    starlight({
      title: "tikzfigure",
      logo: { src: "./src/assets/logo.png", replacesTitle: true },
      customCss: ["katex/dist/katex.min.css"],
      social: [
        {
          icon: "github",
          label: "GitHub",
          href: "https://github.com/max-models/tikzfigure",
        },
      ],
      sidebar: [
        { label: "Home", slug: "" },
        { label: "Installation", slug: "installation" },
        {
          label: "Fundamentals",
          items: [
            { label: "Getting Started", slug: "tutorials/tutorial_01_getting_started" },
            { label: "Styling", slug: "tutorials/tutorial_02_styling" },
            { label: "Saving and Exporting", slug: "tutorials/tutorial_16_saving_and_exporting" },
          ],
        },
        {
          label: "Drawing",
          items: [
            { label: "Paths", slug: "tutorials/tutorial_03_paths" },
            { label: "TikZ Primitives", slug: "tutorials/tutorial_04_primitives" },
            { label: "Layers", slug: "tutorials/tutorial_05_layers" },
            { label: "Loops", slug: "tutorials/tutorial_06_loops" },
            { label: "Coordinates and Midpoints", slug: "tutorials/tutorial_07_coordinates_and_midpoints" },
          ],
        },
        {
          label: "2D Plots",
          items: [
            { label: "Basics", slug: "tutorials/tutorial_11_2d_plots_basics" },
            { label: "Styling", slug: "tutorials/tutorial_12_2d_plots_styling" },
            { label: "Functions", slug: "tutorials/tutorial_13_2d_plots_functions" },
            { label: "Subfigures and Grids", slug: "tutorials/tutorial_14_subfigures" },
            { label: "Mixed Subfigures", slug: "tutorials/tutorial_15_mixed_subfigures" },
          ],
        },
        {
          label: "Advanced",
          items: [
            { label: "3D Figures", slug: "tutorials/tutorial_08_3d_figures" },
            { label: "Raw TikZ", slug: "tutorials/tutorial_09_raw_tikz" },
            { label: "Math Expressions", slug: "tutorials/tutorial_10_math_expressions" },
            { label: "Figure Configuration", slug: "tutorials/tutorial_17_figure_configuration" },
            { label: "Shading and Patterns", slug: "tutorials/tutorial_18_shading_and_patterns" },
            { label: "Opacity", slug: "tutorials/tutorial_19_opacity_and_transparency" },
            { label: "Decorations", slug: "tutorials/tutorial_20_decorations" },
            { label: "Advanced Styling", slug: "tutorials/tutorial_21_advanced_styling" },
          ],
        },
        {
          label: "Showcases",
          items: [
            { label: "Calendar", slug: "tutorials/tutorial_22_calendar" },
          ],
        },
        { label: "API Reference", slug: "api" },
        { label: "Interactive Editor", slug: "editor" },
      ],
    }),
  ],
});
