import streamlit as st
from pages.login import mostrar_login


st.set_page_config(page_title="GPUflow", layout="wide", page_icon="🔐")


if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

def main():
    with st.sidebar:
        st.write(f"Usuario: **{st.session_state.get('usuario_actual', 'Anon')}**")
        if st.button("Cerrar Sesión"):
            st.session_state.logged_in = False
            st.rerun()
        st.divider()
        st.text("GPUflow - BETA 5")

    dashboard = st.Page("pages/home.py", title="Dashboard", icon="🏠", default=True)
    ventas = st.Page("pages/5_Modulo_Ventas.py", title="Punto de Venta", icon="💸")
    
    productos = st.Page("pages/2_Gestion_Productos.py", title="Productos", icon="📦")
    proveedores = st.Page("pages/3_Gestion_Proveedores.py", title="Proveedores", icon="🚚")
    empleados = st.Page("pages/4_Gestion_Empleados.py", title="Empleados", icon="👤")

    pg = st.navigation({
        "Resumen": [dashboard],
        "Operaciones": [ventas],
        "Administración": [productos, proveedores, empleados],
    })
    st.logo ("images/images.png")
    pg.run()

if st.session_state.logged_in:
    main()
else:
    mostrar_login()