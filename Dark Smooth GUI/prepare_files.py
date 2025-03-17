#!/bin/env python3

import glob
import sys
from os import listdir, remove, walk
from os.path import join, relpath
from zipfile import ZIP_DEFLATED, ZipFile


def add_files_to_zip_rec(
    root_dir: str, zip_file: ZipFile, prefix: str, arcname: str = ""
) -> None:
    """
    Recursively adds the files and directories from root_dir to zip_file

    :root_dir: The dir from which to start adding files
    :zip_file: The ZipFile object
    :prefix:   The prefix to remove
    :arcname:  The name to give to the start of the path if it is not the same
               as the one from the file
    """
    for root, _, files in walk(root_dir):
        for file in files:
            zip_file.write(
                join(root, file),
                join(
                    f"{arcname}%s"
                    % str(relpath(join(root, file))).removeprefix(prefix)
                ),
            )
    return None


def add_mods_files(mc_version: str, zip_file: ZipFile) -> None:
    for mod, mod_versions in {
        "axiom": ("1.20-1.20.1", "1.20.2-1.20.4", "1.20.5-1.21.x"),
        "ctms": (
            "1.18.x",
            "1.19.x",
            "1.20-1.20.1",
            "1.20.2-1.20.4",
            "1.20.5-1.21.x",
        ),
        "emi": ("1.19.x", "1.20-1.20.1", "1.20.2-1.20.4", "1.20.5-1.21.x"),
        "entity_texture_features": (
            "1.18.x",
            "1.19.x",
            "1.20-1.20.1",
            "1.20.2-1.20.4",
        ),
        "inventorytabs": ("1.18.x", "1.19.x", "1.20-1.20.1"),
        "iris": ("1.18.x", "1.19.x", "1.20-1.20.1", "1.20.2-1.20.4"),
        "itemswapper": (
            "1.18.x",
            "1.19.x",
            "1.20-1.20.1",
            "1.20.2-1.20.4",
            "1.20.5-1.21.x",
        ),
        "modmenu": (
            "1.18.x",
            "1.19.x",
            "1.20-1.20.1",
            "1.20.2-1.20.4",
            "1.20.5-1.21.x",
        ),
        "raised": (
            "1.18.x",
            "1.19.x",
            "1.20-1.20.1",
            "1.20.2-1.20.4",
            "1.20.5-1.21.x",
        ),
    }.items():
        if mc_version in mod_versions:
            add_files_to_zip_rec(
                f"common/{mod}", zip_file, "common/", "assets/"
            )

    return None


def base_to_zip_file(mc_version: str, zip_file: ZipFile):
    zip_file.write("LICENSE.txt")
    zip_file.write("pack.png")
    zip_file.write(f"{mc_version}/pack.mcmeta", "pack.mcmeta")
    add_files_to_zip_rec(f"{mc_version}/assets", zip_file, f"{mc_version}/")
    add_mods_files(mc_version, zip_file)
    return None


def main() -> None:
    args = sys.argv
    if len(args) != 2:
        print("Version not specified; Aborting")
        exit(1)

    # Remove previously generated Zip files
    for zip_file in glob.glob("Dark Smooth GUI*.zip"):
        remove(zip_file)

    for mc_version in (dir for dir in listdir(".") if dir.startswith("1.")):
        with ZipFile(
            f"Dark Smooth GUI {args[1]}+{mc_version}.zip", "w", ZIP_DEFLATED
        ) as zip_file:
            base_to_zip_file(mc_version, zip_file)

    return None


if __name__ == "__main__":
    main()
