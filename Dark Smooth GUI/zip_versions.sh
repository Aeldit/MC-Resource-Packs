#!/bin/sh

if [ $# -ne 1 ]; then
	echo "Version not specified; Aborting"
	exit 1
fi

if [ -f "pack.mcmeta" ]; then
	rm "pack.mcmeta"
fi

rm Dark\ Smooth\ GUI*.zip

# Obtains the MC version using each directory
VERSIONS=$(ls -d */ | sed 's#/##')

for ver in $VERSIONS; do
	if [ -d "assets/" ]; then
		rm -r assets/ pack.mcmeta
	fi
	cp -r $ver/assets $ver/pack.mcmeta ./
	zip -r "Dark Smooth GUI $1+$ver.zip" assets/ LICENSE.txt pack.png pack.mcmeta
done

rm -r "assets/"
rm "pack.mcmeta"
