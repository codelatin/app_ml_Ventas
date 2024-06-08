import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import altair as alt
from streamlit_extras.dataframe_explorer import dataframe_explorer

import plotly.express as px
from streamlit_option_menu import option_menu
from numerize.numerize import numerize
import time
from streamlit_extras.metric_cards import style_metric_cards
st.set_option('deprecation.showPyplotGlobalUse', False)
import plotly.graph_objs as go




#uncomment this line if you use mysql
#from query import *

st.set_page_config(page_title="Dashboard",page_icon="🌍",layout="wide")
st.header("PROCESAMIENTO ANALÍTICO Y ESTADISTICO,  FRANK 2024")

#all graphs we use custom css not streamlit 
theme_plotly = None 


# load Style css
with open('style.css')as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html = True)

excel_file = "maquinaria.xlsx"
df = pd.read_excel(excel_file)
buscar_palabra = st.sidebar.text_input("Buscar en archivo excel")
fltrar_tabla = df[df.apply(lambda row: buscar_palabra.lower() in row.astype(str).str.lower().values, axis=1)]
st.write("Mostrando datos del archivo")
st.write(df)
st.write("Datos filtrados por la busqueda")
st.write(fltrar_tabla)

#uncomment these two lines if you fetch data from mysql
#result = view_all_data()
#df=pd.DataFrame(result,columns=["Policy","Expiry","Location","State","Region","Investment","Construction","BusinessType","Earthquake","Flood","Rating","id"])

#load excel file | comment this line when  you fetch data from mysql
df=pd.read_excel('maquinaria.xlsx', sheet_name='BD')
with st.sidebar:
    st.title("Seleccione El rango de Datos: ")
    start_date = st.date_input(label="Dato Inicial: ")

with st.sidebar:
    end_date = st.date_input(label="Dato Final: ")
st.error("Elige un Rango de Fecha : " + str(start_date) + "to" + str(end_date))


#switcher
st.sidebar.image("img/logo.png",caption="")

 
zona=st.sidebar.multiselect(
    "Selecciona una Zona",
     options=df["Zona"].unique(),
     default=df["Zona"].unique(),
)
machinename=st.sidebar.multiselect(
    "Selecciona El nombre de Maquina",
     options=df["MachineName"].unique(),
     default=df["MachineName"].unique(),
)

num_adiciones = st.sidebar.multiselect( 
    "Selecciona el Numero de Adiciones",
     options=df["NumOfAdds"].unique(),
     default=df["NumOfAdds"].unique(),
)


df_selection=df.query(
    " Zona==@zona & MachineName==@machinename & NumOfAdds==@num_adiciones" 
)
df2 = df [(df['BatchStartDate'] >= str(start_date)) & (df['BatchStartDate'] <= str(end_date))]

with st.expander("Filtrar datos Excel"):
    filtrar_df = dataframe_explorer(df2, case = False)
    st.dataframe(filtrar_df, use_container_width=True)
    
col1,col2= st.columns(2)
with col1:
    st.subheader(' Grafico')
    #Style
    st.markdown("""
                <style>
                    .divider{
                        margin-top: 10px;
                        margin-bottom: 10px;
                        height: 5px;
                        background-image: linear-gradient(to right, red, blue, green, orange, pink, yellow, violet);
                    }
                </style>
                <div class="divider"></div>
                """,unsafe_allow_html=True)
    source= pd.DataFrame({
        'Zona ($)': df2['Zona'],
        'MachineName': df2['MachineName']
    })
    bar_chart= alt.Chart(source).mark_line().encode(
        x='sum(Zona ($)):Q',
        y=alt.Y('MachineName:N', sort='-x')
    )
    st.altair_chart(bar_chart, use_container_width=True)

def Home():
    with st.expander("Ver Datos en Excel"):
        showData = st.multiselect('Filtrar Columna: ', df_selection.columns, default=["Zona", "MachineName", "NumOfAdds", "No. De Lotes Con Adiciones", "Efectividad de la adición"])
        st.dataframe(df_selection[showData], use_container_width=True)

    mediana = float(pd.Series(df_selection['NumOfAdds']).median()) 
    promedio = float(pd.Series(df_selection['NumOfAdds']).mean())
    desviacion = float(pd.Series(df_selection['NumOfAdds']).std())

   
    col1, col2, col3, col4,= st.columns(4, gap="medium")

    with col1:
        st.info("Mediana adiciones", icon="📊")
        st.metric(label="Resultado mediana", value=f" {mediana:.1f}")

    with col2:
        st.info("Promedio adiciones", icon="📊")
        st.metric(label="Resultado promedio", value=f" {promedio:.1f}")

    with col3:
        st.info("Desviacion_standar", icon="📊")
        st.metric(label="Resultado desviacion standar", value=f" {desviacion:.1f}")

    with col4:
        st.info("Histograma", icon="📊")
        fig = px.histogram(df_selection, x='NumOfAdds', title='Histograma de NumOfAdds')
        st.plotly_chart(fig, use_container_width=True)

Home()

def medidas_tendencia_central():
    st.subheader('Otras Medidas de Tendencia Central')
    moda = float(pd.Series(df_selection['NumOfAdds']).mode()) 
    varianza = float(pd.Series(df_selection['NumOfAdds']).var())
    valor_maximo = float(pd.Series(df_selection['NumOfAdds']).max())
    valor_minimo = float(pd.Series(df_selection['NumOfAdds']).min())

    col5, col6, col7, col8 = st.columns(4, gap="medium")

    with col5:
        st.info("Moda", icon="📊")
        st.metric(label="Resultado moda", value=f" {moda:.1f}")

    with col6:
        st.info("Varianza", icon="📊")
        st.metric(label="Resultado varianza", value=f" {varianza:.1f}")

    with col7:
        st.info("Valor maximo", icon="📊")
        st.metric(label="Resultado valor maximo", value=f" {valor_maximo:.1f}")
       
    with col8:
        st.info("Valor minimo", icon="📊")
        st.metric(label="Resultado valor minimo", value=f" {valor_minimo:.1f}")

medidas_tendencia_central()
def otras_medidas():
    st.write("Quartiles y Percentiles")
    st.dataframe(df,use_container_width=True)
    quartiles = df["NumOfAdds"].quantile([0.25,0.5,0.75])
    st.subheader("Quartiles")
    st.write(quartiles)
    percentil = df["NumOfAdds"].quantile([0.10,0.20,0.30,0.40,0.50,0.6,0.7,0.8,0.9,1.0])
    st.subheader("Percentiles")
    st.write(percentil)

   

otras_medidas()

def graficos():

   st.header("Grafico Histograma 📊")
   fig = px.histogram(df_selection, x='NumOfAdds', title='Histograma de NumOfAdds')
   st.plotly_chart(fig, use_container_width=True)

   grafico = st.selectbox("Seleciona una columna para el grafico", df.columns)
   contar_valores = df[grafico].astype(str).value_counts()
   st.bar_chart(contar_valores)
   plt.bar(contar_valores.index,contar_valores.values)
   plt.xlabel(grafico)
   plt.title("Grafico matplotlib")
   plt.xticks(rotation=45)
   st.pyplot(plt)
    
 
graficos()

