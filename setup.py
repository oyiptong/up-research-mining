import os
from setuptools import setup

requires = []

if os.environ.has_key('MOZ_UPSTUDY_DEV'):
    requires.extend([
        "ipython==1.1.0",
        "psycopg2==2.5.1",
        "python-dateutil==2.2",
    ])

setup(
        name = "upstudy",
        version = "0.1",
        description = "Tools to help make sense of data for the UP User Research Study",
        author = "Mozilla",
        packages=["upstudy", "upstudy.rankers", "upstudy.data", "upstudy.data.backends"],
        namespace_packages=["upstudy"],
        include_package_data=True,
        install_requires = requires,
        scripts=[]
)
