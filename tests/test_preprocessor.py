# The MIT License (MIT)
# Copyright (c) 2020 by Brockmann Consult GmbH and contributors
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
# of the Software, and to permit persons to whom the Software is furnished to do
# so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import unittest
from typing import List

import numpy as np
import xarray as xr

from nc2zarr.error import ConverterError
from nc2zarr.preprocessor import DatasetPreProcessor
from tests.helpers import new_test_dataset


class DatasetPreProcessorTest(unittest.TestCase):

    def test_select_variables(self):
        ds = new_test_dataset(day=1)
        self.assertIn('time', ds)
        pre_processor = DatasetPreProcessor(input_variables=['r_i32', 'lon', 'lat', 'time'],
                                            input_concat_dim='time')
        new_ds = pre_processor.preprocess_dataset(ds)
        self.assertIsInstance(new_ds, xr.Dataset)
        self.assertAllInDataset(['r_i32', 'lon', 'lat', 'time'], new_ds)
        self.assertNoneInDataset(['r_ui16', 'r_f32'], new_ds)

    def test_leaves_time_coord_untouched(self):
        ds = new_test_dataset(day=1)
        self.assertIn('time', ds)
        pre_processor = DatasetPreProcessor(input_variables=None,
                                            input_concat_dim='time')
        new_ds = pre_processor.preprocess_dataset(ds)
        self.assertIsInstance(new_ds, xr.Dataset)
        self.assertAllInDataset(['r_ui16', 'r_ui16', 'r_i32', 'lon', 'lat', 'time'], new_ds)
        self.assertIn('time', new_ds)
        self.assertEqual(ds.time, new_ds.time)

    def test_adds_time_dim_from_iso_format_attrs(self):
        ds = new_test_dataset(day=None)
        ds.attrs.update(time_coverage_start='2020-09-08 10:30:00',
                        time_coverage_end='2020-09-08 12:30:00')
        self._test_adds_time_dim(ds)

    def test_adds_time_dim_from_iso_format_attrs_2(self):
        ds = new_test_dataset(day=None)
        ds.attrs.update(time_coverage_start='2020-09-08T10:30:00Z',
                        time_coverage_end='2020-09-08T12:30:00Z')
        self._test_adds_time_dim(ds)

    def test_adds_time_dim_from_non_iso_format_attrs(self):
        ds = new_test_dataset(day=None)
        ds.attrs.update(time_coverage_start='20200908103000',
                        time_coverage_end='20200908123000')
        self._test_adds_time_dim(ds)

    def test_illegal_time_coverage(self):
        ds = new_test_dataset(day=None)
        ds.attrs.update(time_coverage_start='yesterday',
                        time_coverage_end='20200908123000')
        self._test_raises(ds, 'Cannot parse timestamp from "yesterday".')

    def test_missing_time_coverage(self):
        ds = new_test_dataset(day=None)
        self._test_raises(ds, 'Missing time_coverage_start and/or time_coverage_end in dataset attributes.')

        ds = new_test_dataset(day=None)
        ds.attrs.update(start_time='2020-09-08T10:30:00Z',
                        end_time='2020-09-08T12:30:00Z')
        self._test_raises(ds, 'Missing time_coverage_start and/or time_coverage_end in dataset attributes.')

    def test_illegal_concat_dim(self):
        ds = new_test_dataset(day=None)
        self._test_raises(ds, 'Missing (coordinate) variable "t" for dimension "t".',
                          input_concat_dim='t')

    def _test_adds_time_dim(self, ds: xr.Dataset):
        self.assertNotIn('time', ds)
        pre_processor = DatasetPreProcessor(input_variables=None, input_concat_dim='time')
        new_ds = pre_processor.preprocess_dataset(ds)
        self.assertIsInstance(new_ds, xr.Dataset)
        self.assertAllInDataset(['r_ui16', 'r_ui16', 'r_i32', 'lon', 'lat', 'time', 'time_bnds'], new_ds)
        self.assertEqual(1, len(new_ds.time))
        self.assertEqual(np.array(['2020-09-08T11:30:00'], dtype='datetime64[ns]'),
                         np.array(new_ds.time[0], dtype='datetime64[ns]'))
        self.assertEqual({'bounds': 'time_bnds'}, new_ds.time.attrs)
        self.assertEqual(1, len(new_ds.time_bnds))
        self.assertEqual(np.array(['2020-09-08T10:30:00'], dtype='datetime64[ns]'),
                         np.array(new_ds.time_bnds[0][0], dtype='datetime64[ns]'))
        self.assertEqual(np.array(['2020-09-08T12:30:00'], dtype='datetime64[ns]'),
                         np.array(new_ds.time_bnds[0][1], dtype='datetime64[ns]'))

    def _test_raises(self, ds, expected_message: str, input_concat_dim='time'):
        pre_processor = DatasetPreProcessor(input_variables=None, input_concat_dim=input_concat_dim)
        with self.assertRaises(ConverterError) as cm:
            pre_processor.preprocess_dataset(ds)
        self.assertEqual(expected_message, f'{cm.exception}')

    def assertAllInDataset(self, var_names: List[str], ds: xr.Dataset):
        for var_name in var_names:
            self.assertIn(var_name, ds)

    def assertNoneInDataset(self, var_names: List[str], ds: xr.Dataset):
        for var_name in var_names:
            self.assertNotIn(var_name, ds)
