import re
from os import mkdir
from os.path import join, dirname, abspath, basename, exists
from glob import glob
from base64 import b64decode

from yaml import load, dump
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

BOOKS = join(dirname(abspath(__file__)), "books")
IGNORE = ["_template.yaml"]
TARGET = join(dirname(abspath(__file__)), "source")


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


def create(context):
    if context["schema"] == 1:
        handle_schema_1(context)


def main():
    generated = {}
    for item in glob(f"{BOOKS}/*.yaml"):
        if basename(item) in IGNORE:
            continue
        with open(join(BOOKS, item)) as file:
            data = file.read()
        schema = load(data, Loader=Loader)
        create(schema)
        generated[schema["id"]] = schema["title"]["name"]

    with open(join(TARGET, "global-toc.rst"), "w") as file:
        file.write(".. toctree::\n")
        file.write("   :maxdepth: 2\n")
        file.write("   :hidden:\n")
        file.write("   :caption: Books:\n\n")
        for item in sorted(generated, key=lambda item: generated[item]):
            file.write(f"   {item}\n")


if __name__ == "__main__":
    main()
