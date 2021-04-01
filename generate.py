import re
import json

from os import mkdir, symlink
from os.path import join, dirname, abspath, basename, exists, relpath
from glob import glob
from base64 import b64decode

from yaml import load, dump
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

FOLDER = dirname(abspath(__file__))
BOOKS = join(FOLDER, "books")
IGNORE = ["_template.yaml"]
TARGET = join(FOLDER, "source")
API_TARGET = join(FOLDER, "api")
API_TARGET_ID = join(API_TARGET, "book")
API_TARGET_ISBN13 = join(API_TARGET, "isbn13")
API_TARGET_ISBN10 = join(API_TARGET, "isbn10")


def tree(context, title="", multiple=False, indent=0):
    text = ""

    if title:
        text += f"{title.title()}\n"
        text += f"{'-' * len(title)}\n\n"

    if isinstance(context, dict):
        for idx, item in enumerate(context.items()):
            key, val = item
            key = re.sub("([a-z])([0-9A-Z])", "\g<1> \g<2>", key)
            key = key.lower().capitalize()

            if isinstance(val, (str, int, float)):
                if multiple:
                    if idx == 0:
                        text += f"{' ' * indent * 2}+ | **{key}:** {val}\n"
                    else:
                        text += f"{' ' * indent * 2}  | **{key}:** {val}\n"
                else:
                    text += f"{' ' * indent * 2}+ **{key}:** {val}\n"
            else:
                text += "\n"
                text += tree(val, title=key, indent=0)

    elif isinstance(context, list):
        for item in context:
            if isinstance(item, (str, int, float)):
                text += f"{' ' * indent * 2}+ {item}\n"
            else:
                text += tree(item, indent=indent + 1, multiple=True)
    return text


def image(context):
    text = ""
    if not context.get("image", {}).get("content"):
        return text

    name = context["id"]
    static = join(TARGET, "_static")
    if not exists(static):
        mkdir(static)

    mime = context["image"].get("mime", "image/png").split("/")[-1]
    with open(join(static, f"{name}.{mime}"), "wb") as file:
        file.write(b64decode(context["image"]["content"].encode()))

    text += f".. image:: _static/{name}.{mime}\n\n"
    return text


def handle_schema_1(context):
    with open(join(TARGET, f"{context['id']}.rst"), "w") as file:
        author = context["author"]["name"]
        title = context["title"]["name"]
        header = f"{title} ({author})"
        file.write(f"{header}\n")
        file.write("=" * len(header) + "\n\n")
        file.write(image(context))
        file.write(tree(context["properties"]))
        file.write("\n")
        file.write("Contributed by\n")
        file.write("--------------\n")
        file.write(tree(context["contributor"]))


def apify_schema_1(context):
    main_file = join(API_TARGET_ID, context["id"])
    if exists(main_file):
        print(f"Collision between IDs: {main_file!r}")
        return

    with open(main_file, "w") as file:
        json.dump(context, file, indent=4)
    props = context["properties"]

    if "isbn13" in props:
        dest = props["isbn13"]
        if dest != "9780000000000":
            symlink(
                relpath(main_file, start=API_TARGET_ISBN13),
                join(API_TARGET_ISBN13, dest)
            )

    if "isbn10" in props:
        dest = props["isbn10"]
        if dest != "0000000000":
            symlink(
                relpath(main_file, start=API_TARGET_ISBN10),
                join(API_TARGET_ISBN10, dest)
            )


def create(context):
    if context["schema"] == 1:
        handle_schema_1(context)


def apify(context):
    if context["schema"] == 1:
        apify_schema_1(context)


def global_toc(generated):
    with open(join(TARGET, "global-toc.rst"), "w") as file:
        file.write(".. toctree::\n")
        file.write("   :maxdepth: 2\n")
        file.write("   :hidden:\n")
        file.write("   :caption: Books:\n\n")
        for item in sorted(generated, key=lambda item: generated[item]):
            file.write(f"   {item}\n")


def api_index():
    with open(join(API_TARGET, "index.txt"), "w") as file:
        file.write("Bibliography Space API\n")
        file.write("======================\n\n")
        file.write("* GET /book/<uuid>\n")
        file.write("* GET /isbn13/<isbn13>\n")
        file.write("* GET /isbn10/<isbn10>\n")


def main():
    for fol in API_TARGET, API_TARGET_ID, API_TARGET_ISBN13, API_TARGET_ISBN10:
        if exists(fol):
            continue
        mkdir(fol)

    generated = {}
    for item in glob(f"{BOOKS}/*.yaml"):
        if basename(item) in IGNORE:
            continue
        with open(join(BOOKS, item)) as file:
            data = file.read()
        schema = load(data, Loader=Loader)
        create(schema)
        apify(schema)
        generated[schema["id"]] = schema["title"]["name"]

    global_toc(generated)
    api_index()


if __name__ == "__main__":
    main()
