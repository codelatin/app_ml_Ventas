import streamlit as st
import pandas as pd
import plotly.express as px
import altair as alt
from matplotlib import pyplot as plt
from datetime import date, timedelta
from streamlit_extras.dataframe_explorer import dataframe_explorer
from st_aggrid import AgGrid, GridOptionsBuilder
from sklearn.cluster import KMeans
from prophet import Prophet
import requests

# Page layout
st.set_page_config(page_title="Ventas", page_icon="🛒", layout="wide")

st.header("ANÁLISIS DE VENTAS Y TENDENCIAS 📦 | ANÁLISIS DESCRIPTIVOS 🛒")
st.write("Elija un rango de fechas en la barra lateral para ver las tendencias de ventas | la fecha predeterminada es hoy")

# Streamlit theme
theme_plotly = None 

# Load CSS Style
with open('style.css') as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Load dataset
df = pd.read_csv('sales.csv')
with st.sidebar:
    st.title("Selecciona el Rango Fecha PARA LA CATEGORIA")
    start_date = st.sidebar.date_input("Fecha Inicial", date.today() - timedelta(days=365*4))
    end_date = st.date_input(label="Fecha Final")
    selected_category = st.selectbox("Selecciona la Categoría de Producto", options=df['Category'].unique(), index=0)

# Filtrar datos por rango de fechas y categoría
df_filtered = df[(df['OrderDate'] >= str(start_date)) & (df['OrderDate'] <= str(end_date)) & (df['Category'] == selected_category)]

# Mostrar datos filtrados
st.subheader('Datos Filtrados POR CATEGORIA')
st.dataframe(df_filtered)


# Verificar que el DataFrame filtrado contiene la columna 'Category'
st.write("Columnas del DataFrame Filtrado:", df_filtered.columns)

# Convertir la columna 'Category' a códigos de categorías
df_filtered['Category'] = df_filtered['Category'].astype('category').cat.codes

# KMeans clustering
features = df_filtered[['TotalPrice', 'Quantity', 'Category']]
kmeans = KMeans(n_clusters=3)
df_filtered['Cluster'] = kmeans.fit_predict(features)

# Visualización del clustering
fig8 = px.scatter(df_filtered, x='TotalPrice', y='Quantity', color='Cluster', title='Clustering de Productos')
st.plotly_chart(fig8, use_container_width=True)





# Análisis de Precios y Cantidades
st.subheader('Análisis de Precios y Cantidades')
fig1 = px.scatter(df_filtered, x='UnitPrice', y='Quantity', color='Product', title='Precio Unitario vs Cantidad Vendida')
st.plotly_chart(fig1, use_container_width=True)
# Filter date to view sales
with st.sidebar:
    st.title("Selecciona el Rango Fecha")
    start_date = st.date_input("Fecha Inicial", date.today() - timedelta(days=365*4), key='start_date')
    end_date = st.date_input(label="Fecha Final", key='end_date')
    selected_category = st.selectbox("Selecciona la Categoría de Producto", options=df['Category'].unique(), index=0, key='selected_category')

st.markdown("""
    <style>
    .stApp {
        background-color: #f5f5f5;
    }
    </style>
    """, unsafe_allow_html=True)
st.error("Métricas comerciales entre [ " + str(start_date) + "] y [" + str(end_date) + "]")

# Compare date
df_filtered = df[(df['OrderDate'] >= str(start_date)) & (df['OrderDate'] <= str(end_date)) & (df['Category'] == selected_category)]

# Dataframe
with st.expander("Filtrar Datos Excel"):
    filtered_df = dataframe_explorer(df_filtered, case=False)
    st.dataframe(filtered_df, use_container_width=True)

# Interactive Data Explorer
st.subheader('Explorador de Datos Interactivo')
gb = GridOptionsBuilder.from_dataframe(df_filtered)
gb.configure_pagination()
gb.configure_side_bar()
gridOptions = gb.build()
AgGrid(df_filtered, gridOptions=gridOptions, enable_enterprise_modules=True)

# Low inventory alert
low_inventory_threshold = 5
low_inventory = df_filtered[df_filtered['Quantity'] < low_inventory_threshold]

if not low_inventory.empty:
    st.warning('¡Alerta! Los siguientes productos tienen un inventario muy bajo:')
    st.dataframe(low_inventory)

