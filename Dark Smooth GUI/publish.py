#!/bin/env python3

import glob
import json
import sys
from os import environ, listdir, remove, walk
from os.path import join, relpath
from zipfile import ZIP_DEFLATED, ZipFile

import requests


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
        "entity_features": (
            "1.18.x",
            "1.19.x",
            "1.20-1.20.1",
            "1.20.2-1.20.4",
            "1.20.5-1.21.x",
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


def publish(
    mc_version: str,
    version: str,
    file: str,
    changelog: str,
    versions_range: list[str],
):
    print(
        requests.post(
            "https://api.modrinth.com/v2/version",
            headers={"Authorization": environ["MODRINTH_TOKEN"]},
            data={
                "data": json.dumps(
                    {
                        "name": f"[{mc_version}] Dark Smooth GUI {version}",
                        "version_number": f"{version}+{mc_version}",
                        "changelog": changelog,
                        "dependencies": [
                            {
                                "project_id": "N6n5dqoA",  # Axiom
                                "dependency_type": "optional",
                            },
                            {
                                "project_id": "6OpnBWtt",  # CTMS
                                "dependency_type": "optional",
                            },
                            {
                                "project_id": "fRiHVvU7",  # EMI
                                "dependency_type": "optional",
                            },
                            {
                                "project_id": "BVzZfTc1",  # ETF
                                "dependency_type": "optional",
                            },
                            {
                                "project_id": "VD1aynYU",  # InvetoryTabs
                                "dependency_type": "optional",
                            },
                            {
                                "project_id": "YL57xq9U",  # Iris
                                "dependency_type": "optional",
                            },
                            {
                                "project_id": "RPOSBQgq",  # ItemSwapper
                                "dependency_type": "optional",
                            },
                            {
                                "project_id": "mOgUt4GM",  # Modmenu
                                "dependency_type": "optional",
                            },
                            {
                                "project_id": "AANobbMI",  # Sodium
                                "dependency_type": "optional",
                            },
                        ],
                        "game_versions": versions_range,
                        "version_type": "release",
                        "loaders": ["minecraft"],
                        "featured": True,
                        "project_id": "3BPM3cU5",
                        "file_parts": [file],
                    }
                )
            },
            files={file: open(file, "rb")},
        ).text
    )
    return None


def main() -> None:
    args = sys.argv
    if len(args) != 2:
        print("Version not specified; Aborting")
        exit(1)

    version = args[1]

    # Remove previously generated Zip files
    for zip_file in glob.glob("Dark Smooth GUI*.zip"):
        remove(zip_file)

    files = []
    for mc_version in sorted(
        dir for dir in listdir(".") if dir.startswith("1.")
    ):
        file = f"Dark Smooth GUI {version}+{mc_version}.zip"
        with ZipFile(file, "w", ZIP_DEFLATED) as zip_file:
            base_to_zip_file(mc_version, zip_file)
            files.append((mc_version, version, file))
            print(mc_version)

    ranges = {
        "1.17.x": ["1.17", "1.17.1"],
        "1.18.x": ["1.18", "1.18.1", "1.18.2"],
        "1.19.x": ["1.19", "1.19.1", "1.19.2", "1.19.3", "1.19.4"],
        "1.20-1.20.1": ["1.20", "1.20.1"],
        "1.20.2-1.20.4": ["1.20.2", "1.20.3", "1.20.4"],
        "1.20.5-1.21.x": [
            "1.20.5",
            "1.20.6",
            "1.21",
            "1.21.1",
            "1.21.2",
            "1.21.3",
            "1.21.4",
        ],
    }
    for mc_version, version, file in files:
        publish(
            mc_version,
            version,
            file,
            "Add new Axiom GUI textures + fix some issues",
            ranges[mc_version],
        )
    return None


if __name__ == "__main__":
    main()
