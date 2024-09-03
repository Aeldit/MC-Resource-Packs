#!/bin/sh
###############################################################################
#  This script allows me to publish my 'CTM' packs automatically to modrinth  #
###############################################################################

# Arg 1 = '.project' file
if [ $# -ne 1 ]; then
	echo "Missing arguments"
	exit 1
fi

# Checks if the given file contains 4 properties
# (by checking the number of '=' found)
if [ $(grep -e "=" $1 | wc -l) -ne 3 ]; then
	echo "The file '$1' does not contain the 3 required properties"
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
	esac
	CTR=$((CTR + 1))
done <$1

# IDs of the 3 projects
ID_CTM="uJt1qseH"
ID_CTM_F="qtbeFoLR"
ID_CTM_C="3RaBwrJ0"

# Initializes '$PROJECT_DIR' to the correct directory
case "$PROJECT_ID" in
"$ID_CTM") PROJECT_DIR="CTM_OF_Fabric" ;;
"$ID_CTM_F") PROJECT_DIR="CTM_Faithful" ;;
"$ID_CTM_C") PROJECT_DIR="CTM_Create" ;;
esac

V_1_17_X="\"1.17\", \"1.17.1\""
V_1_18_X="\"1.18\", \"1.18.1\", \"1.18.2\""
V_1_19_X="\"1.19\", \"1.19.1\", \"1.19.2\", \"1.19.3\", \"1.19.4\""
V_1_20_X="\"1.20\", \"1.20.1\", \"1.20.2\", \"1.20.3\", \"1.20.4\", \"1.20.5\", \"1.20.6\""
V_1_21_X="\"1.21\", \"1.21.1\""

# Publishes the given version on Modrinth
# Takes 3 arguments :
# - the version
# - the file
# - the changelog
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

	JSON="{
        \"name\": \"[$MC_VERSION] $PROJECT_NAME $PROJECT_VERSION\",
        \"version_number\": \"$PROJECT_VERSION+$MC_VERSION\",
        \"changelog\": \"$CHANGELOG\",
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
            \"$2\"
        ]
    }"

	curl \
		-s -o /dev/null \
		-H "Content-Type: multipart/form-data" \
		-H "Authorization: $MODRINTH_TOKEN" \
		-F "data=$JSON" \
		-F "upload=@test.zip" \
		https://api.modrinth.com/v2/version

	echo "Published version $MC_VERSION with range\n[$MC_VERSIONS_RANGE]\n"
}

# Sends a message in my discord's announcements channel with the changelog of
# the version
# Arg 1 = versions
send_discord_announcement() {
	VERSIONS=""

	# Puts the versions in the form of a list separated by commas
	for VER in $1; do
		if [ "$VERSIONS" = "" ]; then
			VERSIONS="\`$VER\`"
		else
			VERSIONS="$VERSIONS, \`$VER\`"
		fi
	done

	# Use the correct project role ping (Can be '@CTM', '@CTM Faithful' or '@CTM Create')
	case "$PROJECT_ID" in
	"$ID_CTM") PROJECT_ROLE="<@&1109052269594427432>" ;;
	"$ID_CTM_F") PROJECT_ROLE="<@&1109052339286978641>" ;;
	"$ID_CTM_C") PROJECT_ROLE="<@&1137806476031828078>" ;;
	esac

	# Puts the correct URL
	case "$PROJECT_ID" in
	"$ID_CTM") URL="https://modrinth.com/resourcepack/ctm-of-fabric/versions" ;;
	"$ID_CTM_F") URL="https://modrinth.com/resourcepack/ctm-faithful/versions" ;;
	"$ID_CTM_C") URL="https://modrinth.com/resourcepack/ctm-create/versions" ;;
	esac

	MESSAGE="<@&1097106407972671538> $PROJECT_ROLE \`$PROJECT_VERSION\` for $VERSIONS is now available on Modrinth ($URL)"

	curl \
		-H "Accept: application/json" \
		-H "Content-Type:application/json" \
		-X POST \
		-d "{\"content\": \"$MESSAGE\"}" \
		https://discord.com/api/webhooks/1280508752692383764/2nsRuaESd3PVHMohVX89HxVTibax_ZiNjcW1JnigRQJ9n07mYRrpvxI74NA-lVNyA1-K
}

# Searches the 'mcmeta' files in the 'PROJECT_DIR directory and obtains the
# versions from it, then creates the zip files and publishes the version on
# Modrinth
zip_files() {
	cd "$PROJECT_DIR"
	if [ -f "pack.mcmeta" ]; then
		rm "pack.mcmeta"
	fi

	if [ -f "changelog.md" ]; then
		CHANGELOG=$(cat "changelog.md")
	else
		CHANGELOG="No changelog provided"
	fi

	# Removes any zip archive that is still in the directory
	rm *.zip

	# Obtains the MC version from each mcmeta file
	VERSIONS=$(ls *.mcmeta | cut -d"/" -f2 | cut -c 6- | rev | cut -c 8- | rev)

	for VER in $VERSIONS; do
		cp "pack_$VER.mcmeta" "pack.mcmeta"

		ZIPFILE="$PROJECT_NAME $PROJECT_VERSION+$VER.zip"
		echo "Zipfile = $ZIPFILE"
		zip -q -r "$ZIPFILE" \
			assets/ LICENSE.txt CREDITS.txt pack.png pack.mcmeta

		publish_version "$VER" "$ZIPFILE" "$CHANGELOG"
	done

	rm *.zip
	rm "pack.mcmeta"

	send_discord_announcement "$VERSIONS"
}

zip_files
