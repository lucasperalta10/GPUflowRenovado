import streamlit as st
from src.services.auth_service import AuthService


def mostrar_login():
    auth_service = AuthService()

    _, col2, _ = st.columns([1, 1.4, 1])
    with col2:
        st.markdown("<h1 style='text-align: center;'>🔐 Acceso a GPUflow</h1>", unsafe_allow_html=True)

        tab1, tab2 = st.tabs(["Iniciar Sesión", "Registrarse"])

        # LOGIN
        with tab1:
            with st.form("login_formulario"):
                username = st.text_input("Usuario", key="login_username")
                contrasena = st.text_input("Contraseña", type="password", key="login_password")
                entrar = st.form_submit_button("Entrar", use_container_width=True, type="primary")

            if entrar:
                try:
                    user, error = auth_service.login(username, contrasena)
                    if error:
                        st.error(error)
                    else:
                        st.session_state.logged_in = True
                        st.session_state.authenticated = True
                        st.session_state.usuario_id = user.id_usuario
                        st.session_state.usuario_actual = user.username
                        st.rerun()
                except Exception:
                    st.error("No pudimos iniciar sesión. Revisá la conexión a la base de datos.")

        # REGISTRO
        with tab2:
            with st.form("registro_formulario", clear_on_submit=False):
                nuevo_usuario = st.text_input("Nuevo Usuario (3 a 50 caracteres)", max_chars=50, key="reg_user")
                nueva_contrasena = st.text_input(
                    "Contraseña (mínimo 8 caracteres)", type="password", key="reg_pass"
                )
                nueva_contrasena2 = st.text_input(
                    "Confirmar Contraseña", type="password", key="reg_pass2"
                )
                aceptado = st.checkbox("Acepto crear una cuenta en GPUflow", key="reg_accept")
                crear_cuenta = st.form_submit_button("Crear Cuenta", use_container_width=True, type="primary")

            if crear_cuenta:
                if not aceptado:
                    st.warning("Confirmá que querés crear la cuenta.")
                else:
                    try:
                        user, error = auth_service.register(
                            nuevo_usuario, nueva_contrasena, nueva_contrasena2
                        )
                        if error:
                            st.error(error)
                        else:
                            st.success("Cuenta creada correctamente. Ya podés iniciar sesión en la primera pestaña.")
                    except Exception:
                        st.error("No pudimos registrar el usuario. Revisá la conexión a MySQL.")
