#!/bin/sh

if [ -f "pack.mcmeta" ]; then
	rm "pack.mcmeta"
fi

# Removes any zip archive that is still in the directory
rm *.zip

# Obtains the MC version from each mcmeta file
VERSIONS=$(ls *.mcmeta | cut -d"/" -f2 | cut -c 6- | rev | cut -c 8- | rev)

for VER in $VERSIONS; do
	cp "pack_$VER.mcmeta" "pack.mcmeta"

	ZIPFILE="CTM OF-Fabric test+$VER.zip"
	zip -q -r "$ZIPFILE" \
		assets/ LICENSE.txt CREDITS.txt pack.png pack.mcmeta
	echo "Zip file created : $ZIPFILE"
done

rm "pack.mcmeta"
