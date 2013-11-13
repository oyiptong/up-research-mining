#!/bin/sh

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

set -x

rm -rf upstudy-env

virtualenv --python=python2.7 --no-site-packages upstudy-env
. upstudy-env/bin/activate

export MOZ_UPSTUDY_DEV=1

createdb up-research
python setup.py develop
./scripts/upstudy-pgsql-init.py
