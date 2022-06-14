# Quickly generate a list of selected variables from a netcdf file by declaring to be dropped variables
# The list of selected variables to be provided for nc2zarr config templates

# Import some libraries
# switch to nc2zarr env in your terminal first
import netCDF4

# Declare a netcdf file with path here
netcdf_file = 'inputs/mooring/IMOS_DWM-ASFS_V_20100317T113000Z_SOFS_FV01_30m_END-20100721T180000Z_C-20120702T063213Z.nc'

# Declare to be dropped variables here
dropped_vars = ['']

# List out netcdf_file's variables
dset = netCDF4.Dataset(netcdf_file)
all_vars = list(dset.variables)

# select variables
selected_vars = sorted(list(set(all_vars) - set(dropped_vars)), key=len)

# print out to terminal
# copy and paste the results to the yml config file
for i, var in enumerate(selected_vars):
    print('    - ' + var)
