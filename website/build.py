import os
import shutil
from pathlib import Path
import xml
import pylode


BASEDIR = Path(".", "website")
GLOB_PATTERN = "./*/*.owl"


def get_tmp_dir():
    return Path(BASEDIR, "tmp")


def create_tmp_dir():
    tmpdir = get_tmp_dir()

    if not os.path.exists(tmpdir):
        os.mkdir(tmpdir)


def run_pylode(path):
    html = pylode.MakeDocco(
        input_data_file=str(path), outputformat="html", profile="ontdoc"
    ).document()

    out_path = f"{path}.html"
    out_path.replace(".ttl", "")
    out_path.replace(".owl", "")

    with open(out_path, "w") as html_file:
        html_file.write(html)


def process(path):
    newpath = Path(get_tmp_dir(), os.path.basename(path))
    shutil.copy(path, newpath)

    # Try processing one. If it fails, try processing as Turtle
    try:
        run_pylode(newpath)
    except xml.sax._exceptions.SAXParseException:
        renamedpath = Path(get_tmp_dir(), os.path.basename(newpath).replace(".owl", ".ttl"))
        os.rename(newpath, renamedpath)
        run_pylode(renamedpath)


def copy_html():
    for path in Path(get_tmp_dir()).glob("*.html"):
        os.rename(path, Path(BASEDIR, os.path.basename(path)))

def main():
    create_tmp_dir()

    for path in Path(".").glob(GLOB_PATTERN):
        print(path)

        process(path)
        copy_html()


if __name__ == "__main__":
    main()
