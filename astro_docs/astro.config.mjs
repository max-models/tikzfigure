// @ts-check
// The shared max-models docs setup (@max-models/starlight-theme). The site lives in astro_docs/
// rather than docs/, hence the editLink override. The tutorial pages are converted from the
// notebooks in tutorials/ by starlight-notebooks, the API page by scripts/generate_api_docs.py.
import { defineDocs } from '@max-models/starlight-theme';

export default defineDocs({
	repo: 'tikzfigure',
	title: 'tikzfigure',
	description: 'A Python library to generate readable TikZ figures.',
	nav: [
		{ label: 'Installation', link: '/installation/' },
		{ label: 'Tutorials', link: '/tutorials/tutorial-01-getting-started/', section: '/tutorials/' },
		{ label: 'API Reference', link: '/api/' },
		{ label: 'Interactive Editor', link: '/editor/' },
	],
	sidebar: [
		{ label: 'Home', slug: '' },
		{ label: 'Installation', slug: 'installation' },
		{
			label: 'Fundamentals',
			items: [
				{ label: 'Getting Started', slug: 'tutorials/tutorial-01-getting-started' },
				{ label: 'Styling', slug: 'tutorials/tutorial-02-styling' },
				{ label: 'Saving and Exporting', slug: 'tutorials/tutorial-16-saving-and-exporting' },
			],
		},
		{
			label: 'Drawing',
			items: [
				{ label: 'Paths', slug: 'tutorials/tutorial-03-paths' },
				{ label: 'TikZ Primitives', slug: 'tutorials/tutorial-04-primitives' },
				{ label: 'Layers', slug: 'tutorials/tutorial-05-layers' },
				{ label: 'Loops', slug: 'tutorials/tutorial-06-loops' },
				{ label: 'Coordinates and Midpoints', slug: 'tutorials/tutorial-07-coordinates-and-midpoints' },
			],
		},
		{
			label: '2D Plots',
			items: [
				{ label: 'Basics', slug: 'tutorials/tutorial-11-2d-plots-basics' },
				{ label: 'Styling', slug: 'tutorials/tutorial-12-2d-plots-styling' },
				{ label: 'Functions', slug: 'tutorials/tutorial-13-2d-plots-functions' },
				{ label: 'Subfigures and Grids', slug: 'tutorials/tutorial-14-subfigures' },
				{ label: 'Mixed Subfigures', slug: 'tutorials/tutorial-15-mixed-subfigures' },
			],
		},
		{
			label: 'Advanced',
			items: [
				{ label: '3D Figures', slug: 'tutorials/tutorial-08-3d-figures' },
				{ label: 'Raw TikZ', slug: 'tutorials/tutorial-09-raw-tikz' },
				{ label: 'Math Expressions', slug: 'tutorials/tutorial-10-math-expressions' },
				{ label: 'Tokamak X-Point', slug: 'tutorials/tutorial-25-parametric-tikz-plots' },
				{ label: 'Figure Configuration', slug: 'tutorials/tutorial-17-figure-configuration' },
				{ label: 'Shading and Patterns', slug: 'tutorials/tutorial-18-shading-and-patterns' },
				{ label: 'Opacity', slug: 'tutorials/tutorial-19-opacity-and-transparency' },
				{ label: 'Decorations', slug: 'tutorials/tutorial-20-decorations' },
				{ label: 'Advanced Styling', slug: 'tutorials/tutorial-21-advanced-styling' },
				{ label: 'Gantt Charts', slug: 'tutorials/tutorial-26-gantt' },
			],
		},
		{
			label: 'Showcases',
			items: [{ label: 'Calendar', slug: 'tutorials/tutorial-22-calendar' }],
		},
		{ label: 'API Reference', slug: 'api' },
		{ label: 'Interactive Editor', slug: 'editor' },
	],
	astro: {
		// the pages had the notebooks' file names before (Quarto)
		redirects: {
			'/tutorials/tutorial_01_getting_started/': '/tutorials/tutorial-01-getting-started/',
			'/tutorials/tutorial_02_styling/': '/tutorials/tutorial-02-styling/',
			'/tutorials/tutorial_03_paths/': '/tutorials/tutorial-03-paths/',
			'/tutorials/tutorial_04_primitives/': '/tutorials/tutorial-04-primitives/',
			'/tutorials/tutorial_05_layers/': '/tutorials/tutorial-05-layers/',
			'/tutorials/tutorial_06_loops/': '/tutorials/tutorial-06-loops/',
			'/tutorials/tutorial_07_coordinates_and_midpoints/': '/tutorials/tutorial-07-coordinates-and-midpoints/',
			'/tutorials/tutorial_08_3d_figures/': '/tutorials/tutorial-08-3d-figures/',
			'/tutorials/tutorial_09_raw_tikz/': '/tutorials/tutorial-09-raw-tikz/',
			'/tutorials/tutorial_10_math_expressions/': '/tutorials/tutorial-10-math-expressions/',
			'/tutorials/tutorial_11_2d_plots_basics/': '/tutorials/tutorial-11-2d-plots-basics/',
			'/tutorials/tutorial_11_jupyter_magic/': '/tutorials/tutorial-11-jupyter-magic/',
			'/tutorials/tutorial_12_2d_plots_styling/': '/tutorials/tutorial-12-2d-plots-styling/',
			'/tutorials/tutorial_13_2d_plots_functions/': '/tutorials/tutorial-13-2d-plots-functions/',
			'/tutorials/tutorial_14_subfigures/': '/tutorials/tutorial-14-subfigures/',
			'/tutorials/tutorial_15_mixed_subfigures/': '/tutorials/tutorial-15-mixed-subfigures/',
			'/tutorials/tutorial_16_images_legends_and_ticks/': '/tutorials/tutorial-16-images-legends-and-ticks/',
			'/tutorials/tutorial_16_saving_and_exporting/': '/tutorials/tutorial-16-saving-and-exporting/',
			'/tutorials/tutorial_17_figure_configuration/': '/tutorials/tutorial-17-figure-configuration/',
			'/tutorials/tutorial_18_shading_and_patterns/': '/tutorials/tutorial-18-shading-and-patterns/',
			'/tutorials/tutorial_19_opacity_and_transparency/': '/tutorials/tutorial-19-opacity-and-transparency/',
			'/tutorials/tutorial_20_decorations/': '/tutorials/tutorial-20-decorations/',
			'/tutorials/tutorial_21_advanced_styling/': '/tutorials/tutorial-21-advanced-styling/',
			'/tutorials/tutorial_22_calendar/': '/tutorials/tutorial-22-calendar/',
			'/tutorials/tutorial_23_karl_students/': '/tutorials/tutorial-23-karl-students/',
			'/tutorials/tutorial_24_spy_library/': '/tutorials/tutorial-24-spy-library/',
			'/tutorials/tutorial_25_parametric_tikz_plots/': '/tutorials/tutorial-25-parametric-tikz-plots/',
			'/tutorials/tutorial_26_gantt/': '/tutorials/tutorial-26-gantt/',
			'/tutorials/tutorial_27_parsing_tikz/': '/tutorials/tutorial-27-parsing-tikz/',
		},
	},
	starlight: {
		logo: { src: './src/assets/logo.png', replacesTitle: true },
		editLink: { baseUrl: 'https://github.com/max-models/tikzfigure/edit/devel/astro_docs/' },
	},
});
