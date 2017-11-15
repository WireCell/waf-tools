#!/bin/bash

usage () {
    cat <<EOF
Configure WCT source for a "view" providing external dependencies.

This script should be kept in the "waftools" git submodule of WCT.
But, it may be run from anywhwere:

  ./waftools/wct-configure-for-view.sh <path-to-view> [<path-to-install>]

 - <path-to-view> :: the file system path to the top of the view directory.

 - <path-to-install> :: optional location for installing WCT.  It
   defaults to installing into the view.

Notee: A likely way to create a "view" directory is with Spack:

  spack view add -i /opt/spack/views/wct-dev wirecell-toolkit

EOF
    exit 1
}

view="$1"
if [ -z "$view" ] ; then
    usage
fi
inst="${2:-view}"

topdir=$(dirname $(dirname $(readlink -f $BASH_SOURCE)))

"$topdir/wcb" \
    configure \
    --with-jsoncpp="$view" \
    --with-jsonnet="$view" \
    --with-tbb="$view" \
    --with-eigen="$view" \
    --with-root="$view" \
    --with-fftw="$view" \
    --boost-includes="$view/include" \
    --boost-libs="$view/lib" \
    --boost-mt \
    --with-tbb=false \
    --prefix="$inst"


#--with-fftw-include="$view/include" \
#--with-fftw-lib="$view/lib" \

cat <<EOF
For runtime setup, copy-paste:
PATH=$view/bin:\$PATH
export LD_LIBRARY_PATH=$view/lib:\$LD_LIBRARY_PATH
EOF




