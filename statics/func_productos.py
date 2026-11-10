import streamlit as st
import pandas as pd
from conexion import get_connection_pool


def _obtener_o_crear_marca(pool, nombre_marca):
    if pool is None or not nombre_marca:
        return None

    nombre = nombre_marca.strip()
    if not nombre:
        return None

    conn = None
    cursor = None
    try:
        conn = pool.get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT id_marca FROM Marca WHERE nombre_marca = %s", (nombre,))
        result = cursor.fetchone()
        if result:
            return result[0]

        cursor.execute("INSERT INTO Marca (nombre_marca) VALUES (%s)", (nombre,))
        conn.commit()
        return cursor.lastrowid
    except Exception as e:
        if conn:
            conn.rollback()
        st.error(f"Error al gestionar la marca: {e}")
        return None
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def obtener_productos(pool):
    if pool is None:
        st.warning("No hay pool de conexión.")
        return pd.DataFrame()

    query = """
    SELECT 
        p.id_producto, p.Nombre, m.nombre_marca AS Marca, p.Modelo, p.Memoria_VRAM,
        p.Precio, p.Stock, pr.Nombre AS Proveedor
    FROM Producto p
    LEFT JOIN Proveedor pr ON p.id_proveedor = pr.id_proveedor
    LEFT JOIN Marca m ON p.id_marca = m.id_marca
    ORDER BY m.nombre_marca, p.Modelo;
    """

    try:
        conn = pool.get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query)
        results = cursor.fetchall()

        df = pd.DataFrame(results)

        df.columns = [
            'ID', 'Nombre', 'Marca', 'Modelo',
            'VRAM', 'Precio', 'Stock', 'Proveedor'
        ]
        return df

    except Exception as e:
        st.error(f"Error al consultar los productos: {e}")
        return pd.DataFrame()
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'conn' in locals() and conn:
            conn.close()


def añadir_producto(pool, nombre, marca, modelo, vram, precio, stock, id_proveedor):
    if pool is None:
        return False

    id_marca = _obtener_o_crear_marca(pool, marca)
    if id_marca is None and marca:
        return False

    query = """
        INSERT INTO Producto
            (Nombre, Modelo, Memoria_VRAM, Precio, Stock, id_marca, id_proveedor)
        VALUES
            (%s, %s, %s, %s, %s, %s, %s)
    """
    data = (nombre, modelo, vram, precio, stock, id_marca, id_proveedor)

    try:
        conn = pool.get_connection()
        cursor = conn.cursor()
        cursor.execute(query, data)
        conn.commit()
        return True
    except Exception as e:
        st.error(f"Error al añadir el producto: {e}")
        if 'conn' in locals() and conn:
            conn.rollback()
        return False
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'conn' in locals() and conn:
            conn.close()


def productos_y_precios_disponibles(pool):
    if pool is None:
        return pd.DataFrame()

    query = """
    SELECT p.id_producto, p.Nombre, m.nombre_marca AS Marca, p.Modelo, p.Precio, p.Stock
    FROM Producto p
    LEFT JOIN Marca m ON p.id_marca = m.id_marca
    WHERE p.Stock > 0
    ORDER BY m.nombre_marca, p.Modelo;
    """
    try:
        conn = pool.get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query)
        results = cursor.fetchall()
        return pd.DataFrame(results)
    except Exception as e:
        st.error(f"Error al consultar productos disponibles: {e}")
        return pd.DataFrame()
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'conn' in locals() and conn:
            conn.close()


def actualizar_producto(pool, id_producto, nombre, marca, modelo, vram, precio, stock, id_proveedor):
    """
    Actualiza un producto existente en la base de datos.
    """
    if pool is None:
        return False

    id_marca = _obtener_o_crear_marca(pool, marca)
    if id_marca is None and marca:
        return False

    query = """
        UPDATE Producto
        SET
            Nombre = %s,
            Modelo = %s,
            Memoria_VRAM = %s,
            Precio = %s,
            Stock = %s,
            id_marca = %s,
            id_proveedor = %s
        WHERE
            id_producto = %s
    """
    data = (nombre, modelo, vram, precio, stock, id_marca, id_proveedor, id_producto)
    try:
        conn = pool.get_connection()
        cursor = conn.cursor()
        cursor.execute(query, data)
        conn.commit()
        return True
    except Exception as e:
        st.error(f"Error al actualizar el producto: {e}")
        if 'conn' in locals() and conn:
            conn.rollback()
        return False
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'conn' in locals() and conn:
            conn.close()


def obtener_stock_bajo(pool, umbral=10):
    """
    Obtiene productos con stock igual o inferior a un umbral.
    """
    if pool is None:
        return pd.DataFrame()

    query = """
        SELECT p.Nombre, m.nombre_marca AS Marca, p.Modelo, p.Stock
        FROM Producto p
        LEFT JOIN Marca m ON p.id_marca = m.id_marca
        WHERE p.Stock <= %s AND p.Stock > 0
        ORDER BY p.Stock ASC;
    """
    data = (umbral,)
    try:
        conn = pool.get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query, data)
        results = cursor.fetchall()
        return pd.DataFrame(results)
    except Exception as e:
        st.error(f"Error al consultar stock bajo: {e}")
        return pd.DataFrame()
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'conn' in locals() and conn:
            conn.close()


def eliminar_producto(pool, id_producto):
    """
    Elimina un producto de la base de datos usando su ID.
    Maneja la restricción de clave externa si el producto ya fue vendido.
    """
    if pool is None:
        return False, "Error de conexión"
    if not id_producto:
        return False, "No se seleccionó un ID"

    query = "DELETE FROM Producto WHERE id_producto = %s"
    data = (id_producto,)

    conn = None
    cursor = None

    try:
        conn = pool.get_connection()
        cursor = conn.cursor()
        cursor.execute(query, data)

        if cursor.rowcount == 1:
            conn.commit()
            return True, "¡Producto eliminado con éxito!"
        else:
            conn.rollback()
            return False, "No se encontró ningún producto con ese ID."

    except Exception as e:
        if conn:
            conn.rollback()

        if "foreign key constraint" in str(e).lower():
            return False, "Error: No se puede eliminar. El producto ya está asociado a una o más ventas."
        else:
            return False, f"Error inesperado al eliminar el producto: {e}"
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()