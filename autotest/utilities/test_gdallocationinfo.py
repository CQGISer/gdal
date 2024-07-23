#!/usr/bin/env pytest
# -*- coding: utf-8 -*-
###############################################################################
# $Id$
#
# Project:  GDAL/OGR Test Suite
# Purpose:  gdallocationinfo testing
# Author:   Even Rouault <even dot rouault @ spatialys.com>
#
###############################################################################
# Copyright (c) 2010-2013, Even Rouault <even dot rouault at spatialys.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.
###############################################################################

import sys

import pytest

sys.path.append("../gcore")

import gdaltest
import test_cli_utilities

from osgeo import gdal

pytestmark = pytest.mark.skipif(
    test_cli_utilities.get_gdallocationinfo_path() is None,
    reason="gdallocationinfo not available",
)


@pytest.fixture()
def gdallocationinfo_path():
    return test_cli_utilities.get_gdallocationinfo_path()


###############################################################################
# Test basic usage


def test_gdallocationinfo_1(gdallocationinfo_path):

    (ret, err) = gdaltest.runexternal_out_and_err(
        gdallocationinfo_path + " ../gcore/data/byte.tif 0 0"
    )
    assert err is None or err == "", "got error/warning"

    ret = ret.replace("\r\n", "\n")
    expected_ret = """Report:
  Location: (0P,0L)
  Band 1:
    Value: 107"""
    assert ret.startswith(expected_ret)


###############################################################################
# Test -xml


def test_gdallocationinfo_2(gdallocationinfo_path):

    ret = gdaltest.runexternal(
        gdallocationinfo_path + " -xml ../gcore/data/byte.tif 0 0"
    )
    ret = ret.replace("\r\n", "\n")
    expected_ret = """<Report pixel="0" line="0">
  <BandReport band="1">
    <Value>107</Value>
  </BandReport>
</Report>"""
    assert ret.startswith(expected_ret)


###############################################################################
# Test -valonly


def test_gdallocationinfo_3(gdallocationinfo_path):

    ret = gdaltest.runexternal(
        gdallocationinfo_path + " -b 1 -valonly ../gcore/data/byte.tif 0 0"
    )
    expected_ret = """107"""
    assert ret.startswith(expected_ret)


###############################################################################
# Test -geoloc


def test_gdallocationinfo_4(gdallocationinfo_path):

    ret = gdaltest.runexternal(
        gdallocationinfo_path + " -geoloc ../gcore/data/byte.tif 440720.000 3751320.000"
    )
    ret = ret.replace("\r\n", "\n")
    expected_ret = """Report:
  Location: (0P,0L)
  Band 1:
    Value: 107"""
    assert ret.startswith(expected_ret)


###############################################################################
# Test -lifonly


def test_gdallocationinfo_5(gdallocationinfo_path):

    ret = gdaltest.runexternal(
        gdallocationinfo_path + " -lifonly ../gcore/data/byte.vrt 0 0"
    )
    expected_ret1 = """../gcore/data/byte.tif"""
    expected_ret2 = """../gcore/data\\byte.tif"""
    assert expected_ret1 in ret or expected_ret2 in ret


###############################################################################
# Test -overview


def test_gdallocationinfo_6(gdallocationinfo_path, tmp_path):

    tmp_tif = str(tmp_path / "test_gdallocationinfo_6.tif")

    src_ds = gdal.Open("../gcore/data/byte.tif")
    ds = gdal.GetDriverByName("GTiff").CreateCopy(tmp_tif, src_ds)
    ds.BuildOverviews("AVERAGE", overviewlist=[2])
    ds = None
    src_ds = None

    ret = gdaltest.runexternal(f"{gdallocationinfo_path} {tmp_tif} 10 10 -overview 1")

    expected_ret = """Value: 130"""
    assert expected_ret in ret


def test_gdallocationinfo_wgs84(gdallocationinfo_path):

    ret = gdaltest.runexternal(
        gdallocationinfo_path
        + " -valonly -wgs84 ../gcore/data/byte.tif -117.6354747 33.8970515"
    )

    expected_ret = """115"""
    assert expected_ret in ret


###############################################################################


def test_gdallocationinfo_field_sep(gdallocationinfo_path):

    ret = gdaltest.runexternal(
        gdallocationinfo_path + ' -valonly -field_sep "," ../gcore/data/byte.tif',
        strin="0 0",
    )

    assert "107" in ret
    assert "," not in ret

    ret = gdaltest.runexternal(
        gdallocationinfo_path + ' -valonly -field_sep "," ../gcore/data/rgbsmall.tif',
        strin="15 16",
    )

    assert "72,102,16" in ret


###############################################################################


def test_gdallocationinfo_extra_input(gdallocationinfo_path):

    ret = gdaltest.runexternal(
        gdallocationinfo_path + " ../gcore/data/byte.tif", strin="0 0 foo bar"
    )

    assert "Extra input: foo bar" in ret

    ret = gdaltest.runexternal(
        gdallocationinfo_path + " -valonly ../gcore/data/byte.tif", strin="0 0 foo bar"
    )

    assert "107" in ret
    assert "foo bar" not in ret

    ret = gdaltest.runexternal(
        gdallocationinfo_path + ' -valonly -field_sep "," ../gcore/data/byte.tif',
        strin="0 0 foo bar",
    )

    assert "107,foo bar" in ret

    ret = gdaltest.runexternal(
        gdallocationinfo_path + " -xml ../gcore/data/byte.tif", strin="0 0 foo bar"
    )

    assert "<ExtraInput>foo bar</ExtraInput>" in ret


###############################################################################


