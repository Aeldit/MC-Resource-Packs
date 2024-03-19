#!/bin/sh

if [ $# != 1 ]; then
	echo "Version not specified; Aborting"
	exit 1
fi

if [ -f "pack.mcmeta" ]; then
	rm "pack.mcmeta"
fi

# Obtains the MC version for each file
VERSIONS=$(ls *.mcmeta | cut -c 6-11)

echo "$VERSIONS"

for ver in $VERSIONS; do
	cp "pack_$ver.mcmeta" pack.mcmeta
	zip "CTM OF-Fabric $1+$ver.zip" assets/ LICENSE.txt CREDITS.txt pack.png pack.mcmeta
done