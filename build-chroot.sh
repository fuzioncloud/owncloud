#!/bin/bash

if [ ! -f "rootfs.tar.gz" ]; then
    echo "rootfs is not ready, run 'sudo ./bootstrap.sh'"
    exit 1
elae
    echo "rootfs.tar.gz is here"
fi

rm -rf rootfs
tar xzf rootfs.tar.gz
cp -r ./* rootfs/root
chroot rootfs root/build.sh
mv rootfs/root/owncloud.tar.gz .