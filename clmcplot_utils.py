"""Utility functions for read/write of clmcplot data files.

Note:
These utility methods convert back-and-forth between clmcplot files and
numpy arrays and associated dicts.
"""
import os
import numpy as np


##############################################################################
def save_to_clmcplot_format(
    data: np.ndarray,
    variable_names: list[str],
    variable_unit_names: list[str],
    desc: dict[str, float],
    path: str = '/tmp',
) -> str:
  """Creates clmcplot data file in given directory path.

  clmcplot data files are named dxxxxx, where xxxxx is a 5 digit number
  starting at 0. The file .last_data in the directory 'path' is
  created/maintained to remember the last file number. Automatically, the
  file number is incremented by 1 each time a new file is saved in this
  directory. A existing file with the same name will be overwritten, but this
  can only happen if .last_data is altered manually.

  Note that the time variables are reset to start at zero to create more
  readable numbers for clmcplot.

  Args:
    data: data matrix
    variable_names: name of each column in matrix
    variable_unit_names: units of each column in matrix
    desc: descriptor dict including n_rows, n_cols, and sampling freq of data
    path: path where to save data

  Returns:
    filename of file that was created
  """
  # look for .last_data file in directory, and if it exists, it has
  # the file number of the current data to be saved to disk
  try:
    f = open(os.path.join(path, '.last_data'), 'r')
    file_number = np.fromfile(f, dtype=int, count=1, sep=' ')
    file_number = int(file_number[0])
    f.close()
  except IOError:
    file_number = 0

  # update .last_data to have the file number of the next file in the future
  try:
    f = open(os.path.join(path, '.last_data'), 'w')
    f.write('%d\n' % (file_number + 1))
    f.close()
  except IOError:
    print('Cannot open %s for write' % (os.path.join(path, '.last_data')))

  f = open(os.path.join(path, 'd%05d' % file_number), 'w')
  f.write(
      '%d %d %d %f\n'
      % (
          desc['n_rows'] * desc['n_cols'],
          desc['n_cols'],
          desc['n_rows'],
          desc['freq'],
      )
  )

  assert len(variable_names) == len(
      variable_unit_names
  ), 'len(variable_names) != len(variable_unit_names)'

  for name, unit in zip(variable_names, variable_unit_names):
    f.write('%s  %s  ' % (name, unit))
  f.write('\n')

  # clmcplot files are float32 in big endian format
  np.array(data, dtype='>f').tofile(f)
  f.close()
  data_filename = os.path.join(path, 'd%05d' % file_number)
  print(
      'Wrote file %s with %dx%d data'
      % (
          data_filename,
          desc['n_rows'],
          desc['n_cols'],
      )
  )

  return data_filename


##############################################################################
def read_from_clmcplot_format(
    filename: str,
) -> tuple[np.ndarray, list[str], list[str], dict[str, float]]:
  """Reads from a clmcplot data file into associated variables.

  Args:
    filename: the filename to read from

  Returns:
    A tuple of (data, variable_names, variable_unit_names, desc):
    * data: a numpy array (vector) of data collected
    * variable_names: the name of each element of the data vector
    * variable_unit_names: the unit names associated with each variable
    * desc: descriptor dict including n_rows, n_cols, and sampling freq of data
  """

  # try to read the file
  try:
    f = open(filename, 'r', errors='ignore')

    # The first line contains number of values, number of columns,
    # number of rows, and sampling frequency.
    line = f.readline().strip()
    line_split = line.split(' ')
    for l in line_split:
        if l == '':
            line_split.remove(l)

    values = [float(i) for i in line_split]
      
    desc = {
        'n_cols': int(values[1]),
        'n_rows': int(values[2]),
        'freq': values[3],
    }

    # The second line contains variable names and units.
    line = f.readline().strip()
    values = [str(i) for i in line.split('  ')]
    variable_names = values[::2]
    variable_unit_names = values[1::2]

    data_list = np.fromfile(f, dtype='>f', sep='', count=-1)
    data = np.reshape(data_list, (desc['n_rows'], desc['n_cols']))

    return data, variable_names, variable_unit_names, desc

  except IOError:
    print('Cannot open %s for read' % (filename))
