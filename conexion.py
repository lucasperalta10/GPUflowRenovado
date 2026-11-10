import os
from dotenv import load_dotenv
import streamlit as st
import mysql.connector
from mysql.connector import pooling

load_dotenv()


@st.cache_resource
def get_connection_pool():
    try:
        db_user = os.getenv("DB_USER", "root")
        db_pass = os.getenv("DB_PASSWORD", os.getenv("DB_PASS", ""))
        db_host = os.getenv("DB_HOST", "localhost")
        db_name = os.getenv("DB_NAME", "db_almacenrtx")
        db_port = int(os.getenv("DB_PORT", "3306"))

        pool = pooling.MySQLConnectionPool(
            pool_name="streamlit_pool",
            pool_size=5,
            user=db_user,
            password=db_pass,
            host=db_host,
            port=db_port,
            database=db_name,
        )

        return pool

    except Exception as e:
        print(f"Error al crear el pool de MySQL: {e}")
        st.error(f"Error de conexión a la base de datos: {e}")
        return None