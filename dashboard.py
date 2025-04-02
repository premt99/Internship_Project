import pandas as pd
import dash
from dash import dcc, html
import plotly.express as px
from dash.dependencies import Input, Output
import os

# ✅ File Path
file_path = "C:/Users/Admin/OneDrive/Desktop/Moringa/Work/Python_dashboard/Khadakpada.csv"

# ✅ Check if the file exists
if not os.path.exists(file_path):
    print(f"❌ Error: File '{file_path}' not found. Check the path.")
    exit()

# ✅ Load dataset
df = pd.read_csv(file_path)

# ✅ Print column names to verify structure
print("🔹 Columns in dataset:", df.columns.tolist())

# ✅ Ensure column names are stripped of spaces
df.columns = df.columns.str.strip()

# ✅ Check for required columns
required_columns = {'Date', 'Time', 'Location'}
missing_columns = required_columns - set(df.columns)
if missing_columns:
    print(f"❌ Missing columns: {missing_columns}. Available columns: {df.columns.tolist()}")
    exit()

# ✅ Convert 'Date' column to datetime format
df['Date'] = pd.to_datetime(df['Date'], format="%d-%m-%Y", errors='coerce')

# ✅ Convert 'Time' to proper format and create 'Datetime' column
df['Datetime'] = pd.to_datetime(df['Date'].astype(str) + ' ' + df['Time'], errors='coerce')

# ✅ Fill missing values (forward fill)
df.ffill(inplace=True)

# ✅ Get unique dropdown values
locations = df['Location'].dropna().unique()
times = df['Time'].dropna().unique()
pollutants = ['PM2.5', 'PM10', 'NO', 'NO2', 'NOx', 'NH3', 'SO2', 'CO', 'Ozone']

# ✅ Initialize Dash app
app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("Air Quality Dashboard", style={'textAlign': 'center'}),

    # Dropdowns
    html.Div([
        html.Label("Select Location:"),
        dcc.Dropdown(id="location-dropdown",
                     options=[{'label': loc, 'value': loc} for loc in locations],
                     value=locations[0] if len(locations) > 0 else None, clearable=False),

        html.Label("Select Time:"),
        dcc.Dropdown(id="time-dropdown",
                     options=[{'label': time, 'value': time} for time in times],
                     value=times[0] if len(times) > 0 else None, clearable=False),

        html.Label("Select Pollutant:"),
        dcc.Dropdown(id="pollutant-dropdown",
                     options=[{'label': p, 'value': p} for p in pollutants],
                     value='PM2.5', clearable=False),

        html.Label("View Type:"),
        dcc.Dropdown(id="view-dropdown",
                     options=[{'label': 'Hourly Trend', 'value': 'hourly'},
                              {'label': 'Daily Trend', 'value': 'daily'}],
                     value='hourly', clearable=False),
    ], style={'width': '50%', 'margin': 'auto'}),

    # Line Chart
    dcc.Graph(id="line-chart")
])

# ✅ Callback for chart update
@app.callback(
    Output("line-chart", "figure"),
    Input("location-dropdown", "value"),
    Input("time-dropdown", "value"),
    Input("pollutant-dropdown", "value"),
    Input("view-dropdown", "value")
)
def update_chart(selected_location, selected_time, selected_pollutant, selected_view):
    filtered_df = df[df['Location'] == selected_location].copy()

    if selected_view == 'hourly':
        filtered_df = filtered_df[filtered_df['Time'] == selected_time]
        title = f"{selected_pollutant} Levels at {selected_location} ({selected_time})"
        x_axis = "Datetime"
    else:
        if 'Date' not in filtered_df.columns:
            return px.line(title="No Data Available")

        filtered_df = filtered_df.groupby('Date')[pollutants].mean().reset_index()
        title = f"Daily Average {selected_pollutant} in {selected_location}"
        x_axis = "Date"

    if selected_pollutant not in filtered_df.columns:
        return px.line(title=f"No data available for {selected_pollutant}")

    fig = px.line(filtered_df, x=x_axis, y=selected_pollutant, markers=True, title=title)

    return fig

# ✅ Run the app
if __name__ == "__main__":
    app.run(debug=True, host='127.0.0.1', port=8050)

