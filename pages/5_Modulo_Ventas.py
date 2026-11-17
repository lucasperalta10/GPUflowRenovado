import streamlit as st
import pandas as pd
from src.models.venta import ItemVenta, Venta
from src.services.inventario_service import EmpleadoService, ProductoService, VentaService

st.set_page_config(
    page_title="Módulo de Ventas",
    page_icon="💸",
    layout="wide"
)

empleado_service = EmpleadoService()
producto_service = ProductoService()
venta_service = VentaService()

st.title("💸 Módulo de Ventas")
st.badge("Versión BETA 5", color="yellow", icon="⚠️")

tab1, tab2 = st.tabs(["🛒 Registrar Venta", "📚 Historial de Ventas"])

# PESTAÑA 1: REGISTRAR VENTA
with tab1:
    if "cart" not in st.session_state:
        st.session_state.cart = []

    try:
        df_empleados = empleado_service.listar()
        df_productos = producto_service.listar_disponibles()
    except Exception as exc:
        st.error(f"Error de conexión a la base de datos: {exc}")
        st.stop()

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

    product_details = df_productos.set_index("id_producto").to_dict("index")

    # Sección 1: Selección de Empleado
    st.subheader("1. Vendedor a Cargo")
    empleado_nombre = st.selectbox(
        "Seleccione el empleado que realiza la venta:",
        options=list(employee_dict.keys()),
        key="empleado_selector"
    )
    id_empleado_seleccionado = int(employee_dict[empleado_nombre])

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
                max_stock = product_details[id_prod_sel]["Stock"]

            cantidad = st.number_input(
                "Cantidad:", min_value=1, max_value=int(max_stock), step=1,
                help=f"Stock disponible: {max_stock}"
            )

        submitted = st.form_submit_button("Añadir al Carrito")

    if submitted and producto_modelo:
        id_producto_seleccionado = int(product_dict[producto_modelo])
        detalles = product_details[id_producto_seleccionado]
        item_venta = ItemVenta(
            id_producto=id_producto_seleccionado,
            nombre=producto_modelo,
            marca=detalles["Marca"] or "",
            modelo=detalles["Modelo"] or "",
            cantidad=cantidad,
            precio_unitario=float(detalles["Precio"]),
        )
        st.session_state.cart.append(item_venta.to_dict())
        st.success(f"¡Añadido! {item_venta.cantidad}x {item_venta.nombre} al carrito.")

    st.markdown("---")

    # Sección 3: Carrito de Compra Actual
    st.subheader("3. Carrito de Compra Actual")
    if not st.session_state.cart:
        st.info("El carrito está vacío.")
    else:
        cart_df = pd.DataFrame(st.session_state.cart)
        st.dataframe(cart_df, use_container_width=True)

        items_obj = [ItemVenta.from_dict(item) for item in st.session_state.cart]
        venta_actual = Venta(id_empleado=id_empleado_seleccionado, items=items_obj)

        st.metric(label="Monto Total del Carrito", value=f"${venta_actual.monto_total:,.2f}")

        if st.button("Vaciar Carrito 🗑️", type="secondary"):
            st.session_state.cart = []
            st.rerun()

        st.markdown("---")
        st.subheader("4. Finalizar Venta")

        if st.button("🚨 Procesar Venta y Facturar 🚨", type="primary"):
            with st.spinner("Procesando transacción..."):
                success, message = venta_service.procesar_venta(
                    id_empleado_seleccionado, st.session_state.cart
                )
            if success:
                st.success(message)
                st.balloons()
                st.session_state.cart = []
                st.cache_data.clear()
            else:
                st.error(message)

# PESTAÑA 2: HISTORIAL DE VENTAS
with tab2:
    st.subheader("Historial General de Ventas")

    if st.button("Refrescar Historial"):
        st.rerun()

    df_sales_summary = venta_service.resumen_ventas()

    if df_sales_summary.empty:
        st.info("Aún no se han registrado ventas.")
    else:
        st.markdown("### 📊 Estadísticas de Ventas")

        df_sales_summary["Monto_total"] = df_sales_summary["Monto_total"].astype(float)

        ventas_por_empleado = df_sales_summary.groupby("Empleado")["Monto_total"].sum()

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
            id_compra_seleccionada = int(sales_dict[selected_sale_str])
            df_details = venta_service.detalles_venta(id_compra_seleccionada)

            if df_details.empty:
                st.warning("No se encontraron detalles para esta venta.")
            else:
                st.markdown(f"**Mostrando detalles para la Venta ID #{id_compra_seleccionada}**")
                st.dataframe(df_details, use_container_width=True)
