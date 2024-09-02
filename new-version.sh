#!/bin/sh

# This script allows me to publish my 'CTM' packs automatically to modrinth

# Arg 1 = '.project' file
if [ $# -ne 1 ]; then
	echo "Missing arguments"
	exit 1
fi

# Checks if the given file contains 4 properties
# (by checking the number of '=' found)
if [ $(grep -e "=" $1 | wc -l) -ne 4 ]; then
	echo "The file '$1' does not contain the 4 required properties"
	exit 2
fi

# File parsing, obtains the 4 properties required for the script to work
CTR=0
while IFS= read R; do
	VAL=$(echo "$R" | cut -d"=" -f2)
	case $CTR in
	0) PROJECT_ID=$VAL ;;
	1) PROJECT_NAME=$VAL ;;
	2) PROJECT_VERSION=$VAL ;;
	3) PROJECT_DIR=$VAL ;;
	esac
	CTR=$((CTR + 1))
done <$1

V_1_17_X="\"1.17\", \"1.17.1\""
V_1_18_X="\"1.18\", \"1.18.1\", \"1.18.2\""
V_1_19_X="\"1.19\", \"1.19.1\", \"1.19.2\", \"1.19.3\", \"1.19.4\""
V_1_20_X="\"1.20\", \"1.20.1\", \"1.20.2\", \"1.20.3\", \"1.20.4\", \"1.20.5\", \"1.20.6\""
V_1_21_X="\"1.21\", \"1.21.1\""

publish_version() {
	MC_VERSION="$1"
	MC_VERSIONS_RANGE=""

	# Iterates over each version
	# (If multiple version are present ; ex: 1.20.x-1.21.x ;
	# each version is separated by a dash)
	for MC_VER in $(echo "$MC_VERSION" | tr '-' ' '); do
		STR_VERS=""

		case $MC_VER in
		"1.17.x") STR_VERS=$V_1_17_X ;;
		"1.18.x") STR_VERS=$V_1_18_X ;;
		"1.19.x") STR_VERS=$V_1_19_X ;;
		"1.20.x") STR_VERS=$V_1_20_X ;;
		"1.21.x") STR_VERS=$V_1_21_X ;;
		*) STR_VERS="\"$MC_VER\"" ;;
		esac

		if [ "$MC_VERSIONS_RANGE" = "" ]; then
			MC_VERSIONS_RANGE="$STR_VERS"
		else
			MC_VERSIONS_RANGE="$MC_VERSIONS_RANGE, $STR_VERS"
		fi
	done

	echo "Publishing version $MC_VERSION with range\n[$MC_VERSIONS_RANGE]\n"

	JSON="{
        \"name\": \"$PROJECT_NAME $PROJECT_VERSION\",
        \"version_number\": \"$PROJECT_VERSION+\",
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
            $MC_VERSIONS_RANGE
        ],
        \"version_type\": \"release\",
        \"loaders\":
        [
            \"minecraft\"
        ],
        \"featured\": true,
        \"status\": \"draft\",
        \"project_id\": \"$PROJECT_ID\",
        \"file_parts\":
        [
            \"test.zip\"
        ]
    }"

	#echo "$JSON"

	#curl \
	#	-H "Content-Type: multipart/form-data" \
	#	-H "Authorization: $MODRINTH_TOKEN" \
	#	-F "data=$JSON" \
	#	-F "upload=@test.zip" \
	#	https://api.modrinth.com/v2/version
}

zip_files() {

	if [ -f "$PROJECT_DIR/pack.mcmeta" ]; then
		rm "$PROJECT_DIR/pack.mcmeta"
	fi

	# Removes any zip archive that is still in the directory
	rm "$PROJECT_DIR/"*.zip

	# Obtains the MC version from each mcmeta file
	VERSIONS=$(ls "$PROJECT_DIR"/*.mcmeta | cut -d"/" -f2 | cut -c 6- | rev | cut -c 8- | rev)

	for VER in $VERSIONS; do
		publish_version $VER
		#cp "$PROJECT_DIR/pack_$VER.mcmeta" "$PROJECT_DIR/pack.mcmeta"
		#zip -q -r "$PROJECT_DIR/CTM OF-Fabric $PROJECT_VERSION+$VER.zip" \
		#	$PROJECT_DIR/assets/ $PROJECT_DIR/LICENSE.txt \
		#	$PROJECT_DIR/CREDITS.txt $PROJECT_DIR/pack.png $PROJECT_DIR/pack.mcmeta
	done

	rm "$PROJECT_DIR/pack.mcmeta"
}

zip_files
