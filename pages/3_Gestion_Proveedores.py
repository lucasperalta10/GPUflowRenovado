import streamlit as st
from conexion import get_connection_pool
import statics.func_proveedores as db_prov
import pandas as pd

st.set_page_config(
    page_title="Gestión de Proveedores",
    page_icon="🚚",
    layout="wide"
)

pool = db_prov.get_connection_pool()
if not pool:
    st.error("Error de conexión a la base de datos.")
    st.stop()

try:
    df_proveedores = db_prov.proveedores(pool)
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
        try:
            conn = pool.get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT id_proveedor, Nombre, Direccion, Correo_Electronico FROM Proveedor ORDER BY Nombre")
            full_suppliers_df = pd.DataFrame(cursor.fetchall())
            st.dataframe(full_suppliers_df, use_container_width=True)
        except Exception as e:
            st.error(f"Error al cargar datos completos: {e}")
        finally:
            if 'cursor' in locals(): cursor.close()
            if 'conn' in locals(): conn.close()
            
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
        if not nombre_prov:
            st.warning("El campo 'Nombre' es obligatorio.")
        else:
            success, message = db_prov.añadir_proveedor(
                pool, 
                nombre_prov, 
                direccion_prov, 
                email_prov
            )
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
    
    if selected_supplier_str:
        proveedor_actual = supplier_dict[selected_supplier_str]
        id_proveedor = proveedor_actual['id_proveedor']
        
        try:
            conn = pool.get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM Proveedor WHERE id_proveedor = %s", (id_proveedor,))
            data = cursor.fetchone()
        finally:
            if 'cursor' in locals(): cursor.close()
            if 'conn' in locals(): conn.close()

        with st.form("edit_supplier_form"):
            st.markdown(f"**Editando ID: {id_proveedor}**")
            
            nombre_edit = st.text_input("Nombre del Proveedor*", value=data.get('Nombre', ''))
            direccion_edit = st.text_input("Dirección (Opcional)", value=data.get('Direccion', ''))
            email_edit = st.text_input("Correo Electrónico (Opcional)", value=data.get('Correo_Electronico', ''))
            
            st.markdown("---")
            submitted_edit = st.form_submit_button("Guardar Cambios")
            
            if submitted_edit:
                if not nombre_edit:
                    st.warning("El campo 'Nombre' es obligatorio.")
                else:
                    success, message = db_prov.actualizar_proveedor(
                        pool,
                        id_proveedor,
                        nombre_edit,
                        direccion_edit,
                        email_edit
                    )
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
    
    if selected_supplier_to_delete_str:
        confirmacion = st.checkbox(
            f"Marque para confirmar la eliminación de: **{selected_supplier_to_delete_str}**."
        )
        
        if st.button("Eliminar Proveedor Permanentemente", disabled=(not confirmacion)):
            id_para_borrar = supplier_dict[selected_supplier_to_delete_str]['id_proveedor']
            
            success, message = db_prov.eliminar_proveedor(pool, id_para_borrar)
            
            if success:
                st.success(message)
            else:
                st.error(message)