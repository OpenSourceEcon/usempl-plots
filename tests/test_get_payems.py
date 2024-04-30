"""
Tests of usempl_npp.py module

Three main tests:
* make sure that running the module as a script python usempl_npp_bokeh.py
  results in a saved html file and two csv data files in the correct
  directories
* data files are created with both download_from_internet==True and
  download_from_internet==False.
"""

from usempl_plots import get_payems


# Test that get_usempl_data() delivers the right structures and can download
# the data from the internet
def test_get_payems_data(end_date_str="2022-11-15"):
    data_tuple = get_payems.get_payems_data(end_date_str=end_date_str)
    assert len(data_tuple) == 3
    usempl_df, beg_date_str2, end_date_str2 = data_tuple

    assert usempl_df.shape == (1241, 6)
    assert beg_date_str2 == "1919-07-01"
    assert end_date_str2 == "2022-11-01"
