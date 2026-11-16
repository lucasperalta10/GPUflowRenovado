import streamlit as st
import pandas as pd
from models.empleado import Empleado
from repositories.empleado_repository import EmpleadoRepository

st.set_page_config(
    page_title="Gestión de Empleados",
    page_icon="👤",
    layout="wide"
)

empleado_repo = EmpleadoRepository()
if not empleado_repo.pool:
    st.error("Error de conexión a la base de datos.")
    st.stop()

st.title("👤 Gestión de Empleados")
st.badge("Versión BETA 5", color="yellow", icon="⚠️")

try:
    df_empleados = empleado_repo.obtener_todos_df()
except Exception:
    st.error("No se pudieron cargar los empleados.")
    df_empleados = pd.DataFrame(columns=["ID", "Nombre", "Apellido", "Cargo"])

CARGO_OPTIONS = [
    "(Ninguno)",
    "Vendedor",
    "Gerente",
    "Técnico"
]

if not df_empleados.empty:
    employee_list = [f"{row['Apellido']}, {row['Nombre']} (ID: {row['ID']})" for _, row in df_empleados.iterrows()]
    employee_dict = {f"{row['Apellido']}, {row['Nombre']} (ID: {row['ID']})": row for _, row in df_empleados.iterrows()}
else:
    employee_list = ["No hay empleados registrados"]
    employee_dict = {}

# DEFINICIÓN DE PESTAÑAS
tab1, tab2, tab3 = st.tabs([
    "Ver Empleados",
    "➕ Añadir Empleado",
    "✍️ Editar Empleado"
])

# PESTAÑA 1: Ver Empleados
with tab1:
    st.subheader("Lista de Empleados Registrados")

    if st.button("Refrescar Datos"):
        st.rerun()

    if df_empleados.empty:
        st.info("No hay empleados registrados en la base de datos.")
    else:
        st.dataframe(df_empleados, use_container_width=True)

# PESTAÑA 2: Añadir Empleado
with tab2:
    st.subheader("Registrar un Nuevo Empleado")

    with st.form("new_employee_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            nombre_emp = st.text_input("Nombre*", key="new_nombre")
        with col2:
            apellido_emp = st.text_input("Apellido*", key="new_apellido")

        cargo_emp = st.selectbox(
            "Cargo",
            options=CARGO_OPTIONS,
            key="new_cargo"
        )

        st.markdown("*Campos obligatorios")
        st.markdown("---")

        submitted = st.form_submit_button("Guardar Empleado")

    if submitted:
        nuevo_empleado = Empleado(
            nombre=nombre_emp,
            apellido=apellido_emp,
            cargo=cargo_emp,
        )
        if not nuevo_empleado.tiene_datos_validos():
            st.warning("Por favor, complete los campos Nombre y Apellido.")
        else:
            success, message = empleado_repo.crear(nuevo_empleado)

            if success:
                st.success(message)
            else:
                st.error(message)

# PESTAÑA 3: Editar Empleado
with tab3:
    st.subheader("Modificar un Empleado Existente")

    selected_employee_str = st.selectbox(
        "Empleado a Editar:",
        options=employee_list,
        index=None,
        placeholder="Seleccione un empleado...",
        key="edit_select"
    )

    if selected_employee_str and selected_employee_str in employee_dict:
        empleado_actual = employee_dict[selected_employee_str]
        id_empleado = empleado_actual["ID"]

        cargo_actual = empleado_actual["Cargo"] if empleado_actual["Cargo"] else "(Ninguno)"
        try:
            indice_cargo = CARGO_OPTIONS.index(cargo_actual)
        except ValueError:
            indice_cargo = 0

        with st.form("edit_employee_form"):
            st.markdown(f"**Editando ID: {id_empleado}**")

            nombre_edit = st.text_input("Nombre*", value=empleado_actual["Nombre"])
            apellido_edit = st.text_input("Apellido*", value=empleado_actual["Apellido"])
            cargo_edit = st.selectbox(
                "Cargo",
                options=CARGO_OPTIONS,
                index=indice_cargo,
                key="edit_cargo"
            )

            st.markdown("---")
            submitted_edit = st.form_submit_button("Guardar Cambios")

            if submitted_edit:
                empleado_editado = Empleado(
                    id_empleado=id_empleado,
                    nombre=nombre_edit,
                    apellido=apellido_edit,
                    cargo=cargo_edit,
                )
                if not empleado_editado.tiene_datos_validos():
                    st.warning("Los campos Nombre y Apellido son obligatorios.")
                else:
                    success, message = empleado_repo.actualizar(empleado_editado)
                    if success:
                        st.success(message)
                    else:
                        st.error(message)
