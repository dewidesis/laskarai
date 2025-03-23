import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import seaborn as sbn
import plotly.express as px
import plotly.colors
import streamlit as st

# Impor data
hour = pd.read_csv('https://raw.githubusercontent.com/dewidesis/laskarai/refs/heads/main/dashboard/hour_cleaned.csv')
hour['dteday'] = pd.to_datetime(hour['dteday'])

# Membuat fungsi pengelompokkan berdasarkan musim, bulan, dan hari
def create_season_usage_df(hour):
    season_usage_df = hour.groupby('season').agg({
        'casual': 'mean',
        'registered': 'mean',
        'cnt': 'mean'
    })

    season_usage_df = season_usage_df.reset_index()
    season_usage_df.rename(columns = {
        'cnt' : 'avg_rental_bikes',
        'casual' : 'casual_users',
        'registered' : 'registered_users'
    }, inplace = True)

    season_usage_df = pd.melt(season_usage_df,
                              id_vars=['season'],
                              value_vars=['casual_users', 'registered_users'],
                              var_name='users',
                              value_name='avg_rides')
    
    season_usage_df['season'] = pd.Categorical(season_usage_df['season'],
                                               categories= ['Springer', 'Summer', 'Fall', 'Winter'])
    season_usage_df = season_usage_df.sort_values('season')
    return season_usage_df

def create_monthly_usage_df(hour):
    monthly_usage_df = hour.resample(rule = 'M', on = 'dteday').agg({
        'casual' : 'mean',
        'registered' : 'mean',
        'cnt' : 'mean'
    })

    monthly_usage_df.index = monthly_usage_df.index.strftime('%b-%y')
    monthly_usage_df = monthly_usage_df.reset_index()
    monthly_usage_df.rename(columns={
        'dteday' : 'yearmonth',
        'cnt' : 'avg_rental_bikes',
        'casual' : 'casual_users',
        'registered' : 'registered_users'
    }, inplace = True)

    return monthly_usage_df

def create_weekday_usage_df(hour):
    weekday_usage_df = hour.groupby('weekday').agg({
        'casual' : 'mean',
        'registered' : 'mean',
        'cnt' : 'mean'
    })

    weekday_usage_df = weekday_usage_df.reset_index()
    weekday_usage_df.rename(columns = {
        'cnt' : 'avg_rental_bikes',
        'casual' : 'casual_users',
        'registered' : 'registered_users'
    }, inplace = True)

    weekday_usage_df = pd.melt(weekday_usage_df,
                               id_vars = ['weekday'],
                               value_vars = ['casual_users', 'registered_users'],
                               var_name = 'users',
                               value_name= 'avg_rides')
    
    weekday_usage_df['weekday'] = pd.Categorical(weekday_usage_df['weekday'],
                                                 categories=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'])
    
    weekday_usage_df = weekday_usage_df.sort_values('weekday')
    return weekday_usage_df

# Membuat filter tanggal dari kolom "dteday"
start_date = hour['dteday'].min()
end_date = hour['dteday'].max()

# ----- SIDEBAR -----

with st.sidebar:
    # Menambahkan fitur filter pada sidebar
    st.sidebar.header('Filter:')
    # Memasukkan tanggal awal dan akhir dari kolom dteday
    min_date, max_date = st.date_input(
        label= 'Time Period', min_value= start_date,
        max_value= end_date,
        value= [start_date, end_date]
    )

# Menghubungkan filter dengan dteday
date_day = hour[
    (hour['dteday'] >= str(min_date)) &
    (hour['dteday'] <= str(max_date))
    ]

# Menetapkan date_day ke fungsi yang telah dibuat
season_usage_df = create_season_usage_df(date_day)
monthly_usage_df = create_monthly_usage_df(date_day)
weekday_usage_df = create_weekday_usage_df(date_day)

# ----- MAINPAGE -----

st.title('Bike Sharing Dashboard')
st.markdown('##')

col1, col2, col3 = st.columns(3)
with col1:
    avg_rental_bikes = date_day['cnt'].mean()
    st.metric('Average Rental Bikes', value = avg_rental_bikes)
with col2:
    avg_casual_users = date_day['casual'].mean()
    st.metric('Average Casual Users', value = avg_casual_users)
with col3:
    avg_registered_users = date_day['registered'].mean()
    st.metric('Average Registered Users', value = avg_registered_users)
st.markdown('---')

# ----- CHART -----

pastel_colors = plotly.colors.qualitative.Pastel

fig1 = px.bar(season_usage_df,
              x = 'season',
              y = ['avg_rides'],
              color = 'users',
              color_discrete_sequence = pastel_colors,
              title = 'Rata-Rata Sewa Sepeda Per Musim').update_layout(xaxis_title = '', yaxis_title = 'Rata-Rata Rental Bikes')
st.plotly_chart(fig1, use_container_width = True)

fig2 = px.line(monthly_usage_df,
               x = 'yearmonth',
               y = ['casual_users', 'registered_users', 'avg_rental_bikes'],
               color_discrete_sequence = pastel_colors,
               markers = True,
               title = 'Rata-Rata Sewa Sepeda Per Bulan').update_layout(xaxis_title = '', yaxis_title = 'Rata-Rata Rental Bikes')
st.plotly_chart(fig2, use_container_width = True)

fig3 = px.bar(weekday_usage_df,
              x = 'weekday',
              y = ['avg_rides'],
              color = 'users',
              color_discrete_sequence = pastel_colors,
              title = 'Rata-Rata Sewa Sepeda Per Hari').update_layout(xaxis_title = '', yaxis_title = 'Rata-Rata Rental Bikes')
st.plotly_chart(fig3, use_container_width = True)

# ----- HIDE STREAMLIT STYLE -----

hide_st_style = """
                <style>
                #MainMenu {visibility: hidden;}
                footer {visibility: hidden;}
                header {visibility: hidden;}
                </style>
                """
st.markdown(hide_st_style, unsafe_allow_html=True)