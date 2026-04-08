import os
import shutil
import subprocess

# Path to your Python package/module
PACKAGE = "tikzfigure"
# Output directory for generated Markdown
OUTPUT_DIR = "src/content/docs/api_md"


def main():
    # Ensure output directory exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    # Run pdoc to generate Markdown
    subprocess.run(
        ["pdoc", "--output-dir", OUTPUT_DIR, "--format", "markdown", PACKAGE],
        check=True,
    )
    # Move/rename the main file to api.md for Astro
    src = os.path.join(OUTPUT_DIR, f"{PACKAGE}.md")
    dst = os.path.join("src/content/docs", "api.md")
    shutil.move(src, dst)
    # Optionally, clean up the output dir if empty
    if not os.listdir(OUTPUT_DIR):
        os.rmdir(OUTPUT_DIR)
    print(f"API docs generated at {dst}")


if __name__ == "__main__":
    main()
