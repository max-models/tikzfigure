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
          label: "Tutorials",
          autogenerate: { directory: "tutorials" },
        },
        { label: "API Reference", slug: "api" },
      ],
    }),
  ],
});
