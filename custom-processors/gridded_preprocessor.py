import numpy as np
import xarray as xr


def preprocess_time(dataset):
    """Force a dtype of "<i8" on the time array"""

    data_array = xr.DataArray(data=np.array("", dtype="<i8"), name="time")
    data_array.attrs.update(dataset.crs.attrs)
    dataset["time"] = data_array
    dataset["time"].attrs.pop("_FillValue", None)
    return dataset
