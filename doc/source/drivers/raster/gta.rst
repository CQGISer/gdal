.. _raster.gta:

================================================================================
GTA - Generic Tagged Arrays
================================================================================

.. shortname:: GTA

.. build_dependencies:: libgta

GDAL can read and write GTA data files through
the libgta library.

GTA is a file format that can store any kind of multidimensional array
data, allows generic manipulations of array data, and allows easy
conversion to and from other file formats.

Driver capabilities
-------------------

.. supports_createcopy::

.. supports_georeferencing::

Creation options
----------------

|about-creation-options|
The following creation options are supported:

-  .. co:: COMPRESS
      :choices: NONE, BZIP2, XZ, ZLIB, ZLIB1, ZLIB2, ZLIB3, ZLIB4, ZLIB5, ZLIB6, ZLIB7, ZLIB8, ZLIB9
      :default: NONE

      Set the GTA compression method.


See Also
--------

-  `GTA home page <http://gta.nongnu.org>`__
