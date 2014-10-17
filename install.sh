#/bin/sh
defaultdest="/usr/local/bin"
dest=${1-$defaultdest}

mkdir -p "$dest"
cp modify-color $dest
