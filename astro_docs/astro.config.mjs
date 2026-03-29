// @ts-check
import { defineConfig } from "astro/config";
import starlight from "@astrojs/starlight";
import remarkMath from "remark-math";
import rehypeKatex from "rehype-katex";

// https://astro.build/config
export default defineConfig({
  site: "https://max-models.github.io/tikzpics",
  base: "/tikzpics",
  markdown: {
    remarkPlugins: [remarkMath],
    rehypePlugins: [rehypeKatex],
  },
  integrations: [
    starlight({
      title: "tikzpics",
      customCss: ["katex/dist/katex.min.css"],
      social: [
        {
          icon: "github",
          label: "GitHub",
          href: "https://github.com/max-models/tikzpics",
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
