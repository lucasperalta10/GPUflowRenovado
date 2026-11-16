import streamlit as st
import time
from models.usuario import Usuario
from repositories.usuario_repository import UsuarioRepository


st.set_page_config(
    page_title="Login - GPUflow",
    page_icon="🔐",
    layout="centered"
)


def mostrar_login():
    usuario_repo = UsuarioRepository()

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<h1 style='text-align: center;'>🔐 Acceso a GPUflow </h1>", unsafe_allow_html=True)

        tab1, tab2 = st.tabs(["Iniciar Sesión", "Registrarse"])

        # LOGIN
        with tab1:
            with st.form("login_formulario"):
                username = st.text_input("Usuario")
                contrasena = st.text_input("Contraseña", type="password")
                entrar = st.form_submit_button("Entrar", use_container_width=True)

            if entrar:
                usuario_obj = usuario_repo.autenticar(username, contrasena)
                if usuario_obj:
                    st.session_state.logged_in = True
                    st.session_state.usuario_actual = usuario_obj.username
                    st.success(f"### Bienvenido, {usuario_obj.username} al sistema GPUflow!")
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
                else:
                    usuario_nuevo = Usuario(username=nuevo_usuario, password=nueva_contrasena, rol="Admin")
                    if usuario_repo.crear(usuario_nuevo):
                        st.success("Cuenta creada. Por favor inicia sesión.")
                    else:
                        st.error("No se pudo crear el usuario.")
