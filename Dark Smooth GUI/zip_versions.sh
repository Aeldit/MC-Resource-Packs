#!/bin/sh

if [ $# != 1 ]; then
	echo "Version not specified; Aborting"
	exit 1
fi

# Obtains the MC version using each directory
VERSIONS=$(ls -d */ | sed 's#/##')

echo "$VERSIONS"

for ver in $VERSIONS; do
	rm -r assets/ pack.mcmeta
	cp -r $ver/assets $ver/pack.mcmeta ./
	zip -r "Dark Smoot GUI $1+$ver.zip" assets/ LICENSE.txt pack.png pack.mcmeta
done
