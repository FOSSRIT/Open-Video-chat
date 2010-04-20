#!/bin/sh
#
# publish.sh - Prepare a reST-formatted article for publication
# Copyright (c) 2007 Free Software Foundation, Inc.
# Written by Brett Smith
#
# This program creates and deletes a lot of files in the current directory.
# You should not run it inside a directory that has files that are not part
# of an article.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#
#   1. Redistributions of source code must retain the above copyright
#      notice, this list of conditions and the following disclaimer.
#
#   2. Redistributions in binary form must reproduce the above copyright
#      notice, this list of conditions and the following disclaimer in the
#      documentation and/or other materials provided with the
#      distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE FREE SOFTWARE FOUNDATION ``AS IS'' AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE FREE SOFTWARE FOUNDATION OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
# PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

GWIDTH="5in"

set -e

name="quick-guide-gplv3"
src=${1:-$name.txt}
bn=$(echo "$src" | sed -e 's/\.[^.]*$//')

mkdir $name || {
    echo "Directory $name already exists; aborting." >&2
    exit 1
}
rm -rf "$bn.tar.gz"
cp "$src" *.{dia,png,svg} titlepage.tex publish.sh README $name
tar -czf "$bn.tar.gz" $name
rm -rf $name

rst2html --strict --initial-header-level=2 --no-doc-info <"$src" >"$bn.html"

rst2latex --strict <"$src" | \
    perl -ple "s/\[width=[^\]]+\]/[width=$GWIDTH]/" >"$bn.tex~"
startline=$(grep -n '^\\begin{document}' "$bn.tex~" | head -n 1 | \
    cut -d ':' -f 1)
for lineno in $(grep -n '^\\setlength' "$bn.tex~" | cut -d ':' -f 1); do
    if [ $startline -lt $lineno ]; then
        endline=$lineno
        break
    fi
done
lastline=$(wc -l "$bn.tex~" | awk '{print $1}')
head -n $startline "$bn.tex~" >"$bn.tex"
cat titlepage.tex >>"$bn.tex"
tail -n $(($lastline - $endline)) "$bn.tex~" >>"$bn.tex"
    
pdflatex "$bn.tex"
