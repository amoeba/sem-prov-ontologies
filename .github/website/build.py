import os
import shutil
from pathlib import Path
import xml
import pylode
from jinja2 import Template


BASEDIR = Path(".", "website")
GLOB_PATTERN = "./*/*.owl"
INDEX_TEMPLATE = Path(".", "website", "index.template")
INDEX_HTML = Path(".", "website", "index.html")

def get_tmp_dir():
    return Path(BASEDIR, "tmp")

def create_tmp_dir():
    tmpdir = get_tmp_dir()

    if not os.path.exists(tmpdir):
        os.mkdir(tmpdir)

def run_pylode(path):
    out_path = f"{path}.html"
    out_path = out_path.replace(".ttl", "")
    out_path = out_path.replace(".owl", "")

    print(f"Running PyLODE on {path}")
    html = pylode.MakeDocco(
        input_data_file=str(path), outputformat="html", profile="dataone"
    ).document()

    with open(out_path, "w") as html_file:
        html_file.write(str(html))

    return out_path

def process(path):
    print(f"Processing {path}...")

    newpath = Path(get_tmp_dir(), os.path.basename(path))
    shutil.copy(path, newpath)

    # Try processing one. If it fails, try processing as Turtle
    try:
        return run_pylode(newpath)
    except Exception:
        print("Re-processing as Turtle...")
        renamedpath = Path(get_tmp_dir(), os.path.basename(newpath).replace(".owl", ".ttl"))
        os.rename(newpath, renamedpath)

        return run_pylode(renamedpath)

def copy_all_html():
    new_paths = []

    for path in Path(get_tmp_dir()).glob("*.html"):
        print(f"Copying HTML for {path}")

        basename = os.path.basename(path)
        new_path = Path(BASEDIR, basename)
        os.rename(path, new_path)
        new_paths.append(os.path.basename(new_path))

    return new_paths

def parse_ontology(path):
    return {
        "name": path.replace(".html", ""),
        "path": path
    }

def build_index(html_files):
    ontologies = [parse_ontology(file) for file in html_files]
    output = None

    with open(INDEX_TEMPLATE, "r") as index_template:
        tmpl_str = index_template.read()
        tmpl = Template(tmpl_str)
        output = tmpl.render(ontologies=ontologies)

    with open(INDEX_HTML, "w") as index_html:
        index_html.write(str(output))


def main():
    create_tmp_dir()

    for path in Path(".").glob(GLOB_PATTERN):
        process(path)

    html_files = copy_all_html()
    build_index(html_files)

if __name__ == "__main__":
    main()
