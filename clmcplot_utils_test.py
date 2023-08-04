import clmcplot_utils as cu
import numpy as np

# Create a fake data file.
data = np.random.rand(100, 10)
vnames = ['v1', 'v2', 'v3', 'v4', 'v5', 'v6', 'v7', 'v8', 'v9', 'v10']
vunits = ['m', 'm', 'm', 'm', 'm', 'm', 'm', 'm', 'm', 'm']
desc = {'n_cols': 10, 'n_rows': 100, 'freq': 1000}

# Write the data file.
filename1 = cu.save_to_clmcplot_format(
    data=data,
    variable_names=vnames,
    variable_unit_names=vunits,
    desc=desc,
    path='./',
)

# Read the data file.
data_out, vnames, vunits, desc = cu.read_from_clmcplot_format(filename1)

# Write the data file again such this can be compare against the previous one.
filename2 = cu.save_to_clmcplot_format(
    data=data,
    variable_names=vnames,
    variable_unit_names=vunits,
    desc=desc,
    path='./',
)

print('Compare files %s and %s\n' % (filename1, filename2))
