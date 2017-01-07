# MetaPlot

Metadata writer and helper functions for image files useful for tracking provenance in scientific plots.

# Dependencies

* Python `svn` module

* Python `pkg_resources` module

* we are currently using pyexiv2, can get it as

```
apt-get install python-pyexiv
```

# Install

```
python setup.py build
python setup.py install --user
```

or

```
python setup.py build
sudo python setup.py install
```

# Getting started

```
import metaplot as mp

print mp.helpers.test_helper()
```
