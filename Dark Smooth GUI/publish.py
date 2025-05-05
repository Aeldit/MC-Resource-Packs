#!/bin/env python3

import glob
import json
import sys
from os import environ, listdir, remove, walk
from os.path import join, relpath
from zipfile import ZIP_DEFLATED, ZipFile

import requests
from flask import Flask

PROJECT_ID = "3BPM3cU5"


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
    zip_file.write("../LICENSE")
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
    req = requests.post(
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
                    "project_id": PROJECT_ID,
                    "file_parts": [file],
                }
            )
        },
        files={file: open(file, "rb")},
    )

    if req.status_code == 200:
        print(f"Successfully uploaded version {version}+{mc_version}")
    else:
        print(
            f"Couldn't update the version {version}+{mc_version}.\n"
            f"Error code: {req.status_code}.\n"
            f"Error response: {req.text if req is not None else {}}\n"
        )
    return None


def update_body() -> None:
    with open("README.md", "r") as rf:
        body = rf.read()
        req = requests.patch(
            f"https://api.modrinth.com/v2/project/{PROJECT_ID}",
            headers={"Authorization": environ["MODRINTH_TOKEN"]},
            json={"body": body},
        )
        if req.status_code == 204:
            print("Body synced successfully")
        else:
            print(
                "Couldn't sync the body.\n"
                f"Error code: {req.status_code}.\n"
                f"Error response: {req.text if req is not None else {}}\n"
            )
    return None


def get_existing_versions() -> list[dict]:
    return requests.get(
        f"https://api.modrinth.com/v2/project/{PROJECT_ID}/version"
    ).json()


def send_discord_announcement(changelog: str) -> None:
    try:
        resp = requests.post(
            environ["DISCORDWH"],
            data=json.dumps(
                {
                    "content": f"<@&{environ['DISCORD_ROLE_RPU']}> <@&{environ['DISCORD_ROLE_DGUI']}> A new version of Dark Smooth GUI is available on Modrinth\n\n{changelog}"
                }
            ),
            headers={"Content-Type": "application/json"},
            timeout=1.0,
        )
        # Returns an HTTPError if an error has occurred during the process (used for debugging).
        resp.raise_for_status()
    except requests.exceptions.HTTPError:
        print("An HTTP Error occurred")
        pass
    except requests.exceptions.ConnectionError:
        print("An Error Connecting to the API occurred")
        pass
    except requests.exceptions.Timeout:
        print("A Timeout Error occurred")
        pass
    except requests.exceptions.RequestException:
        print("An Unknown Error occurred")
        pass
    else:
        print(resp.status_code)
    return None


def main(version: str, changelog: str) -> None:
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
            "1.21.5",
        ],
    }
    existing_versions = tuple(
        ev["version_number"] for ev in get_existing_versions()
    )

    for mc_version, version, file in files:
        if f"{version}+{mc_version}" in existing_versions:
            print(
                f"Not uploading version {version}+{mc_version} because it is already on modrinth"
            )
            continue

        publish(mc_version, version, file, changelog, ranges[mc_version])

    update_body()
    send_discord_announcement(changelog)
    return None


if __name__ == "__main__":
    args = sys.argv
    if len(args) < 2:
        print("Version not specified; Aborting")
        exit(1)

    if "bo" in args:
        update_body()
    else:
        version = args[1]
        changelog = args[2] if len(args) == 3 else "No changelog provided"

        main(version, changelog)
