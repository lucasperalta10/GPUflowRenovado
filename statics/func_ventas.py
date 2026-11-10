import streamlit as st
import pandas as pd
from conexion import get_connection_pool


def proceso_transaccion(pool, id_empleado, cart):
    if pool is None:
        return False, "Error de conexión"
    if not cart:
        return False, "El carrito está vacío"

    conn = None
    cursor = None

    try:
        conn = pool.get_connection()
        cursor = conn.cursor()

        conn.autocommit = False

        fecha_hoy = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")

        query_compra = """
            INSERT INTO Compra (Fecha_hora, id_empleado)
            VALUES (%s, %s)
        """
        data_compra = (fecha_hoy, id_empleado)
        cursor.execute(query_compra, data_compra)

        new_compra_id = cursor.lastrowid
        if not new_compra_id:
            raise Exception("No se pudo obtener el ID de la nueva compra.")

        for item in cart:
            query_stock = """
                UPDATE Producto
                SET Stock = Stock - %s
                WHERE id_producto = %s AND Stock >= %s
            """
            data_stock = (item['Cantidad'], item['ID'], item['Cantidad'])
            cursor.execute(query_stock, data_stock)

            if cursor.rowcount == 0:
                raise Exception(f"Stock insuficiente para {item['Nombre']}. Venta cancelada.")

            query_detalle = """
                INSERT INTO Detalle_Compra (Cantidad, Subtotal, id_producto, id_compra)
                VALUES (%s, %s, %s, %s)
            """
            data_detalle = (item['Cantidad'], item['Subtotal'], item['ID'], new_compra_id)
            cursor.execute(query_detalle, data_detalle)

        conn.commit()
        return True, f"¡Venta #{new_compra_id} registrada con éxito!"

    except Exception as e:
        if conn:
            conn.rollback()
        return False, f"Error en la transacción: {e}"
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def resumen_ventas(pool):
    """
    Obtiene un resumen de todas las compras, uniendo con el empleado.
    """
    if pool is None:
        return pd.DataFrame()

    query = """
    SELECT
        c.id_compra,
        c.Fecha_hora AS Fecha,
        COALESCE(SUM(dc.Subtotal), 0) AS Monto_total,
        CONCAT(e.Apellido, ', ', e.Nombre) AS Empleado
    FROM Compra c
    LEFT JOIN Detalle_Compra dc ON dc.id_compra = c.id_compra
    JOIN Empleado e ON c.id_empleado = e.id_empleado
    GROUP BY c.id_compra, c.Fecha_hora, e.Apellido, e.Nombre
    ORDER BY c.Fecha_hora DESC, c.id_compra DESC;
    """
    try:
        conn = pool.get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query)
        results = cursor.fetchall()
        return pd.DataFrame(results)
    except Exception as e:
        st.error(f"Error al consultar el historial de ventas: {e}")
        return pd.DataFrame()
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'conn' in locals() and conn:
            conn.close()


def detalles_venta(pool, id_compra):
    """
    Obtiene los detalles (productos) de una compra específica.
    """
    if pool is None:
        return pd.DataFrame()

    query = """
    SELECT
        dc.Cantidad,
        p.Nombre AS Producto,
        m.nombre_marca AS Marca,
        p.Modelo,
        dc.Subtotal
    FROM Detalle_Compra dc
    JOIN Producto p ON dc.id_producto = p.id_producto
    LEFT JOIN Marca m ON p.id_marca = m.id_marca
    WHERE dc.id_compra = %s;
    """
    data = (id_compra,)

    try:
        conn = pool.get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query, data)
        results = cursor.fetchall()
        return pd.DataFrame(results)
    except Exception as e:
        st.error(f"Error al consultar el detalle de la venta: {e}")
        return pd.DataFrame()
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'conn' in locals() and conn:
            conn.close()
