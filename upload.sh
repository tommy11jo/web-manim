#!/bin/bash
# clear the previous wheel 
rm -r dist/*

# generate the wheel from source files
python3 setup.py sdist bdist_wheel

# upload to testpypi
twine upload --repository testpypi dist/*