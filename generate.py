import re
import json

from os import mkdir, symlink
from os.path import join, dirname, abspath, basename, exists, relpath
from glob import glob
from base64 import b64decode
from collections import defaultdict

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
API_TARGET_BOOK = join(API_TARGET, "book")
API_TARGET_AUTHOR = join(API_TARGET, "author")
API_TARGET_CHECK = join(API_TARGET, "check-id")
API_TARGET_ISBN13 = join(API_TARGET, "isbn13")
API_TARGET_ISBN10 = join(API_TARGET, "isbn10")
API_DIRS = [
    API_TARGET, API_TARGET_BOOK, API_TARGET_AUTHOR,
    API_TARGET_ISBN13, API_TARGET_ISBN10,
    API_TARGET_CHECK
]


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


def book_schema_1(context):
    with open(join(TARGET, f"{context['id']}.rst"), "w") as file:
        author = context["author"]["name"]
        title = context["title"]["name"]
        file.write(f"{title}\n")
        file.write("=" * len(title) + "\n\n")
        file.write(image(context))
        file.write(tree(context["properties"]))
        file.write("\n")
        file.write("Contributed by\n")
        file.write("--------------\n")
        file.write(tree(context["contributor"]))


def apify_book_schema_1(context):
    main_file = join(API_TARGET_BOOK, context["id"])
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


def create_book(context):
    if context["schema"] == 1:
        book_schema_1(context)


def apify_book(context):
    if context["schema"] == 1:
        apify_book_schema_1(context)


def create_author(aid, children):
    dest = join(TARGET, f"{aid}.rst")
    if exists(dest):
        raise Exception(f"Collision between IDs: {dest!r}")

    author = children[0]["author"]
    assert aid == author["id"], (aid, author)

    bullets = "\n".join([
        f"*   `{item['title']['name']} <{item['id']}>`_"
        for item in sorted(children, key=lambda item: item["title"]["name"])
    ])
    with open(dest, "w") as file:
        name = author["name"]
        file.write(f"{name}\n")
        file.write("=" * len(name) + "\n\n")
        file.write(bullets)


def apify_author(aid, children):
    main_file = join(API_TARGET_AUTHOR, aid)
    if exists(main_file):
        raise Exception(f"Collision between IDs: {dest!r}")

    response = children[0]["author"]
    response["books"] = [item["id"] for item in children]

    with open(main_file, "w") as file:
        json.dump(response, file, indent=4)


def apify_author_full(aid, children):
    main_file = join(API_TARGET_AUTHOR, aid)
    if exists(main_file):
        raise Exception(f"Collision between IDs: {dest!r}")

    response = children[0]["author"]
    response["books"] = [item["id"] for item in children]

    with open(main_file, "w") as file:
        json.dump(response, file, indent=4)


def global_books(books):
    sorted_books = sorted(
        books,
        key=lambda item: books[item]["title"]["name"]
    )
    content = "\n".join([f"   {item}" for item in sorted_books])

    with open(join(TARGET, "global-books.rst"), "w") as file:
        file.write("Books\n")
        file.write("=====\n\n")
        file.write(".. toctree::\n")
        file.write("   :maxdepth: 1\n")
        file.write("   :titlesonly:\n\n")
        file.write(content)


def global_authors(authors):
    sorted_authors = sorted(
        authors,
        key=lambda item: authors[item][0]["author"]["name"]
    )
    content = "\n".join([f"   {aid}" for aid in sorted_authors])

    with open(join(TARGET, "global-authors.rst"), "w") as file:
        file.write("Authors\n")
        file.write("=======\n\n")
        file.write(".. toctree::\n")
        file.write("   :maxdepth: 1\n")
        file.write("   :titlesonly:\n\n")
        file.write(content)


def global_toc(generated):
    global_books(generated["books"])
    global_authors(generated["authors"])

    with open(join(TARGET, "global-toc.rst"), "w") as file:
        file.write(".. toctree::\n")
        file.write("   :maxdepth: 2\n")
        file.write("   :hidden:\n\n")
        file.write("   global-authors\n")
        file.write("   global-books\n")


def api_index():
    with open(join(API_TARGET, "index.txt"), "w") as file:
        file.write("Bibliography Space API\n")
        file.write("======================\n\n")
        file.write("API base: https://bibliography.rest\n")
        file.write("* GET /book/<uuid>\n")
        file.write("* GET /isbn13/<isbn13>\n")
        file.write("* GET /isbn10/<isbn10>\n\n")
        file.write("See also: https://bibliography.space\n")


def read_books(callbacks: list):
    output = {"books": {}, "authors": defaultdict(list)}

    for item in glob(f"{BOOKS}/*.yaml"):
        if basename(item) in IGNORE:
            continue
        with open(join(BOOKS, item)) as file:
            data = file.read()
        schema = load(data, Loader=Loader)
        for cbk in callbacks:
            cbk(schema)
        output["books"][schema["id"]] = schema
        output["authors"][schema["author"]["id"]].append(schema)
    return output


def api_check_index(generated):
    for author_id in generated["authors"]:
        symlink(
            relpath(
                join(API_TARGET_AUTHOR, author_id),
                start=API_TARGET_CHECK
            ),
            join(API_TARGET_CHECK, author_id)
        )
    for book_id in generated["books"]:
        symlink(
            relpath(
                join(API_TARGET_BOOK, book_id),
                start=API_TARGET_CHECK
            ),
            join(API_TARGET_CHECK, book_id)
        )

def main():
    [mkdir(fol) for fol in API_DIRS if not exists(fol)]

    generated = read_books(callbacks=[create_book, apify_book])

    for author, books in generated["authors"].items():
        create_author(author, books)
        apify_author(author, books)

    global_toc(generated)
    api_index()
    api_check_index(generated)


if __name__ == "__main__":
    main()
