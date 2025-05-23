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
) -> None:
    req = requests.post(
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
    )

    if req.status_code == 200:
        print(f"Successfully uploaded version {version}+{mc_version}")
    else:
        print(
            f"Couldn't upload version with file {file}.\n"
            f"Error code: {req.status_code}.\n"
            f"Error response: {req.text if req is not None else {}}\n"
        )
    return None


def get_existing_versions(project_id: str) -> list[dict]:
    return requests.get(
        f"https://api.modrinth.com/v2/project/{project_id}/version"
    ).json()


def update_body(project_id: str, project_dir: str | None = None) -> None:
    path = "README.md" if project_dir is None else f"{project_dir}/README.md"

    with open(path, "r") as rf:
        body = rf.read()
        req = requests.patch(
            f"https://api.modrinth.com/v2/project/{project_id}",
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


def send_discord_announcement(changelog: str, rp_role: str) -> None:
    requests.post(
        environ["DISCORDWH"],
        data=json.dumps(
            {
                "content": f"<@&{environ['DISCORD_ROLE_RPU']}> <@&{rp_role}> A new version of Dark Smooth GUI is available on Modrinth\n\n{changelog}"
            }
        ),
        headers={"Content-Type": "application/json"},
        timeout=1.0,
    )
    return None


def main(
    project_dir: str,
    project_id: str,
    project_name: str,
    version: str,
    changelog: str,
    rp_role: str,
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
            zip_file.write("../LICENSE", "LICENSE")
            zip_file.write("pack.png")
            zip_file.write(mcmeta_file, "pack.mcmeta")
            add_files_to_zip_rec("assets", zip_file)

            files.append((mc_version, version, file_name))

    ranges = {
        "1.17.x": ["1.17", "1.17.1"],
        "1.18.x": ["1.18", "1.18.1", "1.18.2"],
        "1.19-1.19.2": ["1.19", "1.19.1", "1.19.2"],
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
    existing_versions = tuple(
        ev["version_number"] for ev in get_existing_versions(project_id)
    )

    for mc_version, version, file_name in files:
        if f"{version}+{mc_version}" in existing_versions:
            print(
                f"Not uploading version {version}+{mc_version} because it is already on modrinth"
            )
            continue

        publish(
            mc_version,
            version,
            project_name,
            project_id,
            file_name,
            changelog,
            ranges[mc_version] if mc_version in ranges.keys() else [mc_version],
        )

    update_body(project_id)
    send_discord_announcement(changelog, rp_role)
    return None


if __name__ == "__main__":
    args = sys.argv
    if len(args) < 3:
        print("Invalid number of arguments; Aborting")
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

    if "bo" in args:
        update_body(project_id, project_dir)
    else:
        project_name = (
            "CTM OF-Fabric"
            if args[1] == "ctm"
            else "CTM Faithful"
            if args[1] == "ctmf"
            else "CTM Create"
        )
        version = args[2]
        changelog = args[3] if len(args) == 4 else "No changelog provided"
        rp_role = (
            environ["DISCORD_ROLE_CTM"]
            if args[1] == "ctm"
            else environ["DISCORD_ROLE_CTMF"]
            if args[1] == "ctmf"
            else environ["DISCORD_ROLE_CTMC"]
        )

        main(project_dir, project_id, project_name, version, changelog, rp_role)
