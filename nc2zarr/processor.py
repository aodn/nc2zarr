# The MIT License (MIT)
# Copyright (c) 2021 by Brockmann Consult GmbH and contributors
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

from typing import Any, Tuple, Dict

import xarray as xr


class DatasetProcessor:
    def __init__(self,
                 process_rename: Dict[str, str] = None,
                 process_rechunk: Dict[str, Dict[str, int]] = None,
                 output_encoding: Dict[str, Dict[str, Any]] = None):
        self._process_rename = process_rename
        self._process_rechunk = process_rechunk
        self._output_encoding = output_encoding

    def process_dataset(self, ds: xr.Dataset) -> Tuple[xr.Dataset, Dict[str, Dict[str, Any]]]:
        if self._process_rename:
            ds = ds.rename(self._process_rename)
        if self._process_rechunk:
            chunk_encoding = self._get_chunk_encodings(ds, self._process_rechunk)
        else:
            chunk_encoding = dict()
        return ds, self._merge_encodings(ds,
                                         chunk_encoding,
                                         self._output_encoding or {})

    @classmethod
    def _get_chunk_encodings(cls,
                             ds: xr.Dataset,
                             process_rechunk: Dict[str, Dict[str, int]]) \
            -> Dict[str, Dict[str, Any]]:
        output_encoding = dict()
        all_chunk_sizes = process_rechunk.get('*', {})
        for k, v in ds.variables.items():
            var_name = str(k)
            var_chunk_sizes = dict(all_chunk_sizes)
            var_chunk_sizes_delta = process_rechunk.get(var_name, {})
            if var_chunk_sizes_delta is None:
                var_chunk_sizes_delta = {dim_name: None for dim_name in v.dims}
            elif isinstance(var_chunk_sizes_delta, int):
                var_chunk_sizes_delta = {var_name: var_chunk_sizes_delta}
            var_chunk_sizes.update(var_chunk_sizes_delta)
            chunks = []
            for dim_index in range(len(v.dims)):
                dim_name = v.dims[dim_index]
                if dim_name in var_chunk_sizes:
                    chunks.append(var_chunk_sizes[dim_name] or v.sizes[dim_name])
                else:
                    chunks.append(v.chunks[dim_index]
                                  if v.chunks is not None else v.sizes[dim_name])
            output_encoding[var_name] = dict(chunks=tuple(chunks))
        return output_encoding

    @classmethod
    def _merge_encodings(cls,
                         ds: xr.Dataset,
                         *encodings: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        output_encoding = dict()
        for encoding in encodings:
            for k, v in ds.variables.items():
                var_name = str(k)
                if var_name in encoding:
                    if var_name not in output_encoding:
                        output_encoding[var_name] = dict(encoding[var_name])
                    else:
                        output_encoding[var_name].update(encoding[var_name])
        return output_encoding
