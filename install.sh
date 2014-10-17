#/bin/sh
defaultdest="/usr/local/bin"
dest=${1-$defaultdest}

mkdir -p "$dest"
cp color-util $dest
