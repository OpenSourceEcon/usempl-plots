"""
This module downloads the U.S. total nonfarm payrolls seasonally adjusted
(PAYEMS) monthly time series from the St. Louis Federal Reserve's FRED system
(https://fred.stlouisfed.org/series/PAYEMS) or loads it from this directory.

This module defines the following function(s):
    get_payems_data()
"""

# Import packages
import numpy as np
import pandas as pd
import pandas_datareader as pddr
import datetime as dt
import os

"""
Define functions
"""


def get_payems_data(
    beg_date_str="1919-01-01", end_date_str="today", file_path=None
):
    """
    This function either downloads or reads in the U.S. total nonfarm payrolls
    seasonally adjusted monthly data series (PAYEMS).

    Args:
        beg_date_str (str): beg date of PAYEMS time series in 'YYYY-mm-dd'
            format or None
        end_date_str (str): end date of PAYEMS time series in 'YYYY-mm-dd'
            format or "today" or None
        file_path: =None or string path to .csv file. If = None, download data
            from fred.stlouisfed.org, otherwise read data from local directory

    Other functions and files called by this function:
        usempl_payems_[yyyy-mm-dd].csv or file_path

    Files created by this function:
        usempl_payems_[yyyy-mm-dd].csv

    Returns:
        usempl_pk (DataFrame): N x 46 DataFrame of mths_frm_peak, Date{i},
            Close{i}, and close_dv_pk{i} for each of the 15 recessions for the
            periods specified by bkwd_days_max and frwd_days_max
        end_date_str2 (str): actual end date of DJIA time series in
            'YYYY-mm-dd' format. Can differ from the end_date input to this
            function if the final data for that day have not come out yet
            (usually 2 hours after markets close, 6:30pm EST), or if the
            end_date is one on which markets are closed (e.g. weekends and
            holidays). In this latter case, the pandas_datareader library
            chooses the most recent date for which we have DJIA data.
        peak_vals (list): list of peak DJIA value at the beginning of each of
            the last 15 recessions
        peak_dates (list): list of string date (YYYY-mm-dd) of peak DJIA value
            at the beginning of each of the last 15 recessions
        rec_label_yr_lst (list): list of string start year and end year of each
            of the last 15 recessions
        rec_label_yrmth_lst (list): list of string start year and month and end
            year and month of each of the last 15 recessions
        rec_beg_yrmth_lst (list): list of string start year and month of each
            of the last 15 recessions
        maxdate_rng_lst (list): list of tuples with start string date and end
            string date within which range we define the peak DJIA value at the
            beginning of each of the last 15 recessions
    """
    # Input validation
    if beg_date_str != None:
        try:
            beg_date = dt.datetime.strptime(beg_date_str, "%Y-%m-%d")
        except:
            err_msg = (
                "Error get_payems.py: beg_date_str input must be either a "
                + "date string in 'YYYY-mm-dd' format or None."
            )
            raise ValueError(err_msg)
    if beg_date_str != None and beg_date < dt.datetime(1919, 1, 1):
        err_msg = (
            "Error get_payems.py module: beg_date_str input must be a date "
            + "string in 'YYYY-mm-dd' format that is on or later than "
            + "1919-01-01."
        )
        raise ValueError(err_msg)
    if end_date_str != "today" and end_date_str != None:
        try:
            end_date = dt.datetime.strptime(end_date_str, "%Y-%m-%d")
        except:
            err_msg = (
                "Error get_payems.py: end_date_str input must be either a "
                + "date string in 'YYYY-mm-dd' format or 'Today' or None."
            )
            raise ValueError(err_msg)
    elif end_date_str == "today":
        end_date = dt.datetime.today()
    if beg_date_str != None and end_date_str != None and beg_date > end_date:
        err_msg = (
            "Error get_payems.py module: beg_date_str input must be a date "
            + "string in 'YYYY-mm-dd' format that is on or earlier than "
            + "end_date_str input."
        )
        raise ValueError(err_msg)

    # Name the current directory and make sure it has a data folder
    cur_path = os.path.split(os.path.abspath(__file__))[0]
    data_fldr = "data"
    data_dir = os.path.join(cur_path, data_fldr)
    if not os.access(data_dir, os.F_OK):
        os.makedirs(data_dir)

    if not file_path:
        # Download the employment data directly from fred.stlouisfed.org
        # (requires internet connection)
        start_date_mthly = dt.datetime(1939, 1, 1)
        beg_date_mthly = max(beg_date, start_date_mthly)
        usempl_df = pddr.fred.FredReader(
            symbols="PAYEMS", start=beg_date_mthly, end=end_date
        ).read()
        # Convert PAYEMS data (not NA or inf) to millions of persons
        usempl_df.loc[:, "PAYEMS"] = usempl_df["PAYEMS"] * 1_000
        usempl_df = pd.DataFrame(usempl_df).sort_index()  # Sort old to new
        usempl_df = usempl_df.reset_index(level=["DATE"])
        usempl_df = usempl_df.rename(columns={"DATE": "Date"})
        end_date_str2 = usempl_df["Date"].iloc[-1].strftime("%Y-%m-%d")
        end_date2 = dt.datetime.strptime(end_date_str2, "%Y-%m-%d")
        usempl_df["Source"] = "BLS monthly series"
        if beg_date < start_date_mthly:
            # Merge in U.S. annual average nonfarm payroll employment (not
            # seasonally adjusted) 1919-1938. Date values for annual data are
            # set to July 1 of that year. These data are taken from Table 1 on
            # page 1 of "Employment, Hours, and Earnings, United States, 1909-
            # 90, Volume I," Bulletin of the United States Bureau of Labor
            # Statistics, No. 2370, March 1991.
            # <https://fraser.stlouisfed.org/title/employment-earnings-united-
            # states-189/employment-hours-earnings-united-states-1909-90-5435/
            # content/pdf/emp_bmark_1909_1990_v1>
            filename_annual = "usempl_annual_1919-1938.csv"
            ann_data_file_path = os.path.join(data_dir, filename_annual)
            usempl_ann_df = pd.read_csv(
                ann_data_file_path,
                names=["Date", "PAYEMS"],
                parse_dates=["Date"],
                skiprows=1,
                na_values=[".", "na", "NaN"],
            )
            # Convert PAYEMS data to millions of persons
            usempl_ann_df["PAYEMS"] = usempl_ann_df["PAYEMS"] * 1_000
            usempl_ann_df["Source"] = ""
            # Add other months to annual data 1919-01-01 to 1938-12-01 and fill
            # in artificial employment data by cubic spline interpolation
            months_df = pd.DataFrame(
                pd.date_range(beg_date_str, "1938-12-01", freq="MS"),
                columns=["Date"],
            )
            usempl_ann_df = pd.merge(
                usempl_ann_df,
                months_df,
                left_on="Date",
                right_on="Date",
                how="right",
            )
            usempl_df = pd.concat(
                [usempl_ann_df, usempl_df], ignore_index=True
            )
            usempl_df = usempl_df.sort_values(by="Date")
            usempl_df = usempl_df.reset_index(drop=True)
            usempl_df = usempl_df.sort_values(by="Date")
            usempl_df = usempl_df.reset_index(drop=True)
            obs_interp = int(
                (start_date_mthly.year - beg_date.year) * 12
                + start_date_mthly.month
                - beg_date.month
                + 2
            )
            usempl_df_interp = usempl_df.iloc[:obs_interp, :]
            usempl_df_interp.loc[:, "PAYEMS"] = (
                usempl_df["PAYEMS"]
                .iloc[:obs_interp]
                .interpolate(method="cubic")
            )
            usempl_df.loc[: obs_interp - 3, "PAYEMS"] = usempl_df_interp.loc[
                : obs_interp - 3, "PAYEMS"
            ]
            usempl_df.loc[: obs_interp - 3, "Source"] = (
                "Cubic spline interp. of BLS annual data"
            )

            # Drop NaN values at in time series
            # print("Below are the observations that were dropped due to NaN values.")
            # print(usempl_df[usempl_df["PAYEMS"].isna()])
            usempl_df = usempl_df.dropna()
            usempl_df = usempl_df.reset_index(drop=True)

        # Create "BLS_annual" column that only takes the July values between 1919 and 1938
        usempl_df["BLS_annual"] = np.nan
        usempl_df.loc[
            (usempl_df["Date"].dt.month == 7)
            & (usempl_df["Date"].dt.year >= 1919)
            & (usempl_df["Date"].dt.year <= 1938),
            "BLS_annual",
        ] = usempl_df.loc[
            (usempl_df["Date"].dt.month == 7)
            & (usempl_df["Date"].dt.year >= 1919)
            & (usempl_df["Date"].dt.year <= 1938),
            "PAYEMS",
        ]

        usempl_df["diff_monthly"] = usempl_df["PAYEMS"].diff()
        usempl_df["diff_yoy"] = usempl_df["PAYEMS"].diff(12)
        # reorder the columns
        usempl_df = usempl_df[
            [
                "Date",
                "PAYEMS",
                "BLS_annual",
                "diff_monthly",
                "diff_yoy",
                "Source",
            ]
        ]

        filename = "usempl_" + end_date_str2 + ".csv"
        usempl_df.to_csv(os.path.join(data_dir, filename), index=False)
    else:
        # Import the data as pandas DataFrame
        end_date_str2 = end_date_str
        end_date2 = dt.datetime.strptime(end_date_str2, "%Y-%m-%d")
        filename = "usempl_" + end_date_str2 + ".csv"
        data_file_path = os.path.join(data_dir, filename)
        usempl_df = pd.read_csv(
            data_file_path,
            names=["Date", "PAYEMS", "Source"],
            parse_dates=["Date"],
            skiprows=1,
            na_values=[".", "na", "NaN"],
        )
        usempl_df = usempl_df.dropna()

    beg_date_str2 = usempl_df["Date"].iloc[0].strftime("%Y-%m-%d")
    beg_date2 = dt.datetime.strptime(beg_date_str2, "%Y-%m-%d")
    print(
        "Beginning date of U.S. employment series is",
        beg_date2.strftime("%Y-%m-%d"),
    )
    print(
        "End date of U.S. employment series is", end_date2.strftime("%Y-%m-%d")
    )

    return usempl_df, beg_date_str2, end_date_str2


if __name__ == "__main__":
    # execute only if run as a script
    usempl_df, beg_date_str, end_date_str = get_payems_data()
