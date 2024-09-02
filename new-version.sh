#!/bin/sh

if [ $# -ne 3 ]; then
	echo "Missing arguments"
	exit 1
fi

V_1_17_X="\"1.17\", \"1.17.1\""
V_1_18_X="\"1.18\", \"1.18.1\", \"1.18.2\""
V_1_19_X="\"1.19\", \"1.19.1\", \"1.19.2\", \"1.19.3\", \"1.19.4\""
V_1_20_X="\"1.20\", \"1.20.1\", \"1.20.2\", \"1.20.3\", \"1.20.4\", \"1.20.5\", \"1.20.6\""
V_1_21_X="\"1.21\", \"1.21.1\""

PROJECT="$1"
VERSION="$2"
MC_VERSIONS=""

# Iterates over each version of the third option (each version is separated by a comma)
export IFS=','
for MC_VER in $3; do
	STR_VERS=""
	case $MC_VER in
	"1.17.x") STR_VERS=$V_1_17_X ;;
	"1.18.x") STR_VERS=$V_1_18_X ;;
	"1.19.x") STR_VERS=$V_1_19_X ;;
	"1.20.x") STR_VERS=$V_1_20_X ;;
	"1.21.x") STR_VERS=$V_1_21_X ;;
	*) ;;
	esac
	if [ "$MC_VERSIONS" = "" ]; then
		MC_VERSIONS="$STR_VERS"
	else
		MC_VERSIONS="$MC_VERSIONS, $STR_VERS"
	fi
done

JSON="{
    \"name\": \"$PROJECT $VERSION\",
    \"version_number\": \"$VERSION+\",
    \"changelog\": \"List of changes in this version: ...\",
    \"dependencies\":
    [
        {
            \"project_id\": \"1IjD5062\",
            \"dependency_type\": \"required\"
        }
    ],
    \"game_versions\":
    [
        $MC_VERSIONS
    ],
    \"version_type\": \"release\",
    \"loaders\":
    [
        \"minecraft\"
    ],
    \"featured\": true,
    \"status\": \"draft\",
    \"project_id\": \"uJt1qseH\",
    \"file_parts\":
    [
        \"test.zip\"
    ]
}"

echo "$JSON"

curl \
	-H "Content-Type: multipart/form-data" \
	-H "Authorization: $MODRINTH_TOKEN" \
	-F "data=$JSON" \
	-F "upload=@test.zip" \
	https://api.modrinth.com/v2/version
