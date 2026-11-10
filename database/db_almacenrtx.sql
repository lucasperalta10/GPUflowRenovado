CREATE DATABASE IF NOT EXISTS db_almacenrtx;
USE db_almacenrtx;


CREATE TABLE IF NOT EXISTS Pais (
    id_pais INT AUTO_INCREMENT PRIMARY KEY,
    nombre_pais VARCHAR(100) NOT NULL
);

CREATE TABLE IF NOT EXISTS Usuario(
    id_usuario INT AUTO_INCREMENT PRIMARY KEY,
    nombre_usuario VARCHAR(100) NOT NULL,
    contrasena_usuario VARCHAR(255) NOT NULL,
    rol_usuario VARCHAR(30) DEFAULT "Admin",
    id_empleado INT NOT NULL,
    fecha_creacion (timestamp default current_timestamp):
    FOREIGN KEY (id_empleado) REFERENCES Empleado(id_empleado)
    ON UPDATE CASCADE
    ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS Region (
    id_region INT AUTO_INCREMENT PRIMARY KEY,
    nombre_region VARCHAR(100) NOT NULL,
    id_pais INT NOT NULL,
    FOREIGN KEY (id_pais) REFERENCES Pais(id_pais)
    ON UPDATE CASCADE
    ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS Ciudad (
    id_ciudad INT AUTO_INCREMENT PRIMARY KEY,
    nombre_ciudad VARCHAR(100) NOT NULL,
    id_region INT,
    FOREIGN KEY (id_region) REFERENCES Region(id_region)
    ON UPDATE CASCADE
    ON DELETE RESTRICT
);


CREATE TABLE IF NOT EXISTS Proveedor (
    id_proveedor INT AUTO_INCREMENT PRIMARY KEY,
    Nombre VARCHAR(100) NOT NULL,
    Direccion VARCHAR(150),
    id_ciudad INT NOT NULL,
    Correo_Electronico VARCHAR(100) UNIQUE,
    FOREIGN KEY (id_ciudad) REFERENCES Ciudad(id_ciudad)
    ON UPDATE CASCADE
    ON DELETE RESTRICT
);


CREATE TABLE IF NOT EXISTS Cargo (
    id_cargo INT AUTO_INCREMENT PRIMARY KEY,
    nombre_cargo VARCHAR(80) NOT NULL
);

CREATE TABLE IF NOT EXISTS Tipo_Memoria (
    id_tipo_memoria INT AUTO_INCREMENT PRIMARY KEY,
    nombre_tipo_memoria VARCHAR(90) NOT NULL,
    especificaciones_tipo_memoria TEXT
);

CREATE TABLE IF NOT EXISTS Empresa (
    id_empresa INT AUTO_INCREMENT PRIMARY KEY,
    nombre_empresa VARCHAR(100) NOT NULL,
    CUIT_empresa VARCHAR(20) UNIQUE NOT NULL,
    id_ciudad INT NOT NULL,
    FOREIGN KEY (id_ciudad) REFERENCES Ciudad(id_ciudad)
    ON UPDATE CASCADE
    ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS Marca (
    id_marca INT AUTO_INCREMENT PRIMARY KEY,
    nombre_marca VARCHAR(50) NOT NULL
);

CREATE TABLE IF NOT EXISTS Cliente (
    id_cliente INT AUTO_INCREMENT PRIMARY KEY,
    nombre_cliente VARCHAR(100) NOT NULL,
    apellido_cliente VARCHAR(100) NOT NULL,
    correo_cliente VARCHAR(100) UNIQUE NOT NULL,
    telefono_cliente VARCHAR(20) UNIQUE NOT NULL,
    DNI_cliente VARCHAR(20) UNIQUE NOT NULL,
    direccion_cliente VARCHAR(150) NOT NULL,
    id_ciudad INT,
    FOREIGN KEY (id_ciudad) REFERENCES Ciudad(id_ciudad)
    ON UPDATE CASCADE
    ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS Producto (
    id_producto INT AUTO_INCREMENT PRIMARY KEY,
    Nombre VARCHAR(100) NOT NULL,
    Modelo VARCHAR(50),
    Memoria_VRAM VARCHAR(50),
    Precio DECIMAL(10,2) NOT NULL,
    Stock INT DEFAULT 0,
    id_marca INT NOT NULL,
    id_tipo_memoria INT NOT NULL,
    id_proveedor INT NOT NULL,
    FOREIGN KEY (id_proveedor) REFERENCES Proveedor(id_proveedor)
    ON UPDATE CASCADE
    ON DELETE RESTRICT,
    FOREIGN KEY (id_tipo_memoria) REFERENCES Tipo_Memoria(id_tipo_memoria)
    ON UPDATE CASCADE
    ON DELETE RESTRICT,
    
    FOREIGN KEY (id_marca) REFERENCES Marca(id_marca)
    ON UPDATE CASCADE
    ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS Empleado (
    id_empleado INT AUTO_INCREMENT PRIMARY KEY,
    Nombre VARCHAR(100) NOT NULL,
    Apellido VARCHAR(100) NOT NULL,
    Correo_Electronico VARCHAR(100) UNIQUE,
    password VARCHAR(255) NOT NULL,
    direccion VARCHAR(150),
    id_cargo INT NOT NULL,
    id_ciudad INT NOT NULL,
    id_empresa INT NOT NULL,
    FOREIGN KEY (id_empresa) REFERENCES Empresa(id_empresa)
    ON UPDATE CASCADE
    ON DELETE RESTRICT,
    FOREIGN KEY (id_ciudad) REFERENCES Ciudad(id_ciudad)
    ON UPDATE CASCADE
    ON DELETE RESTRICT,
    FOREIGN KEY (id_cargo) REFERENCES Cargo(id_cargo)
    ON UPDATE CASCADE
    ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS Venta (
    id_venta INT AUTO_INCREMENT PRIMARY KEY,
    fecha_venta DATE NOT NULL,
    monto_total DECIMAL(10,2) NOT NULL,
    id_empleado INT NOT NULL,
    id_cliente INT NOT NULL,
    FOREIGN KEY (id_empleado) REFERENCES Empleado(id_empleado) 
        ON DELETE RESTRICT ON UPDATE CASCADE,
    FOREIGN KEY (id_cliente) REFERENCES Cliente(id_cliente) 
        ON DELETE RESTRICT ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS Compra (
    id_compra INT AUTO_INCREMENT PRIMARY KEY,
    Fecha_hora DATETIME NOT NULL,
    id_empleado INT NOT NULL,
    FOREIGN KEY (id_empleado) REFERENCES Empleado(id_empleado) ON DELETE RESTRICT ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS Detalle_Compra (
    id_detalle_compra INT AUTO_INCREMENT PRIMARY KEY,
    Cantidad INT NOT NULL,
    Subtotal DECIMAL(10,2) NOT NULL,
    id_producto INT NOT NULL,
    id_compra INT NOT NULL,
    FOREIGN KEY (id_producto) REFERENCES Producto(id_producto) ON DELETE RESTRICT ON UPDATE CASCADE,
    FOREIGN KEY (id_compra) REFERENCES Compra(id_compra) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS Detalle_Venta (
    id_detalle_venta INT AUTO_INCREMENT PRIMARY KEY,
    Cantidad INT NOT NULL,
    Subtotal DECIMAL(10,2) NOT NULL,
    id_producto INT NOT NULL,
    id_venta INT,
    FOREIGN KEY (id_producto) REFERENCES Producto(id_producto) ON DELETE RESTRICT ON UPDATE CASCADE,
    FOREIGN KEY (id_venta) REFERENCES Venta(id_venta) ON DELETE CASCADE ON UPDATE CASCADE
);