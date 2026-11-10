import streamlit as st
import pandas as pd
from conexion import get_connection_pool
import statics.func_productos as db_func_prod

st.set_page_config(
    page_title="Almacén de GPUs",
    page_icon="📦",
    layout="wide"
)

pool = db_func_prod.get_connection_pool()

if pool:
    df_productos = db_func_prod.obtener_productos(pool)
    df_stock_bajo = db_func_prod.obtener_stock_bajo(pool, umbral=10)
else:
    st.error("No se pudo conectar a la base de datos. Revise db_funciones.py")
    df_productos = pd.DataFrame()
    df_stock_bajo = pd.DataFrame()

st.title("📦 Dashboard de Inventario")
st.badge("Versión BETA 5", color="yellow", icon="⚠️")
st.markdown("Vista general del stock de productos.")

if not df_productos.empty:
    total_stock = int(df_productos['Stock'].sum())
    modelos_unicos = df_productos['Modelo'].nunique()
    valor_inventario = (df_productos['Precio'] * df_productos['Stock']).sum()
else:
    total_stock = 0
    modelos_unicos = 0
    valor_inventario = 0

col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label="Stock Total (Unidades)", value=total_stock)
with col2:
    st.metric(label="Modelos Diferentes", value=modelos_unicos)
with col3:
    st.metric(label="Valor Total del Inventario", value=f"${valor_inventario:,.2f}")

st.markdown("---")

if not df_stock_bajo.empty:
    st.warning("🚨 ¡ALERTA DE STOCK BAJO!")
    st.write("Los siguientes productos tienen 10 o menos unidades en stock:")
    df_stock_bajo.columns = ["Producto", "Marca", "Modelo", "Stock Disponible"]
    st.dataframe(df_stock_bajo, use_container_width=True)
    st.markdown("---")

st.header("Stock de Productos")
if not df_productos.empty:
    st.dataframe(df_productos, use_container_width=True)
else:
    st.warning("No hay productos en la base de datos para mostrar.")

if not df_productos.empty:
    st.subheader("Stock por Marca")
    stock_por_marca = df_productos.groupby('Marca')['Stock'].sum()
    if not stock_por_marca.empty:
        st.bar_chart(stock_por_marca)
    else:
        st.info("No hay datos de stock por marca.")
else:
    st.info("No hay datos para mostrar gráficos.")