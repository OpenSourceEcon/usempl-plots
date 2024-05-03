# Import packages
import numpy as np
import pandas as pd
import datetime as dt
import os
from usempl_plots.get_payems import get_payems_data

from bokeh.core.property.numeric import Interval
from bokeh.models.annotations import Label, LabelSet
from bokeh.models.glyphs import VArea
from bokeh.models.tickers import SingleIntervalTicker
from bokeh.io import output_file
from bokeh.plotting import figure, show
from bokeh.models import (
    ColumnDataSource,
    Title,
    Legend,
    HoverTool,
    NumeralTickFormatter,
)

"""
-------------------------------------------------------------------------------
Create pandas DataFrames and Column Data Source data objects
-------------------------------------------------------------------------------
"""


def gen_payems_tseries(
    start_date="min",
    end_date="max",
    recession_bars=True,
    download=True,
    fig_title_str=(
        "Time Series of US Monthly Nonfarm Payroll Employment (PAYEMS)"
    ),
    html_show=True,
):
    """
    This function creates a simple time series plot of US nonfarm payroll
    employment (PAYEMS).

    Args:
        start_date (str): start date of PAYEMS time series in 'YYYY-mm-dd'
            format or 'min'
    """
    # Create data and images directory as well as recession data path
    cur_path = os.path.split(os.path.abspath(__file__))[0]
    image_dir = os.path.join(cur_path, "images")
    data_dir = os.path.join(cur_path, "data")
    recession_data_path = os.path.join(data_dir, "recession_data.csv")

    # Get the employment data
    if start_date == "min":
        beg_date_str = "1919-01-01"
    else:
        try:
            beg_date_test = dt.datetime.strptime(start_date, "%Y-%m-%d")
        except:
            err_msg = (
                "Error get_payems.py: start_date input must be either a "
                + "date string in 'YYYY-mm-dd' format or 'min'."
            )
            raise ValueError(err_msg)
        beg_date_str = start_date

    if end_date == "max":
        end_date_str = "today"
    else:
        try:
            end_date_test = dt.datetime.strptime(end_date, "%Y-%m-%d")
        except:
            err_msg = (
                "Error get_payems.py: end_date input must be either a "
                + "date string in 'YYYY-mm-dd' format or 'max'."
            )
            raise ValueError(err_msg)
        end_date_str = end_date

    if end_date_str == "today":
        download_date = dt.datetime.today()
    else:
        download_date = dt.datetime.strptime(end_date_str, "%Y-%m-%d")
    download_date_str = download_date.strftime("%Y-%m-%d")
    if download:
        usempl_df, beg_date_str2, end_date_str2 = get_payems_data(
            beg_date_str=beg_date_str,
            end_date_str=end_date_str,
            file_path=None,
        )
        print(
            "PAYEMS data downloaded on "
            + download_date_str
            + " and has most recent PAYEMS data month of "
            + end_date_str2
            + "."
        )
    else:
        usempl_df, beg_date_str2, end_date_str2 = get_payems_data(
            beg_date_str=beg_date_str,
            end_date_str=end_date_str,
            file_path=os.path.join(
                data_dir, "usempl_" + end_date_str + ".csv"
            ),
        )
        print(
            "PAYEMS data loaded from memory on "
            + download_date_str
            + " and has most recent PAYEMS data month of "
            + end_date_str2
            + "."
        )

    # Create a dataframe that only contains dates less than 1939-01-01
    usempl_imputed_df = usempl_df[usempl_df["Date"] < "1939-01-01"]
    usempl_monthly_df = usempl_df[usempl_df["Date"] >= "1939-01-01"]
    # Create a dataframe usempl_annual_df that only contains data from before
    # 1939 and only for month 7
    usempl_annual_df = usempl_imputed_df[
        usempl_imputed_df["Date"].dt.month == 7
    ]
    usempl_imputed_cds = ColumnDataSource(usempl_imputed_df)
    usempl_annual_cds = ColumnDataSource(usempl_annual_df)
    usempl_monthly_cds = ColumnDataSource(usempl_monthly_df)
    # print(usempl_monthly_df.keys())
    # print(usempl_annual_df.keys())
    # print(usempl_imputed_df.keys())
    # print(usempl_annual_df[['Date', 'PAYEMS', 'BLS_annual']])

    # Create recession data column data source object
    recession_df = pd.read_csv(
        recession_data_path, parse_dates=["Peak", "Trough"]
    )
    recession_data_length = len(recession_df["Peak"])

    # Create Bokeh plot of PAYEMS time series
    fig_title = fig_title_str
    filename = "tseries_payems_" + end_date_str2 + ".html"
    output_file(
        os.path.join(image_dir, filename), title=fig_title, mode="inline"
    )

    # Format the tooltip
    tooltips = [
        ("Date", "@Date{%F}"),
        ("Employed", "@PAYEMS{0,0.}"),
        ("Change from prev. month", "@diff_monthly{0,0.}"),
        ("Change from prev. year", "@diff_yoy{0,0.}"),
    ]

    min_date = usempl_df["Date"].min()
    max_date = usempl_df["Date"].max()
    min_y_val = usempl_df["PAYEMS"].min()
    max_y_val = usempl_df["PAYEMS"].max()
    range_y_vals = max_y_val - min_y_val
    fig_buffer_pct = 0.10
    fig = figure(
        height=400,
        width=800,
        x_axis_label="Date (monthly)",
        y_axis_label="Employment (millions)",
        y_range=(
            min_y_val - fig_buffer_pct * range_y_vals,
            max_y_val + fig_buffer_pct * range_y_vals,
        ),
        y_minor_ticks=2,
        x_range=(min_date, max_date),
        x_minor_ticks=2,
        tools=[
            "save",
            "zoom_in",
            "zoom_out",
            "box_zoom",
            "pan",
            "undo",
            "redo",
            "reset",
            "help",
        ],
        toolbar_location="left",
    )
    fig.toolbar.logo = None

    # Set title font size and axes font sizes
    fig.xaxis.axis_label_text_font_size = "12pt"
    fig.xaxis.major_label_text_font_size = "12pt"
    fig.yaxis.axis_label_text_font_size = "12pt"
    fig.yaxis.major_label_text_font_size = "12pt"

    # Reformat the labels for the ticks on the x and y axes
    y_tick_label_dict = {
        20_000_000: "20m",
        40_000_000: "40m",
        60_000_000: "60m",
        80_000_000: "80m",
        100_000_000: "100m",
        120_000_000: "120m",
        140_000_000: "140m",
        160_000_000: "160m",
    }

    fig.yaxis.major_label_overrides = y_tick_label_dict

    monthly = fig.line(
        x="Date",
        y="PAYEMS",
        source=usempl_monthly_cds,
        color="blue",
        line_dash="solid",
        line_width=3,
        alpha=0.7,
        muted_alpha=0.1,
        legend_label="Monthly data",
    )

    imputed = fig.line(
        x="Date",
        y="PAYEMS",
        source=usempl_imputed_cds,
        color="red",
        line_dash="solid",
        line_width=3,
        alpha=0.7,
        muted_alpha=0.1,
        legend_label="Interpolated from annual data",
    )

    annual = fig.scatter(
        x="Date",
        y="PAYEMS",
        source=usempl_annual_cds,
        size=2,
        line_width=1,
        line_color="black",
        fill_color="purple",
        alpha=0.7,
        muted_alpha=0.1,
        legend_label="Annual data points",
    )

    if recession_bars:
        # Create recession bars
        for x in range(0, recession_data_length):
            peak_date = recession_df["Peak"][x]
            trough_date = recession_df["Trough"][x]
            if peak_date >= min_date and trough_date >= min_date:
                fig.patch(
                    x=[peak_date, trough_date, trough_date, peak_date],
                    y=[
                        -10_000_000,
                        -10_000_000,
                        max_y_val + 100_000_000,
                        max_y_val + 100_000_000,
                    ],
                    fill_color="gray",
                    fill_alpha=0.4,
                    line_width=0,
                    legend_label="Recession",
                )
            if (
                peak_date == trough_date
                and peak_date >= min_date
                and trough_date >= min_date
            ):
                fig.patch(
                    x=[peak_date, trough_date, trough_date, peak_date],
                    y=[
                        -10_000_000,
                        -10_000_000,
                        max_y_val + 100_000_000,
                        max_y_val + 100_000_000,
                    ],
                    fill_color="gray",
                    fill_alpha=0.4,
                    line_width=0,
                    legend_label="Recession",
                )

    hover = HoverTool(
        tooltips=tooltips,
        visible=False,
        formatters={"@Date": "datetime"},
    )
    hover.renderers = [monthly, imputed]

    # Add the HoverTool to the figure
    fig.add_tools(hover)

    # Add legend
    fig.legend.location = "top_left"
    fig.legend.border_line_width = 2
    fig.legend.border_line_color = "black"
    fig.legend.border_line_alpha = 1
    fig.legend.label_text_font_size = "4mm"

    # Set legend muting click policy
    fig.legend.click_policy = "mute"

    # Add title
    fig.add_layout(
        Title(
            text=fig_title_str,
            text_font_style="bold",
            text_font_size="15pt",
            align="center",
        ),
        "above",
    )

    # Add notes below image. The list note_text_list contains a tuple with a
    # string for every line of the notes
    updated_date_str = (
        download_date.strftime("%B")
        + " "
        + download_date.strftime("%d").lstrip("0")
        + ", "
        + download_date.strftime("%Y")
    )
    note_text_list = [
        (
            "Source: Richard W. Evans (@RickEcon), historical PAYEMS data "
            + "from FRED and BLS, updated "
        ),
        ("   " + updated_date_str + "."),
    ]
    for note_text in note_text_list:
        caption = Title(
            text=note_text,
            align="left",
            text_font_size="4mm",
            text_font_style="italic",
        )
        fig.add_layout(caption, "below")

    if html_show:
        show(fig)

    return fig, beg_date_str2, end_date_str2


if __name__ == "__main__":
    # execute only if run as a script
    fig, beg_date_str, end_date_str = gen_payems_tseries()
