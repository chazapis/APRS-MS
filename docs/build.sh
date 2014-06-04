#!/bin/bash

cd "$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

for file in `ls *.rst`
do
    filename=`basename ${file} .rst`
    rst2html-2.7.py --stylesheet=rst2html.css --link-stylesheet ${filename}.rst ${filename}.html
done
