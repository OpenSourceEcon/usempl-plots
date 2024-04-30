"""
This module plots the streaks of consecutive positive employment gains from the
US nonfarm employment (PAYEMS) seasonally adjusted monthly time series from the
St. Louis Federal Reserve's FRED system
(https://fred.stlouisfed.org/series/PAYEMS) or loads it from this directory and
organizes it into series of consecutive positive monthly gain streaks.

This module defines the following function(s):
    usempl_streaks()
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


def usempl_streaks(
    start_date="min",
    end_date="max",
    download_from_internet=True,
    fig_title_strk=(
        "US employment streaks: consecutive positive monthly gains and " +
        "cumulative employment gains, 1939 to 2024"
    ),
    scatter_histogram=True,
    table_output=True,
    html_show=True,
):
    """
    This function creates the HTML and JavaScript code for the dynamic
    visualization of the US positive employment streaks from 1939 (the
    beginning of US monthly data) to the given end date.

    Args:
        start_date (str): start date of PAYEMS time series in 'YYYY-mm-dd'
            format or 'min'
    """
    # Create data and images directory paths
    cur_path = os.path.split(os.path.abspath(__file__))[0]
    image_dir = os.path.join(cur_path, "images")
    data_dir = os.path.join(cur_path, "data")

    # Get the employment data
    if start_date == "min":
        beg_date_str = "1939-01-01"
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
    if download_from_internet:
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

    strk_df_lst = []
    strk_cds_lst = []
    strk_label_lst = []
    min_gain_val_lst = []
    max_gain_val_lst = []
    min_cum_val_lst = []
    max_cum_val_lst = []
    min_mth_val_lst = []
    max_mth_val_lst = []
    strk_num = 0
    strk_mths = 0
    strk_cum = 0
    strk_table_df = pd.DataFrame(
        columns=[
            "strk_num",
            "start_date",
            "end_date",
            "months_in_streak",
            "total_emp_gain",
            "avg_monthly_emp_gain",
        ]
    )
    for i in range(usempl_df.shape[0]):
        if usempl_df.loc[i, "diff_monthly"] > 0:
            if strk_mths == 0:
                j = i
                strk_num += 1
                strk_df = pd.DataFrame(
                    columns=[
                        "Date",
                        "PAYEMS",
                        "diff_monthly",
                        "strk_mths",
                        "strk_cum",
                        "strk_mths_tot",
                        "strk_avg_emp_gain",
                        "strk_cum_tot",
                    ]
                )
                strk_start_mth_str = usempl_df.loc[i, "Date"].strftime("%Y-%m")
            strk_df.loc[i - j, ["Date", "PAYEMS", "diff_monthly"]] = (
                usempl_df.loc[i, ["Date", "PAYEMS", "diff_monthly"]]
            )
            strk_mths += 1
            strk_df.loc[i - j, "strk_mths"] = strk_mths
            strk_cum += usempl_df.loc[i, "diff_monthly"]
            strk_df.loc[i - j, "strk_cum"] = strk_cum
            if i == usempl_df.shape[0] - 1:
                strk_end_mth_str = usempl_df.loc[i, "Date"].strftime("%Y-%m")
                strk_label = strk_start_mth_str + " to " + strk_end_mth_str
                strk_label_lst.append(strk_label)
                strk_df["strk_mths_tot"] = strk_mths
                strk_df["strk_avg_emp_gain"] = strk_cum / strk_mths
                strk_df["strk_cum_tot"] = strk_cum
                strk_df_lst.append(strk_df)
                strk_cds_lst.append(ColumnDataSource(strk_df))
                min_gain_val_lst.append(strk_df["diff_monthly"].min())
                max_gain_val_lst.append(strk_df["diff_monthly"].max())
                min_cum_val_lst.append(strk_df["strk_cum"].min())
                max_cum_val_lst.append(strk_df["strk_cum"].max())
                min_mth_val_lst.append(strk_df["strk_mths"].min())
                max_mth_val_lst.append(strk_df["strk_mths"].max())
                strk_table_df.loc[strk_num - 1] = [
                    strk_num, strk_start_mth_str, strk_end_mth_str, strk_mths,
                    strk_cum, strk_cum / strk_mths
                ]
        elif (
            usempl_df.loc[i, "diff_monthly"] <= 0
            and usempl_df.loc[i - 1, "diff_monthly"] > 0
            and i > 0
        ):
            strk_df["strk_mths_tot"] = strk_mths
            strk_df["strk_avg_emp_gain"] = strk_cum / strk_mths
            strk_df["strk_cum_tot"] = strk_cum
            strk_end_mth_str = usempl_df.loc[i - 1, "Date"].strftime("%Y-%m")
            strk_label = strk_start_mth_str + " to " + strk_end_mth_str
            strk_label_lst.append(strk_label)
            strk_df_lst.append(strk_df)
            strk_cds_lst.append(ColumnDataSource(strk_df))
            min_gain_val_lst.append(strk_df["diff_monthly"].min())
            max_gain_val_lst.append(strk_df["diff_monthly"].max())
            min_cum_val_lst.append(strk_df["strk_cum"].min())
            max_cum_val_lst.append(strk_df["strk_cum"].max())
            min_mth_val_lst.append(strk_df["strk_mths"].min())
            max_mth_val_lst.append(strk_df["strk_mths"].max())
            strk_table_df.loc[strk_num - 1] = [
                strk_num, strk_start_mth_str, strk_end_mth_str, strk_mths,
                strk_cum, strk_cum / strk_mths
            ]
            strk_mths = 0
            strk_cum = 0

    print("Number of streaks:", strk_num)

    # Create Bokeh plot of PAYEMS normalized peak plot figure
    filename_strk = "usempl_streaks_" + end_date_str2 + ".html"
    output_file(
        os.path.join(image_dir, filename_strk),
        title=fig_title_strk,
        mode='inline'
    )

    # Format the tooltip
    tooltips = [
        ("Date", "@Date{%F}"),
        ("Current month in streak", "@strk_mths{0.}"),
        ("Total months in streak", "@strk_mths_tot{0.}"),
        ("Monthly employment gain", "@diff_monthly{0,0.}"),
        ("Cumulative employment gain", "@strk_cum{0,0.}"),
        ("Total cumulative employment gain", "@strk_cum_tot{0,0.}"),
        ("Avg. monthly employment gain", "@strk_avg_emp_gain{0,0.}"),
    ]

    # Solve for minimum and maximum PAYEMS/Peak values in monthly main display
    # window in order to set the appropriate xrange and yrange
    min_cum_val = min(min_cum_val_lst)
    max_cum_val = max(max_cum_val_lst)
    min_mth_val = min(min_mth_val_lst)
    max_mth_val = max(max_mth_val_lst)

    datarange_cum_vals = max_cum_val - min_cum_val
    datarange_mth_vals = int(min_mth_val + max_mth_val)
    fig_buffer_pct = 0.05
    fig_strk = figure(
        height=500,
        width=800,
        x_axis_label="Streak length (months)",
        y_axis_label="Cumulative employment gains (millions)",
        y_range=(
            min_cum_val - fig_buffer_pct * datarange_cum_vals,
            max_cum_val + fig_buffer_pct * datarange_cum_vals,
        ),
        y_minor_ticks=5,
        x_range=(
            (min_mth_val - fig_buffer_pct * datarange_mth_vals),
            (max_mth_val + fig_buffer_pct * datarange_mth_vals),
        ),
        tools=[
            "save",
            "zoom_in",
            "zoom_out",
            "box_zoom",
            "pan",
            "undo",
            "redo",
            "reset",
            "hover",
            "help",
        ],
        toolbar_location="left",
    )
    fig_strk.toolbar.logo = None

    # Set title font size and axes font sizes
    fig_strk.xaxis.axis_label_text_font_size = "12pt"
    fig_strk.xaxis.major_label_text_font_size = "12pt"
    fig_strk.yaxis.axis_label_text_font_size = "12pt"
    fig_strk.yaxis.major_label_text_font_size = "12pt"

    # Reformat the labels for the ticks on the x and y axes
    y_tick_label_dict_strk = {
        0: "0", 5_000_000: "5m", 10_000_000: "10m", 15_000_000: "15m",
        20_000_000: "20m"
    }

    fig_strk.yaxis.major_label_overrides = y_tick_label_dict_strk

    fig_lst_strk = []
    label_items_strk_lst = []
    j = -1
    for i in range(strk_num):
        if max_cum_val_lst[i] > 10_000_000 or max_mth_val_lst[i] > 40:
            j += 1
            li = fig_strk.line(
                x="strk_mths",
                y="strk_cum",
                source=strk_cds_lst[i],
                color=Viridis8[7 - j],
                # color=Plasma256[255 - int(i * (256 - 1) / (strk_num - 1))],
                line_width=4,
                alpha=0.7,
                muted_alpha=0.15,
            )
            label_items_strk_lst.append((strk_label_lst[i], [li]))
        else:
            li = fig_strk.line(
                x="strk_mths",
                y="strk_cum",
                source=strk_cds_lst[i],
                color="orange",
                line_width=2,
                alpha=0.7,
                muted_alpha=0.15,
            )
        fig_lst_strk.append(li)

    # Add legend
    legend = Legend(items=label_items_strk_lst, location="center")
    fig_strk.add_layout(legend, "right")
    fig_strk.legend.click_policy = "mute"

    # Add title and subtitle to the plot
    fig_strk.add_layout(
        Title(
            text=fig_title_strk,
            text_font_style="bold",
            text_font_size="11pt",
            align="center",
        ),
        "above",
    )

    # Add source text below figure
    updated_date_str = (
        download_date.strftime("%B") +
        " " +
        download_date.strftime("%d").lstrip("0") +
        ", " +
        download_date.strftime("%Y")
    )
    note_text_list = [
        (
            "Source: Richard W. Evans (@RickEcon), historical PAYEMS data " +
            "from FRED and BLS, updated "
        ),
        ("    " + updated_date_str + ".")
    ]
    for note_text in note_text_list:
        caption = Title(text=note_text, align='left', text_font_size='4mm',
                        text_font_style='italic')
        fig_strk.add_layout(caption, 'below')

    # Add the HoverTool to the figure
    fig_strk.add_tools(
        HoverTool(
            tooltips=tooltips,
            visible=False,
            formatters={"@Date": "datetime"},
        )
    )

    if table_output:
        print("")
        print("Print a table of streaks with +40 months or +10,000,000 jobs.")
        print("")
        print(
            strk_table_df[
                (
                    (strk_table_df["months_in_streak"] >= 40) |
                    (strk_table_df["total_emp_gain"] >= 10_000_000)
                )
            ].sort_values(by="months_in_streak", ascending=False)
        )

    if html_show:
        show(fig_strk)

    fig_lst = [fig_strk]

    if scatter_histogram:
        fig_title_scat=(
            "US employment streaks: consecutive positive monthly gains and " +
            "average monthly employment gains, 1939 to 2024"
        )
        filename_scat = "usempl_streaks_scatter" + end_date_str2 + ".html"
        output_file(
            os.path.join(image_dir, filename_scat),
            title=fig_title_scat,
            mode='inline'
        )

        # Format the tooltip
        tooltips_scat = [
            ("Start date", "@start_date{%F}"),
            ("End date", "@end_date{%F}"),
            ("Months in streak", "@months_in_streak{0.}"),
            ("Total employment gain", "@total_emp_gain{0,0.}"),
            ("Avg. monthly employment gain", "@avg_monthly_emp_gain{0,0.}"),
        ]

        min_avg_val = strk_table_df["avg_monthly_emp_gain"].min()
        max_avg_val = strk_table_df["avg_monthly_emp_gain"].max()

        strk_table_cds = ColumnDataSource(strk_table_df)
        datarange_avgmth_vals = max_avg_val - min_avg_val
        fig_scat = figure(
            height=500,
            width=700,
            x_axis_label="Streak length (months)",
            y_axis_label="Avg. monthly employment gains (thousands)",
            x_minor_ticks=4,
            y_range=(
                min_avg_val - fig_buffer_pct * datarange_avgmth_vals,
                max_avg_val + fig_buffer_pct * datarange_avgmth_vals,
            ),
            y_minor_ticks=5,
            x_range=(
                (min_mth_val - fig_buffer_pct * datarange_mth_vals),
                121,
                # (max_mth_val + fig_buffer_pct * datarange_mth_vals),
            ),
            tools=[
                "save",
                "zoom_in",
                "zoom_out",
                "box_zoom",
                "pan",
                "undo",
                "redo",
                "reset",
                "hover",
                "help",
            ],
            toolbar_location="left",
        )
        fig_scat.toolbar.logo = None

        # Set title font size and axes font sizes
        fig_scat.xaxis.axis_label_text_font_size = "12pt"
        fig_scat.xaxis.major_label_text_font_size = "12pt"
        fig_scat.yaxis.axis_label_text_font_size = "12pt"
        fig_scat.yaxis.major_label_text_font_size = "12pt"

        # Reformat the labels for the ticks on the x and y axes
        y_tick_label_dict_scat = {
            0: "0", 500_000: "500k", 1_000_000: "1.0m", 1_500_000: "1.5m",
            2_000_000: "2.0m"
        }

        fig_scat.yaxis.major_label_overrides = y_tick_label_dict_scat

        scat = fig_scat.scatter(
            x="months_in_streak",
            y="avg_monthly_emp_gain",
            source=strk_table_cds,
            size=8,
            line_width=1,
            line_color='black',
            fill_color="blue",
            alpha=0.6,
        )

        # Add title and subtitle to the plot
        fig_scat.add_layout(
            Title(
                text=fig_title_scat,
                text_font_style="bold",
                text_font_size="14pt",
                align="center",
            ),
            "above",
        )

        # Add the HoverTool to the figure
        fig_scat.add_tools(
            HoverTool(
                tooltips=tooltips_scat,
                visible=False,
                formatters={"@Start date": "datetime", "@End date": "datetime"},
            )
        )

        # create the horizontal histogram
        hhist, hedges = np.histogram(
            strk_table_df["months_in_streak"], bins=24, range=(0, 120)
        )
        hzeros = np.zeros(len(hedges)-1)
        hmax = max(hhist)*1.15

        LINE_ARGS = dict(color="#3A5785", line_color=None)

        xhist = figure(
            toolbar_location=None,
            width=fig_scat.width,
            height=200,
            x_range=fig_scat.x_range,
            x_minor_ticks=4,
            y_range=(-3, hmax),
            y_minor_ticks=2,
            min_border=10,
            min_border_left=50,
            y_axis_location="right"
        )
        xhist.toolbar.logo = None
        xhist.xgrid.grid_line_color = None
        # xhist.yaxis.major_label_orientation = np.pi/4
        xhist.background_fill_color = "#fafafa"

        # Set title font size and axes font sizes
        xhist.xaxis.axis_label_text_font_size = "12pt"
        xhist.xaxis.major_label_text_font_size = "12pt"
        xhist.yaxis.axis_label_text_font_size = "10pt"
        xhist.yaxis.major_label_text_font_size = "10pt"

        xhist.quad(
            bottom=0, left=hedges[:-1], right=hedges[1:], top=hhist,
            color="blue", line_color="black"
        )
        hh1 = xhist.quad(
            bottom=0, left=hedges[:-1], right=hedges[1:], top=hzeros,
            alpha=0.5, **LINE_ARGS
        )
        hh2 = xhist.quad(
            bottom=0, left=hedges[:-1], right=hedges[1:], top=hzeros,
            alpha=0.1, **LINE_ARGS
        )

        # Create x-histogram labels
        xhist_label_source = ColumnDataSource(
            dict(
                bin_midpoints=(hedges[1:]-2.5).tolist(),
                bin_heights=hhist.tolist()
            )
        )

        xhist_labels = LabelSet(
            x='bin_midpoints', y='bin_heights', text='bin_heights',
            level='glyph', text_align='center', text_font_size="8pt",
            y_offset=3, source=xhist_label_source
        )
        xhist.add_layout(xhist_labels)

        # create the vertical histogram
        vhist, vedges = np.histogram(
            strk_table_df["avg_monthly_emp_gain"], bins=18,
            range=(0, 1_800_000)
        )
        vzeros = np.zeros(len(vedges)-1)
        vmax = max(vhist)*1.2

        yhist = figure(
            toolbar_location=None,
            width=200,
            height=fig_scat.height,
            x_range=(-2, vmax),
            x_minor_ticks=2,
            y_range=fig_scat.y_range,
            y_minor_ticks=5,
            min_border=10,
            y_axis_location="right"
        )
        yhist.toolbar.logo = None
        yhist.ygrid.grid_line_color = None
        # yhist.xaxis.major_label_orientation = np.pi/4
        yhist.background_fill_color = "#fafafa"

        # Set title font size and axes font sizes
        yhist.xaxis.axis_label_text_font_size = "10pt"
        yhist.xaxis.major_label_text_font_size = "10pt"
        yhist.yaxis.axis_label_text_font_size = "12pt"
        yhist.yaxis.major_label_text_font_size = "12pt"

        # Reformat the labels for the ticks on the x and y axes
        yhist.yaxis.major_label_overrides = y_tick_label_dict_scat

        yhist.quad(
            left=0, bottom=vedges[:-1], top=vedges[1:], right=vhist,
            color="blue", line_color="black"
        )
        vh1 = yhist.quad(
            left=0, bottom=vedges[:-1], top=vedges[1:], right=vzeros,
            alpha=0.5, **LINE_ARGS
        )
        vh2 = yhist.quad(
            left=0, bottom=vedges[:-1], top=vedges[1:], right=vzeros,
            alpha=0.1, **LINE_ARGS
        )

        # Create y-histogram labels
        yhist_label_source = ColumnDataSource(
            dict(
                bin_midpoints=(vedges[1:]-60_000).tolist(),
                bin_heights=vhist.tolist()
            )
        )

        yhist_labels = LabelSet(
            x='bin_heights', y='bin_midpoints', text='bin_heights',
            level='glyph', text_align='left', text_font_size="8pt",
            x_offset=3, source=yhist_label_source
        )
        yhist.add_layout(yhist_labels)

        layout = gridplot(
            [[fig_scat, yhist], [xhist, None]], merge_tools=False
        )
        layout.toolbar.logo = None

        # Add notes below image. The list note_text_list contains a tuple with
        # a string for every line of the notes
        updated_date_str = (
            download_date.strftime("%B") +
            " " +
            download_date.strftime("%d").lstrip("0") +
            ", " +
            download_date.strftime("%Y")
        )
        note_text_list = [
            (
                "Source: Richard W. Evans (@RickEcon), historical PAYEMS " +
                "data from FRED and BLS,"
            ),
            ("    updated " + updated_date_str + ".")
        ]
        for note_text in note_text_list:
            caption = Title(text=note_text, align='left', text_font_size='4mm',
                            text_font_style='italic')
            xhist.add_layout(caption, 'below')

        # show(fig_scat)
        show(layout)

        # fig_lst.append(fig_scat)
        fig_lst.append(layout)

    return fig_lst, beg_date_str2, end_date_str2


# def usempl_streaks_hist():

#     return fig, beg_date_str2, end_date_str2


if __name__ == "__main__":
    # execute only if run as a script
    fig_lst, beg_date_str, end_date_str = usempl_streaks()
