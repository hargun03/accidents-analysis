import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import plotly.express as px

DATA_URL = (
"Motor_Vehicle_Collisions.csv"
)

st.title("Motor Vehicle Collisions in New York")
st.markdown("This application is a streamlit dashboard that can be used to analyse motor vehicle collisions in NYC")

@st.cache_data(persist=True)
def load_data(nrows):
    data = pd.read_csv(DATA_URL, nrows=nrows, parse_dates=[['CRASH DATE','CRASH TIME']])
    data.dropna(subset = ['LATITUDE','LONGITUDE'], inplace = True)
    lowercase = lambda x: str(x).lower()
    data.rename(lowercase, axis = 'columns', inplace = True)
    # data.rename(columns = {'crash dat time': 'crash_time'},inplace = True)
    data.rename(columns = {'number of persons injured': 'number_of_persons_injured'},inplace = True)
    return data

data = load_data(100000)
original_data = data

st.header("Where are the most poeple injured in NYC?")
injured_people = st.slider("NUmber of persons injured in collisions", 0, 19)
st.map(data.query("number_of_persons_injured >= @injured_people")[["latitude", "longitude"]].dropna(how="any"))

st.header("How many collisions occur during a given time of day")
hour = st.slider("Hour to look at",0,23)
data = data[data['crash date_crash time'].dt.hour == hour]

st.markdown("Vehicle collisions between %i:00 and %i:00" % (hour,(hour+1)%24 ))
if not data.empty:
    midpoint = (np.average(data['latitude']), np.average(data['longitude']))
else:
    midpoint = (40.7128, -74.0060)  # Default to NYC coordinates if no data

# midpoint = (np.average(data['latitude']),np.average(data['longitude']))
st.write(pdk.Deck(
    map_style = "mapbox://styles/mapbox/light-v9",
    initial_view_state = {
        "latitude":midpoint[0],
        "longitude":midpoint[1],
        "zoom":11,
        "pitch": 50,
    }, 
    layers = [
        pdk.Layer(
            "HexagonLayer",
            data = data[['crash date_crash time','latitude','longitude']],
            get_position = ['longitude','latitude'],
            radius = 100,
            extruded = True,  
            pickable = True,
            elevation_scale = 4,
            elevation_range = [0,1000],
        ),
    ],
))

st.subheader("Breakdown by minute between %i:00 and %i:00" % (hour, (hour+1)%24))
filtered = data[
    (data['crash date_crash time'].dt.hour >= hour & (data['crash date_crash time'].dt.hour < (hour+1)))
]
hist = np.histogram(filtered['crash date_crash time'].dt.minute, bins = 60, range = (0,60))[0]
chart_data = pd.DataFrame({'minute': range(60), 'crashes': hist})
fig = px.bar(chart_data, x = 'minute', y = 'crashes', hover_data = ['minute', 'crashes'], height = 400)
st.write(fig)

st.header("Top 5 dangerous streets by affected type")
select = st.selectbox('Affected type of people' , ['Pedestrians', 'Cyclists', 'Motorists'])

original_data.rename(columns = {'number of pedestrians injured': 'injured_pedestrians'},inplace = True)
original_data.rename(columns = {'number of cyclist injured': 'injured_cyclists'},inplace = True)
original_data.rename(columns = {'number of motorist injured': 'injured_motorists'},inplace = True)


if select == 'Pedestrians':
    st.write(original_data.query("injured_pedestrians >= 1")[["on street name","injured_pedestrians"]].sort_values(by=['injured_pedestrians'], ascending = False).dropna(how='any')[:5])
if select == 'Cyclists':
    st.write(original_data.query("injured_cyclists >= 1")[["on street name","injured_cyclists"]].sort_values(by=['injured_cyclists'], ascending = False).dropna(how='any')[:5])
if select == 'Motorists':
    st.write(original_data.query("injured_motorists >= 1")[["on street name","injured_motorists"]].sort_values(by=['injured_motorists'], ascending = False).dropna(how='any')[:5])




if st.checkbox("Show raw data", False):
    st.subheader('Raw data')
    st.write(data)


