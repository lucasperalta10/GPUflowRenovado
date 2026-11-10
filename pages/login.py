import streamlit as st
import statics.func_usuarios as db_usuario
import time
from conexion import get_connection_pool


st.set_page_config(
    page_title="Login - GPUflow",
    page_icon="🔐",
    layout="centered"
)

def mostrar_login():
    pool = get_connection_pool()
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<h1 style='text-align: center;'>🔐 Acceso a GPUflow </h1>", unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs(["Iniciar Sesión", "Registrarse"])
        
        # LOGIN
        with tab1:
            with st.form("login_formulario"):
                usuario = st.text_input("Usuario")
                contrasena = st.text_input("Contraseña", type="password")
                entrar = st.form_submit_button("Entrar", use_container_width=True)
                
            if entrar:
                usuario_data = db_usuario.login_usuario(pool, usuario, contrasena)
                if usuario_data:
                    st.session_state.logged_in = True
                    st.session_state.usuario_actual = usuario_data['username']
                    st.success(f"### Bienvenido, {usuario_data['username']} al sistema GPUflow!")
                    time.sleep(2)
                    st.rerun()
                else:
                    st.error("Usuario o contraseña incorrectos.")

        # REGISTRO 
        with tab2:
            with st.form("registro_formulario"):
                nuevo_usuario = st.text_input("Nuevo Usuario")
                nueva_contrasena = st.text_input("Contraseña", type="password")
                nueva_contrasena2 = st.text_input("Confirmar Contraseña", type="password")
                crear_cuenta = st.form_submit_button("Crear Cuenta", use_container_width=True)

            if crear_cuenta:
                if nueva_contrasena != nueva_contrasena2:
                    st.error("Las contraseñas no coinciden.")
                elif db_usuario.crear_usuario(pool, nuevo_usuario, nueva_contrasena):
                    st.success("Cuenta creada. Por favor inicia sesión.")
                else:
                    st.error("No se pudo crear el usuario.")