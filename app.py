import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import plotly.express as px

st.title("Анализ температуры")
uplfile=st.file_uploader("Загрузи CSV файл")
if uplfile:
    df=pd.read_csv(uplfile)
    df['timestamp']=pd.to_datetime(df['timestamp'])
    st.write("Данные:")
    st.write(df.head())
    city=st.selectbox("Выбери город", df['city'].unique())
    
    df=df.sort_values(['city','timestamp'])
    df['mean']=df.groupby('city')['temperature'].transform(lambda x: x.rolling(30, min_periods=1).mean())
    df['std']=df.groupby('city')['temperature'].transform(lambda x: x.rolling(30, min_periods=1).std())
    df['anomal']=((df['temperature']>df['mean']+2*df['std'])|(df['temperature']<df['mean']-2*df['std']))
    dfc=df[df['city']==city]
    
    st.subheader("Статистика")
    st.write(dfc['temperature'].describe())
    
    st.subheader("График температуры")
    dfc['type']=dfc['anomal'].apply(lambda x: 'Аномалия' if x else 'Норма')
    fig=px.line(dfc,x='timestamp',y='temperature',title='Температура')
    an=dfc[dfc['anomal']]
    fig.add_scatter(x=an['timestamp'],y=an['temperature'],mode='markers',name='Аномалии')
    st.plotly_chart(fig)

    season=df.groupby(['city','season'])['temperature'].agg(['mean','std']).reset_index()
    st.subheader("Сезонная статистика")
    st.write(season[season['city']==city])

    ak=st.text_input("Введите API ключ OpenWeatherMap")

    if ak:
        url=f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={ak}&units=metric"
        r=requests.get(url)
        data =r.json()
        if data.get("cod")==401:
            st.error("cod:401, message: Invalid API key. Please see https://openweathermap.org/faq#error401 for more info.")
        else:
            temp=data['main']['temp']
            st.write(f"Текущая температура: {temp}")

            def gets(x):
                if x in [12,1,2]:
                    return 'winter'
                elif x in [3,4,5]:
                    return 'spring'
                elif x in [6,7,8]:
                    return 'summer'
                else:
                    return 'autumn'
            s=gets(datetime.now().month)
            a=season[(season['city']==city)&(season['season']==s)]
            mean=a['mean'].values[0]
            std=a['std'].values[0]
            if temp>mean+2*std or temp<mean-2*std:
                st.error("Аномальная температура")
            else:
                st.success("Температура в норме")