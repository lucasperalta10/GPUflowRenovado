import streamlit as st
from conexion import get_connection_pool
import statics.func_productos as db_prod
import statics.func_proveedores as db_prov
import pandas as pd

st.set_page_config(
    page_title="Gestión de Productos",
    page_icon="📦",
    layout="wide"
)

pool = db_prod.get_connection_pool()
if not pool:
    st.error("Error de conexión a la base de datos.")
    st.stop()

st.title("📦 Gestión de Productos")
st.badge("Versión BETA 5", color="yellow", icon="⚠️")

try:
    df_proveedores = db_prov.proveedores(pool)
    df_productos_full = db_prod.obtener_productos(pool)
except Exception as e:
    st.error(f"No se pudieron cargar los datos: {e}")
    st.stop()

# Diccionarios de Proveedores
if not df_proveedores.empty:
    supplier_dict = pd.Series(
        df_proveedores.id_proveedor.values, 
        index=df_proveedores.Nombre
    ).to_dict()
    supplier_names = list(supplier_dict.keys())
else:
    supplier_dict = {}
    supplier_names = ["No hay proveedores registrados"]

# Diccionarios de Productos
if not df_productos_full.empty:
    df_productos_editable = df_productos_full.copy()
    
    product_dict = pd.Series(
        df_productos_editable.ID.values, 
        index=df_productos_editable.apply(lambda row: f"{row['Marca']} {row['Modelo']} - {row['Nombre']} (ID: {row['ID']})", axis=1)
    ).to_dict()
    product_names = list(product_dict.keys())
    
    df_productos_editable.set_index('ID', inplace=True)
else:
    product_dict = {}
    product_names = ["No hay productos para gestionar"]
    df_productos_editable = pd.DataFrame()


# PESTAÑAS
tab1, tab2, tab3 = st.tabs(["✍️ Editar Producto", "➕ Añadir Producto Nuevo", "⛔ Eliminar Producto"])

# PESTAÑA 1: EDITAR PRODUCTO
with tab1:
    st.subheader("Seleccionar Producto para Editar")
    
    selected_product_str = st.selectbox(
        "Producto:",
        options=product_names,
        index=None,
        placeholder="Seleccione un producto para modificar...",
        key="edit_select"
    )
    
    if selected_product_str:
        id_producto_a_editar = product_dict[selected_product_str]
        producto_actual = df_productos_editable.loc[id_producto_a_editar]
        
        proveedor_actual_nombre = producto_actual['Proveedor']
        try:
            indice_proveedor = supplier_names.index(proveedor_actual_nombre)
        except ValueError:
            indice_proveedor = 0 

        st.markdown("---")
        
        st.subheader(f"Editando: {producto_actual['Nombre']}")
        with st.form("edit_product_form"):
            
            nombre = st.text_input("Nombre Descriptivo", value=producto_actual['Nombre'])
            marca = st.text_input("Marca", value=producto_actual['Marca'])
            modelo = st.text_input("Modelo", value=producto_actual['Modelo'])
            vram = st.text_input("Memoria VRAM", value=producto_actual['VRAM'])
            
            col1, col2 = st.columns(2)
            with col1:
                precio = st.number_input("Precio (USD)", min_value=0.01, step=0.01, format="%.2f", value=float(producto_actual['Precio']))
            with col2:
                stock = st.number_input("Stock", min_value=0, step=1, value=producto_actual['Stock'])
            
            selected_supplier_name = st.selectbox(
                "Proveedor", 
                options=supplier_names,
                index=indice_proveedor
            )
            
            st.markdown("---")
            submitted = st.form_submit_button("Guardar Cambios")

            if submitted:
                if selected_supplier_name in supplier_dict:
                    id_proveedor_seleccionado = supplier_dict[selected_supplier_name]
                else:
                    st.error("Proveedor no válido seleccionado.")
                    st.stop()

                success = db_prod.actualizar_producto(
                    pool,
                    id_producto_a_editar,
                    nombre, marca, modelo, vram,
                    precio, stock, id_proveedor_seleccionado
                )
                
                if success:
                    st.success("¡Producto actualizado con éxito!")
                    st.info("Refresca la página para ver los cambios.")
                else:
                    st.error("Error al actualizar el producto.")

# PESTAÑA 2: AÑADIR PRODUCTO
with tab2:
    st.subheader("Registrar un Nuevo Producto")
    
    with st.form("new_product_form"):
        st.subheader("Detalles del Producto")
        
        nombre_new = st.text_input("Nombre Descriptivo", key="new_nombre")
        marca_new = st.text_input("Marca", key="new_marca")
        modelo_new = st.text_input("Modelo", key="new_modelo")
        vram_new = st.text_input("Memoria VRAM", key="new_vram")
        
        col1_new, col2_new = st.columns(2)
        with col1_new:
            precio_new = st.number_input("Precio (USD)", min_value=0.01, step=0.01, format="%.2f", key="new_precio")
        with col2_new:
            stock_new = st.number_input("Stock Inicial", min_value=0, step=1, key="new_stock")
        
        selected_supplier_name_new = st.selectbox(
            "Proveedor", 
            options=supplier_names,
            key="new_proveedor"
        )
        
        st.markdown("---")
        submitted_new = st.form_submit_button("Añadir Producto al Inventario")

    if submitted_new:
        if not nombre_new or not marca_new or not modelo_new or not selected_supplier_name_new:
            st.warning("Por favor, rellene todos los campos obligatorios.")
        else:
            try:
                id_proveedor_seleccionado_new = supplier_dict[selected_supplier_name_new]
                
                success_new = db_prod.añadir_producto(
                    pool,
                    nombre_new, marca_new, modelo_new, vram_new,
                    precio_new, stock_new, id_proveedor_seleccionado_new
                )
                
                if success_new:
                    st.success(f"¡Producto '{nombre_new}' añadido con éxito!")
                else:
                    st.error("Hubo un error al guardar el producto.")
            
            except Exception as e:
                st.error(f"Error inesperado: {e}")

# PESTAÑA 3: ELIMINAR PRODUCTO
with tab3:
    st.subheader("Eliminar un Producto")
    st.warning("Advertencia: Esta acción es irreversible. No podrá eliminar productos que ya tengan ventas registradas.")
    
    selected_product_to_delete_str = st.selectbox(
        "Producto a Eliminar:",
        options=product_names,
        index=None,
        placeholder="Seleccione un producto para eliminar...",
        key="delete_select"
    )
    
    if selected_product_to_delete_str:
        confirmacion = st.checkbox(
            f"Marque esta casilla para confirmar que desea eliminar: **{selected_product_to_delete_str}**."
        )
        
        if st.button("Eliminar Producto Permanentemente", disabled=(not confirmacion)):
            id_para_borrar = product_dict[selected_product_to_delete_str]
            
            success_delete, mensaje_eliminar = db_prod.eliminar_producto(pool, id_para_borrar)
            
            if success_delete:
                st.success(mensaje_eliminar)
                st.info("Refresca la página para actualizar las listas.")
            else:
                st.error(mensaje_eliminar)