def test_gdallocationinfo_extra_input_ignored(gdallocationinfo_path):

    ret = gdaltest.runexternal(
        gdallocationinfo_path
        + ' -valonly -field_sep "," -ignore_extra_input ../gcore/data/byte.tif',
        strin="0 0 foo bar",
    )

    assert "107" in ret
    assert "foo bar" not in ret


###############################################################################
# Test echo mode


def test_gdallocationinfo_echo(gdallocationinfo_path):

    _, err = gdaltest.runexternal_out_and_err(
        gdallocationinfo_path + " -E ../gcore/data/byte.tif 1 2"
    )
    assert "-E can only be used with -valonly" in err

    _, err = gdaltest.runexternal_out_and_err(
        gdallocationinfo_path + " -E -valonly ../gcore/data/byte.tif 1 2"
    )
    assert (
        "-E can only be used if -field_sep is specified (to a non-newline value)" in err
    )

    ret = gdaltest.runexternal(
        gdallocationinfo_path + ' -E -valonly -field_sep "," ../gcore/data/byte.tif',
        strin="1 2",
    )
    assert "1,2,132" in ret


###############################################################################
# Test out of raster coordinates


def test_gdallocationinfo_out_of_raster_coordinates_valonly(gdallocationinfo_path):

    ret = gdaltest.runexternal(
        gdallocationinfo_path + " -valonly ../gcore/data/byte.tif",
        strin="1 2\n-1 -1\n1 2",
    )

    ret = ret.replace("\r\n", "\n")
    assert "132\n\n132\n" in ret

    ret = gdaltest.runexternal(
        gdallocationinfo_path + ' -E -valonly -field_sep "," ../gcore/data/byte.tif',
        strin="1 2\n-1 -1\n1 2",
    )

    ret = ret.replace("\r\n", "\n")
    assert "1,2,132\n-1,-1,\n1,2,132\n" in ret


def test_gdallocationinfo_out_of_raster_coordinates_valonly_multiband(
    gdallocationinfo_path,
):

    ret = gdaltest.runexternal(
        gdallocationinfo_path + " -valonly ../gcore/data/rgbsmall.tif",
        strin="1 2\n-1 -1\n1 2",
    )

    ret = ret.replace("\r\n", "\n")
    assert "0\n0\n0\n\n\n\n0\n0\n0\n" in ret

    ret = gdaltest.runexternal(
        gdallocationinfo_path
        + ' -E -valonly -field_sep "," ../gcore/data/rgbsmall.tif',
        strin="1 2\n-1 -1\n1 2",
    )

    ret = ret.replace("\r\n", "\n")
    assert "1,2,0,0,0\n-1,-1,,,\n1,2,0,0,0\n" in ret


###############################################################################


def test_gdallocationinfo_nad27_interpolate_bilinear(gdallocationinfo_path):

    # run on nad27 explicitly to avoid datum transformations.
    ret = gdaltest.runexternal(
        gdallocationinfo_path
        + " -valonly  -r bilinear -l_srs EPSG:4267 ../gcore/data/byte.tif -117.6354747 33.8970515"
    )

    assert float(ret) == pytest.approx(130.476908, rel=1e-4)


def test_gdallocationinfo_nad27_interpolate_cubicspline(gdallocationinfo_path):

    ret = gdaltest.runexternal(
        gdallocationinfo_path
        + " -valonly  -r cubicspline -l_srs EPSG:4267 ../gcore/data/byte.tif -117.6354747 33.8970515"
    )

    assert float(ret) == pytest.approx(125.795025, rel=1e-4)


def test_gdallocationinfo_report_geoloc_interpolate_bilinear(gdallocationinfo_path):

    ret = gdaltest.runexternal(
        gdallocationinfo_path
        + " -r bilinear -geoloc ../gcore/data/byte.tif 441319.09 3750601.80"
    )
    ret = ret.replace("\r\n", "\n")
    assert "Report:" in ret
    assert "Location: (9.98" in ret
    assert "P,11.97" in ret
    assert "Value: 137.2524" in ret


def test_gdallocationinfo_report_interpolate_bilinear(gdallocationinfo_path):

    ret = gdaltest.runexternal(
        gdallocationinfo_path + " -r bilinear ../gcore/data/byte.tif 9.98 11.97"
    )
    ret = ret.replace("\r\n", "\n")
    assert "Report:" in ret
    assert "Location: (9.98" in ret
    assert "P,11.97" in ret
    assert "Value: 137.24" in ret


def test_gdallocationinfo_value_interpolate_bilinear(gdallocationinfo_path):

    # Those coordinates are almost 10,12. It is testing that they are not converted to integer.
    ret = gdaltest.runexternal(
        gdallocationinfo_path
        + " -valonly -r bilinear ../gcore/data/byte.tif 9.9999999 11.9999999"
    )
    assert float(ret) == pytest.approx(139.75, rel=1e-6)


def test_gdallocationinfo_interpolate_float_data(gdallocationinfo_path, tmp_path):
    dst_filename = str(tmp_path / "tmp_float.tif")
    driver = gdal.GetDriverByName("GTiff")
    dst_ds = driver.Create(
        dst_filename, xsize=2, ysize=2, bands=1, eType=gdal.GDT_Float32
    )
    np = pytest.importorskip("numpy")
    raster_array = np.array(([10.5, 1.1], [2.4, 3.8]))
    dst_ds.GetRasterBand(1).WriteArray(raster_array)
    dst_ds = None

    ret = gdaltest.runexternal(
        gdallocationinfo_path + " -valonly -r bilinear {} 1 1".format(dst_filename)
    )
    assert float(ret) == pytest.approx(4.45, rel=1e-6)
