from shiny import reactive, render, req
from shiny.express import ui
import random
from datetime import datetime
from collections import deque
import pandas as pd
import plotly.express as px
from shinywidgets import render_plotly
from scipy import stats
from faicons import icon_svg


UPDATE_INTERVAL_SECS: int = 3
DEQUE_SIZE: int = 5
reactive_value_wrapper = reactive.value(deque(maxlen=DEQUE_SIZE))

@reactive.calc()
def reactive_calc_combined():

    reactive.invalidate_later(UPDATE_INTERVAL_SECS)

    temp = round(random.uniform(-18, -16), 1)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_dictionary_entry = {"temp":temp, "timestamp":timestamp}
    reactive_value_wrapper.get().append(new_dictionary_entry)
    df = pd.DataFrame(reactive_value_wrapper.get())

    return df, new_dictionary_entry

ui.page_opts(title="PyShiny Express: Live Data Example", fillable=True)

with ui.sidebar(open="open"):

    ui.h2("Antarctic Explorer", class_="text-center")
    ui.p(
        "A demonstration of real-time temperature readings in Antarctica.",
        class_="text-center",
    )
    ui.hr()
    ui.h6("Links:")
    ui.a(
        "GitHub Source",
        href="https://github.com/denisecase/cintel-05-cintel",
        target="_blank",
    )
    ui.a(
        "GitHub App",
        href="https://denisecase.github.io/cintel-05-cintel/",
        target="_blank",
    )
    ui.a("PyShiny", href="https://shiny.posit.co/py/", target="_blank")
    ui.a(
        "PyShiny Express",
        href="hhttps://shiny.posit.co/blog/posts/shiny-express/",
        target="_blank",
    )

with ui.layout_columns():
    with ui.value_box(
        showcase=icon_svg("sun"),
        theme="bg-gradient-blue-purple",
    ):

        "Current Temperature"

        @render.text
        def display_temp():
            """Get the latest reading and return a temperature string"""
            df, latest_dictionary_entry = reactive_calc_combined()
            return f"{latest_dictionary_entry['temp']} C"

        "warmer than usual"

    with ui.card(full_screen=True):
        ui.card_header("Current Date and Time")

        @render.text
        def display_time():
            """Get the latest reading and return a timestamp string"""
            df, latest_dictionary_entry = reactive_calc_combined()
            return f"{latest_dictionary_entry['timestamp']}"


#with ui.card(full_screen=True, min_height="40%"):
with ui.card(full_screen=True):
    ui.card_header("Most Recent Readings")

    @render.data_frame
    def display_df():
        """Get the latest reading and return a dataframe with current readings"""
        df, latest_dictionary_entry = reactive_calc_combined()
        pd.set_option('display.width', None)        # Use maximum width
        return render.DataGrid( df,width="100%")

with ui.card():
    ui.card_header(f"Chart with Current Trend")

    @render_plotly
    def display_plot():

        df, latest_dictionary_entry = reactive_calc_combined()
        req(len(df)>1)

        df["timestamp"] = pd.to_datetime(df["timestamp"])

        fig = px.scatter(
            df,
            x="timestamp",
            y="temp",
            title="Temperature Readings with Regression Line",
            labels={"temp": "Temperature (°C)", "timestamp": "Time"},
            color_discrete_sequence=["blue"],
            template = "plotly_white"
        )
            
        x_vals = [*range(len(df))]
        slope, intercept, r_value, p_value, std_err = stats.linregress(x_vals, df['temp'])
        df['best_fit_line'] = [slope * x + intercept for x in x_vals]

        fig.add_scatter(x=df["timestamp"], y=df['best_fit_line'], mode='lines', name='Regression Line', line_color='forestgreen')
        fig.update_layout(xaxis_title="Time",yaxis_title="Temperature (°C)")
        fig.add_annotation(
            text=f'R-sqr: {r_value**2:.5e}',
            xref="paper", yref="paper",
            x=1.122, y=0.9,
            showarrow=False,
            font=dict(size=11, color="black"),
            align="right",
        )

        return fig