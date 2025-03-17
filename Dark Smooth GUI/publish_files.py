#!/bin/env python3


from os import environ

import requests

version = "x.y.z"
mc_version = "1.21.x"
json_data = {
    "name": f"[{mc_version}] Dark Smooth GUI {version}",
    "version_number": f"{version}+{mc_version}",
    "changelog": "No changelog provided",
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
    "game_versions": ["1.21.x"],
    "version_type": "release",
    "loaders": ["minecraft"],
    "featured": True,
    "project_id": "3BPM3cU5",
    "file_parts": ["LICENSE.txt"],
}


def main() -> None:
    print(
        requests.post(
            "https://api.modrinth.com/v2/version",
            headers={"Authorization": environ["MODRINTH_TOKEN"]},
            data=json_data,
            files={"LICENSE.txt": open("LICENSE.txt", "rb")},
        ).json()
    )
    return None


if __name__ == "__main__":
    main()