# Metric cards
st.subheader('Métricas')
from streamlit_extras.metric_cards import style_metric_cards
col1, col2 = st.columns(2)
col1.metric(label="Todos Los Productos del Inventario", value=df_filtered['Product'].count(), delta="Número de artículos en stock")
col2.metric(label="Suma del precio del producto:", value=f"{df_filtered['TotalPrice'].sum():,.0f}", delta=df_filtered['TotalPrice'].median())

col11, col22, col33 = st.columns(3)
col11.metric(label="Precio Máximo USD:", value=f"{df_filtered['TotalPrice'].max():,.0f}", delta="Precio mayor")
col22.metric(label="Precio mínimo USD:", value=f"{df_filtered['TotalPrice'].min():,.0f}", delta="precio menor")
col33.metric(label="Rango de precios total USD:", value=f"{df_filtered['TotalPrice'].max() - df_filtered['TotalPrice'].min():,.0f}", delta="Annual Salary Range")
style_metric_cards(background_color="#FFFFFF", border_left_color="#686664", border_color="#000000", box_shadow="#F71938")

# Análisis de precios y cantidades
st.subheader('Análisis de Precios y Cantidades')
fig1 = px.scatter(df_filtered, x='UnitPrice', y='Quantity', color='Product', title='Precio Unitario vs Cantidad Vendida')
st.plotly_chart(fig1, use_container_width=True)

# Dot Plot
a1, a2 = st.columns(2)
with a1:
    st.subheader('Productos & Precio Total')
    fig2 = px.scatter(df_filtered, x='Product', y='TotalPrice', color='Category', title='Productos & Precio Total')
    st.plotly_chart(fig2, use_container_width=True)

with a2:
    st.subheader('Productos & Precio Unitario')
    df_filtered['OrderMonth'] = pd.to_datetime(df_filtered['OrderDate']).dt.to_period('M').astype(str)  # Convertir Period a cadena
    monthly_prices = df_filtered.groupby(['OrderMonth', 'Product']).sum().reset_index()
    fig3 = px.bar(monthly_prices, x='OrderMonth', y='UnitPrice', color='Product', title='Precio Unitario por Mes')
    st.plotly_chart(fig3, use_container_width=True)

# Scatter Plot
p1, p2 = st.columns(2)
with p1:
    st.subheader('Funciones por frecuencia')
    feature_x = st.selectbox('Seleccionar característica para x Datos cualitativos', df_filtered.select_dtypes("object").columns, key='feature_x')
    feature_y = st.selectbox('Seleccionar característica para y Datos cuantitativos', df_filtered.select_dtypes("number").columns, key='feature_y')

    fig4 = px.scatter(df_filtered, x=feature_x, y=feature_y, color='Product', title=f'{feature_x} vs {feature_y}')
    st.plotly_chart(fig4, use_container_width=True)

with p2:
    st.subheader('Productos & Cantidades')
    quantity_per_product = df_filtered.groupby('Product').sum().reset_index()
    fig5 = px.bar(quantity_per_product, x='Product', y='Quantity', title='Cantidad Vendida por Producto')
    st.plotly_chart(fig5, use_container_width=True)

# Sales Forecasting
st.subheader('Pronóstico de Ventas')
forecast_period = st.slider('Selecciona el periodo de pronóstico en meses:', 1, 12, 3, key='forecast_period')
df_filtered['OrderDate'] = pd.to_datetime(df_filtered['OrderDate'])
df_filtered = df_filtered.groupby('OrderDate').agg({'TotalPrice': 'sum'}).reset_index()

# Prepare data for Prophet
df_forecast = df_filtered.rename(columns={'OrderDate': 'ds', 'TotalPrice': 'y'})
m = Prophet()
m.fit(df_forecast)

future = m.make_future_dataframe(periods=forecast_period * 30)
forecast = m.predict(future)

fig6 = px.line(forecast, x='ds', y='yhat', title='Pronóstico de Ventas')
st.plotly_chart(fig6)

#GRAFICOS DE tENDENCIA MANUAL
df_filtered['OrderMonth'] = pd.to_datetime(df_filtered['OrderDate']).dt.to_period('M').astype(str)
monthly_sales = df_filtered.groupby('OrderMonth').agg({'TotalPrice': 'sum'}).reset_index()
fig7 = px.line(monthly_sales, x='OrderMonth', y='TotalPrice', title='Tendencias de Ventas Mensuales')
st.plotly_chart(fig7, use_container_width=True)





st.sidebar.image("img/logo.png")

