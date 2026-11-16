import streamlit as st
import pandas as pd
from models.proveedor import Proveedor
from repositories.proveedor_repository import ProveedorRepository

st.set_page_config(
    page_title="Gestión de Proveedores",
    page_icon="🚚",
    layout="wide"
)

proveedor_repo = ProveedorRepository()
if not proveedor_repo.pool:
    st.error("Error de conexión a la base de datos.")
    st.stop()

try:
    df_proveedores = proveedor_repo.obtener_todos_df()
except Exception as e:
    st.error(f"No se pudieron cargar los proveedores: {e}")
    df_proveedores = pd.DataFrame(columns=["id_proveedor", "Nombre"])

st.title("🚚 Gestión de Proveedores")
st.badge("Versión BETA 5", color="yellow", icon="⚠️")

if not df_proveedores.empty:
    supplier_list = [f"{row['Nombre']} (ID: {row['id_proveedor']})" for _, row in df_proveedores.iterrows()]
    supplier_dict = {f"{row['Nombre']} (ID: {row['id_proveedor']})": row for _, row in df_proveedores.iterrows()}
else:
    supplier_list = ["No hay proveedores registrados"]
    supplier_dict = {}

# DEFINICIÓN DE PESTAÑAS (TABS)
tab1, tab2, tab3, tab4 = st.tabs([
    "Ver Proveedores",
    "➕ Añadir Proveedor",
    "✍️ Editar Proveedor",
    "⛔ Eliminar Proveedor"
])

# PESTAÑA 1: Ver Proveedores
with tab1:
    st.subheader("Lista de Proveedores Registrados")
    if st.button("Refrescar Lista"):
        st.rerun()

    if df_proveedores.empty:
        st.info("No hay proveedores registrados.")
    else:
        full_suppliers_df = proveedor_repo.obtener_todos_completos_df()
        if not full_suppliers_df.empty:
            st.dataframe(full_suppliers_df, use_container_width=True)

# PESTAÑA 2: Añadir Proveedor
with tab2:
    st.subheader("Registrar un Nuevo Proveedor")
    with st.form("new_supplier_form", clear_on_submit=True):
        nombre_prov = st.text_input("Nombre del Proveedor*", key="new_nombre")
        direccion_prov = st.text_input("Dirección (Opcional)", key="new_dir")
        email_prov = st.text_input("Correo Electrónico (Opcional, debe ser único)", key="new_email")

        st.markdown("---")
        submitted = st.form_submit_button("Guardar Proveedor")

    if submitted:
        nuevo_proveedor = Proveedor(
            nombre=nombre_prov,
            direccion=direccion_prov,
            email=email_prov,
        )
        if not nuevo_proveedor.tiene_datos_validos():
            st.warning("El campo 'Nombre' es obligatorio.")
        else:
            success, message = proveedor_repo.crear(nuevo_proveedor)
            if success:
                st.success(message)
            else:
                st.error(message)

# PESTAÑA 3: Editar Proveedor
with tab3:
    st.subheader("Modificar un Proveedor Existente")

    selected_supplier_str = st.selectbox(
        "Proveedor a Editar:",
        options=supplier_list,
        index=None,
        placeholder="Seleccione un proveedor...",
        key="edit_select"
    )

    if selected_supplier_str and selected_supplier_str in supplier_dict:
        proveedor_actual = supplier_dict[selected_supplier_str]
        id_proveedor = proveedor_actual["id_proveedor"]

        prov_obj = proveedor_repo.obtener_por_id(id_proveedor)
        if prov_obj:
            with st.form("edit_supplier_form"):
                st.markdown(f"**Editando ID: {id_proveedor}**")

                nombre_edit = st.text_input("Nombre del Proveedor*", value=prov_obj.nombre)
                direccion_edit = st.text_input("Dirección (Opcional)", value=prov_obj.direccion or "")
                email_edit = st.text_input("Correo Electrónico (Opcional)", value=prov_obj.email or "")

                st.markdown("---")
                submitted_edit = st.form_submit_button("Guardar Cambios")

                if submitted_edit:
                    proveedor_editado = Proveedor(
                        id_proveedor=id_proveedor,
                        nombre=nombre_edit,
                        direccion=direccion_edit,
                        email=email_edit,
                    )
                    if not proveedor_editado.tiene_datos_validos():
                        st.warning("El campo 'Nombre' es obligatorio.")
                    else:
                        success, message = proveedor_repo.actualizar(proveedor_editado)
                        if success:
                            st.success(message)
                        else:
                            st.error(message)

# PESTAÑA 4: Eliminar Proveedor
with tab4:
    st.subheader("Eliminar un Proveedor")
    st.warning("Advertencia: Esta acción es irreversible. No podrá eliminar proveedores que ya estén asociados a productos.")

    selected_supplier_to_delete_str = st.selectbox(
        "Proveedor a Eliminar:",
        options=supplier_list,
        index=None,
        placeholder="Seleccione un proveedor...",
        key="delete_select"
    )

    if selected_supplier_to_delete_str and selected_supplier_to_delete_str in supplier_dict:
        confirmacion = st.checkbox(
            f"Marque para confirmar la eliminación de: **{selected_supplier_to_delete_str}**."
        )

        if st.button("Eliminar Proveedor Permanentemente", disabled=(not confirmacion)):
            id_para_borrar = supplier_dict[selected_supplier_to_delete_str]["id_proveedor"]

            success, message = proveedor_repo.eliminar(id_para_borrar)

            if success:
                st.success(message)
            else:
                st.error(message)
