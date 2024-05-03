"""
This module plots the change in monthly US seasonally adjusted US nonfarm
employment (PAYEMS) by industry. The data is either taken from the St. Louis
Federal Reserve's FRED system(https://fred.stlouisfed.org/) or loads it from
this directory.

https://www.bls.gov/webapps/legacy/cesbtab1.htm

This module defines the following function(s):
    usempl_ind_chg()

The industries are:
| Industry                                 | Series ID     |  Sep 2003   |   Apr 2024  |
|------------------------------------------|---------------|-------------|-------------|
- Total nonfarm:                             CES0000000001   130_252_000   158_286_000
  - Total private:                           CES0500000001   108_748_000   135_015_000
    - Goods Producing:                       CES0600000001    21_700_000    21_821_000
      - Mining and Logging                   CES1000000001       570_000       641_000
      - Construction                         CES2000000001     6_783_000     8_219_000
      - Manufacturing                        CES3000000001    14_347_000    12_961_000
    - Private Service Providing:             CES0800000001    87_048_000   113_194_000
      - Wholesale Trade                      CES4142000001     5_537_400     6_169_700
      - Retail Trade                         CES4200000001    14_911_800    15_677_900
      - Transportation and Warehousing       CES4300000001     4_162_100     6_575_800
      - Utilities                            CES4422000001       573_100       587_400
    - Information                            CES5000000001     3_162_000     3_013_000
    - Financial Activities                   CES5500000001     8_100_000     9_233_000
    - Professional and Business Services     CES6000000001    16_108_000    22_942_000
    - Private Education and Health Services: CES6500000001    16_883_000    26_194_000
      - Private Educational Services         CES6561000001     2_693_700     3_869_300
      - Health Care and Social Assistance    CES6562000001    14_189_400    22_324_300
    - Leisure and Hospitality                CES7000000001    12_208_000    16_897_000
    - Other Services                         CES8000000001     5_403_000     5_904_000
  - Government:                              CES9000000001    21_504_000    23_271_000
    - Federal Government                     CES9091000001     2_749_000     2_993_000
    - State Government                       CES9092000001     4_980_000     5_451_000
    - Local Government                       CES9093000001    13_775_000    14_827_000

Use this URL for API access: https://data.bls.gov/cgi-bin/srgate
"""

# Import packages
import numpy as np
import pandas as pd
import pandas_datareader as pddr
import datetime as dt
import os
from usempl_plots.get_payems import get_payems_data
from bokeh.io import output_file
from bokeh.plotting import curdoc, figure, show
from bokeh.models import ColumnDataSource, Title, Legend, HoverTool, LabelSet
from bokeh.layouts import gridplot

# from bokeh.models import Label
from bokeh.palettes import Category20, Plasma256, Viridis8

"""
Define functions
"""


def usempl_ind_chg(
    start_date="2003-09-01",
    end_date="max",
    download_from_internet=True,
    fig_title_strk=(
        "Change in US employment my industry: Sep. 2003 to Apr. 2024"
    ),
    html_show=True,
):
    """
    This function creates the HTML and JavaScript code for the dynamic
    visualization of the US change in monthly seasonally adjusted nonfarm
    employment (PAYEMS) by industry.

    Args:
        start_date (str): start date of PAYEMS time series in 'YYYY-mm-dd'
            format or 'min'
    """
    # Create data and images directory paths
    cur_path = os.path.split(os.path.abspath(__file__))[0]
    image_dir = os.path.join(cur_path, "images")
    data_dir = os.path.join(cur_path, "data")

    data_df = pd.read_csv(
        os.path.join(data_dir, "industry", "jobs_by_industry.csv")
    )
    data_df["diff_Sep03_Apr24"] = data_df["Apr24"] - data_df["Sep03"]
    data_df["pctchg_Sep03_Apr24"] = (
        (data_df["Apr24"] - data_df["Sep03"]) / data_df["Sep03"]
    ) * 100

    print(
        "Total jobs created from Sep. 2003 to Apr. 2024: ",
        int(
            data_df.loc[
                data_df["Industry"] == "Total nonfarm", "diff_Sep03_Apr24"
            ]
        ),
    )
    print("")
    print(
        "Percent change in jobs from Sep. 2003 to Apr. 2024:",
        data_df.loc[
            data_df["Industry"] == "Total nonfarm", "pctchg_Sep03_Apr24"
        ],
    )
    print("")
    print(
        data_df[
            [
                "Industry",
                "Sep03",
                "Apr24",
                "diff_Sep03_Apr24",
                "pctchg_Sep03_Apr24",
            ]
        ]
    )

    return data_df


if __name__ == "__main__":
    # execute only if run as a script
    data_df = usempl_ind_chg()
