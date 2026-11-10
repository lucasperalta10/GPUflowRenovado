import streamlit as st
from conexion import get_connection_pool
import statics.func_empleados as db
import pandas as pd

st.set_page_config(
    page_title="Gestión de Empleados",
    page_icon="👤",
    layout="wide" 
)

pool = db.get_connection_pool()
if not pool:
    st.error("Error de conexión a la base de datos. Revise db_funciones.py")
    st.stop()

st.title("👤 Gestión de Empleados")
st.badge("Versión BETA 5", color="yellow", icon="⚠️")

try:
    df_empleados = db.empleados(pool)
except Exception as e:
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
        if not nombre_emp or not apellido_emp:
            st.warning("Por favor, complete los campos Nombre y Apellido.")
        else:
            cargo_para_db = cargo_emp if cargo_emp != "(Ninguno)" else None
            
            success, message = db.añadir_empleado(
                pool,
                nombre_emp, 
                apellido_emp, 
                cargo_para_db
            )
            
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
    
    if selected_employee_str:
        empleado_actual = employee_dict[selected_employee_str]
        id_empleado = empleado_actual['ID']
        
        cargo_actual = empleado_actual['Cargo'] if empleado_actual['Cargo'] else "(Ninguno)"
        try:
            indice_cargo = CARGO_OPTIONS.index(cargo_actual)
        except ValueError:
            indice_cargo = 0 

        with st.form("edit_employee_form"):
            st.markdown(f"**Editando ID: {id_empleado}**")
            
            nombre_edit = st.text_input("Nombre*", value=empleado_actual['Nombre'])
            apellido_edit = st.text_input("Apellido*", value=empleado_actual['Apellido'])
            cargo_edit = st.selectbox(
                "Cargo",
                options=CARGO_OPTIONS,
                index=indice_cargo,
                key="edit_cargo"
            )
            
            st.markdown("---")
            submitted_edit = st.form_submit_button("Guardar Cambios")
            
            if submitted_edit:
                if not nombre_edit or not apellido_edit:
                    st.warning("Los campos Nombre y Apellido son obligatorios.")
                else:
                    cargo_para_db_edit = cargo_edit if cargo_edit != "(Ninguno)" else None
                    
                    success, message = db.actualizar_empleado(
                        pool,
                        id_empleado,
                        nombre_edit,
                        apellido_edit,
                        cargo_para_db_edit
                    )
                    if success:
                        st.success(message)
                    else:
                        st.error(message)