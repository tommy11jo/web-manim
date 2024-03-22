#!/bin/bash
# poetry build
# poetry publish --repository testpypi --build
# TODO: fix config

#!/bin/bash
# clear the previous wheel 
rm -r dist/*

# generate the wheel from source files
python3 setup.py sdist bdist_wheel

# upload to testpypi
twine upload --repository testpypi dist/*