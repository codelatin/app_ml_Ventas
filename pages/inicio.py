import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd

excel_file = "maquinaria.xlsx"
df = pd.read_excel(excel_file)
buscar_palabra = st.sidebar.text_input("Buscar en archivo excel")
fltrar_tabla = df[df.apply(lambda row: buscar_palabra.lower() in row.astype(str).str.lower().values, axis=1)]
st.write("Mostrando datos del archivo")
st.write(df)
st.write("Datos filtrados por la busqueda")
st.write(fltrar_tabla)
grafico = st.selectbox("Seleciona una columna para el grafico", df.columns)
contar_valores = df[grafico].astype(str).value_counts()
st.bar_chart(contar_valores)
plt.bar(contar_valores.index,contar_valores.values)
plt.xlabel(grafico)
plt.title("Grafico matplotlib")
plt.xticks(rotation=45)
st.pyplot(plt)