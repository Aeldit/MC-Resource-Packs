#!/bin/env python3


import glob
import json
import sys
from os import environ, listdir, remove, walk
from os.path import isfile, join
from zipfile import ZIP_DEFLATED, ZipFile

import requests


def add_files_to_zip_rec(root_dir: str, zip_file: ZipFile) -> None:
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
            zip_file.write(join(root, file))
    return None


def publish(
    mc_version: str,
    version: str,
    project_name: str,
    project_id: str,
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
                        "name": f"[{mc_version}] {project_name} {version}",
                        "version_number": f"{version}+{mc_version}",
                        "changelog": changelog,
                        "dependencies": [
                            {
                                "project_id": "1IjD5062",  # Continuity
                                "dependency_type": "required",
                            }
                        ],
                        "game_versions": versions_range,
                        "version_type": "release",
                        "loaders": ["minecraft"],
                        "featured": True,
                        "project_id": project_id,
                        "file_parts": [file],
                    }
                )
            },
            files={file: open(file, "rb")},
        ).text
    )
    return None


def main(
    project_dir: str,
    project_id: str,
    project_name: str,
    version: str,
    changelog: str,
) -> None:
    # Remove previously generated Zip files
    for zip_file in glob.glob(f"{project_dir}/{project_name}*.zip"):
        remove(zip_file)

    files = []
    for mc_version in sorted(
        file
        for file in listdir(".")
        if isfile(file)
        and file.startswith("pack_1.")
        and file.endswith(".mcmeta")
    ):
        mcmeta_file = mc_version
        mc_version = mc_version.removeprefix("pack_").removesuffix(".mcmeta")

        file_name = f"{project_name} {version}+{mc_version}.zip"

        with ZipFile(file_name, "w", ZIP_DEFLATED) as zip_file:
            zip_file.write("CREDITS.txt")
            zip_file.write("../LICENSE")
            zip_file.write("pack.png")
            zip_file.write(mcmeta_file, "pack.mcmeta")
            add_files_to_zip_rec("assets", zip_file)

            files.append((mc_version, version, file_name))

    ranges = {
        "1.17.x": ["1.17", "1.17.1"],
        "1.18.x": ["1.18", "1.18.1", "1.18.2"],
        "1.20.x-1.21.x": [
            "1.20",
            "1.20.1",
            "1.20.2",
            "1.20.3",
            "1.20.4",
            "1.20.5",
            "1.20.6",
            "1.21",
            "1.21.1",
            "1.21.2",
            "1.21.3",
            "1.21.4",
            "1.21.5",
        ],
    }
    for mc_version, version, file_name in files:
        publish(
            mc_version,
            version,
            project_name,
            project_id,
            file_name,
            changelog,
            ranges[mc_version] if mc_version in ranges.keys() else mc_version,
        )
    return None


if __name__ == "__main__":
    args = sys.argv
    if len(args) != 4:
        print("Version not specified; Aborting")
        exit(1)

    project_dir = (
        "CTM_OF_Fabric"
        if args[1] == "ctm"
        else "CTM_Faithful"
        if args[1] == "ctmf"
        else "CTM_Create"
    )
    project_id = (
        "uJt1qseH"
        if args[1] == "ctm"
        else "qtbeFoLR"
        if args[1] == "ctmf"
        else "3RaBwrJ0"
    )
    project_name = (
        "CTM OF-Fabric"
        if args[1] == "ctm"
        else "CTM Faithful"
        if args[1] == "ctmf"
        else "CTM Create"
    )
    version = args[2]

    main(project_dir, project_id, project_name, version, args[3])
