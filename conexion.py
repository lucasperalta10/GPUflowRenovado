import streamlit as st
from src.core.database import DatabaseConnection


@st.cache_resource
def get_connection_pool():
    """
    Obtiene el pool de conexiones utilizando la clase Singleton DatabaseConnection.
    Se mantiene esta función como fachada para compatibilidad con los módulos existentes.
    """
    db = DatabaseConnection()
    return db.get_pool()
