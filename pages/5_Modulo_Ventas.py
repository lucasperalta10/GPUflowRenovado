import streamlit as st
from conexion import get_connection_pool
import statics.func_empleados as db_emp
import statics.func_productos as db_prod
import statics.func_ventas as db_ventas
import pandas as pd

st.set_page_config(
    page_title="Módulo de Ventas",
    page_icon="💸",
    layout="wide"
)

pool = get_connection_pool()
if not pool:
    st.error("Error de conexión a la base de datos.")
    st.stop()

st.title("💸 Módulo de Ventas")
st.badge("Versión BETA 5", color="yellow", icon="⚠️")

tab1, tab2 = st.tabs(["🛒 Registrar Venta", "📚 Historial de Ventas"])

# PESTAÑA 1: REGISTRAR VENTA
with tab1:
    
    if 'cart' not in st.session_state:
        st.session_state.cart = []

    df_empleados = db_emp.empleados(pool)
    df_productos = db_prod.productos_y_precios_disponibles(pool)
    if df_empleados.empty:
        st.error("No hay empleados registrados. Añada empleados primero.")
        st.stop()
    if df_productos.empty:
        st.error("No hay productos con stock disponible. Añada productos primero.")
        st.stop()

    employee_dict = pd.Series(
        df_empleados.ID.values, 
        index=df_empleados.apply(lambda r: f"{r['Apellido']}, {r['Nombre']}", axis=1)
    ).to_dict()
    
    product_dict = pd.Series(
        df_productos.id_producto.values,
        index=df_productos.Nombre
    ).to_dict()
    
    product_details = df_productos.set_index('id_producto').to_dict('index')

    # Sección 1: Selección de Empleado
    st.subheader("1. Vendedor a Cargo")
    empleado_nombre = st.selectbox(
        "Seleccione el empleado que realiza la venta:",
        options=list(employee_dict.keys()),
        key="empleado_selector"
    )
    id_empleado_seleccionado = employee_dict[empleado_nombre]

    st.markdown("---")

    # Sección 2: Añadir Productos al Carrito
    st.subheader("2. Añadir Productos al Carrito")
    with st.form("add_item_form"):
        col1, col2 = st.columns([3, 1])
        with col1:
            producto_modelo = st.selectbox(
                "Producto:",
                options=list(product_dict.keys()),
                index=None,
                placeholder="Seleccione un producto..."
            )
        with col2:
            max_stock = 1
            if producto_modelo:
                id_prod_sel = product_dict[producto_modelo]
                max_stock = product_details[id_prod_sel]['Stock']
            
            cantidad = st.number_input(
                "Cantidad:", min_value=1, max_value=int(max_stock), step=1,
                help=f"Stock disponible: {max_stock}"
            )
        
        submitted = st.form_submit_button("Añadir al Carrito")

    if submitted and producto_modelo:
        id_producto_seleccionado = product_dict[producto_modelo]
        detalles = product_details[id_producto_seleccionado]
        nuevo_item = {
            "ID": id_producto_seleccionado, "Nombre": producto_modelo, "Marca": detalles['Marca'], "Modelo": detalles['Modelo'],
            "Cantidad": cantidad, "Precio_Unitario": detalles['Precio'],
            "Subtotal": detalles['Precio'] * cantidad
        }
        st.session_state.cart.append(nuevo_item)
        st.success(f"¡Añadido! {cantidad}x {producto_modelo} al carrito.")

    st.markdown("---")

    # --- Sección 3: Carrito de Compra Actual ---
    st.subheader("3. Carrito de Compra Actual")
    if not st.session_state.cart:
        st.info("El carrito está vacío.")
    else:
        cart_df = pd.DataFrame(st.session_state.cart)
        st.dataframe(cart_df, use_container_width=True)
        
        monto_total_carrito = cart_df['Subtotal'].sum()
        st.metric(label="Monto Total del Carrito", value=f"${monto_total_carrito:,.2f}")
        
        if st.button("Vaciar Carrito 🗑️", type="secondary"):
            st.session_state.cart = []
            st.rerun()

        st.markdown("---")
        st.subheader("4. Finalizar Venta")
        
        if st.button("🚨 Procesar Venta y Facturar 🚨", type="primary"):
            with st.spinner("Procesando transacción..."):
                success, message = db_ventas.proceso_transaccion(
                    pool, id_empleado_seleccionado, st.session_state.cart
                )
            if success:
                st.success(message)
                st.balloons()
                st.session_state.cart = []
                st.cache_data.clear() 
            else:
                st.error(message)

# --- PESTAÑA 2: HISTORIAL DE VENTAS ---
with tab2:
    st.subheader("Historial General de Ventas")
    
    if st.button("Refrescar Historial"):
        st.rerun()

    df_sales_summary = db_ventas.resumen_ventas(pool)
    
    if df_sales_summary.empty:
        st.info("Aún no se han registrado ventas.")
    else:
        st.markdown("### 📊 Estadísticas de Ventas")
        
        df_sales_summary['Monto_total'] = df_sales_summary['Monto_total'].astype(float)
        
        ventas_por_empleado = df_sales_summary.groupby('Empleado')['Monto_total'].sum()
        
        st.bar_chart(ventas_por_empleado)
        st.markdown("---")

        st.dataframe(df_sales_summary, use_container_width=True)
        
        st.markdown("---")
        
        st.subheader("Ver Detalles de una Venta")
        
        sales_dict = pd.Series(
            df_sales_summary.id_compra.values,
            index=df_sales_summary.apply(
                lambda row: f"ID #{row['id_compra']} ({row['Fecha']}) - {row['Empleado']}", axis=1
            )
        ).to_dict()
        
        selected_sale_str = st.selectbox(
            "Seleccione una venta para ver su detalle:",
            options=list(sales_dict.keys()),
            index=None,
            placeholder="Seleccione una venta..."
        )
        
        if selected_sale_str:
            id_compra_seleccionada = sales_dict[selected_sale_str]
            df_details = db_ventas.detalles_venta(pool, id_compra_seleccionada)
            
            if df_details.empty:
                st.warning("No se encontraron detalles para esta venta.")
            else:
                st.markdown(f"**Mostrando detalles para la Venta ID #{id_compra_seleccionada}**")
                st.dataframe(df_details, use_container_width=True)