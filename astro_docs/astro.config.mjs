// @ts-check
import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';

// https://astro.build/config
export default defineConfig({
	site: 'https://max-models.github.io/tikzpics',
	base: '/tikzpics',
	integrations: [
		starlight({
			title: 'tikzpics',
			social: [{ icon: 'github', label: 'GitHub', href: 'https://github.com/max-models/tikzpics' }],
			sidebar: [
				{ label: 'Home', slug: '' },
				{ label: 'Installation', slug: 'installation' },
				{
					label: 'Tutorials',
					autogenerate: { directory: 'tutorials' },
				},
				{ label: 'API Reference', slug: 'api' },
			],
		}),
	],
});
