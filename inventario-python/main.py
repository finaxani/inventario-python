import sqlite3

DB_NAME = "inventario.db"

# =========================================================
# FUNCIONES PARA MANEJAR LA BASE DE DATOS (SQLITE)
# =========================================================

def crear_base_de_datos():
    with sqlite3.connect(DB_NAME) as conexion:
        cursor = conexion.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS productos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                descripcion TEXT,
                cantidad INTEGER NOT NULL,
                precio REAL NOT NULL,
                categoria TEXT
            )
        ''')

def guardar_producto(nombre, descripcion, cantidad, precio, categoria):
    with sqlite3.connect(DB_NAME) as conexion:
        cursor = conexion.cursor()
        cursor.execute('''
            INSERT INTO productos (nombre, descripcion, cantidad, precio, categoria)
            VALUES (?, ?, ?, ?, ?)
        ''', (nombre, descripcion, cantidad, precio, categoria))

def traer_todos_los_productos():
    with sqlite3.connect(DB_NAME) as conexion:
        cursor = conexion.cursor()
        cursor.execute("SELECT * FROM productos")
        return cursor.fetchall()

def modificar_producto(id_prod, nombre, descripcion, cantidad, precio, categoria):
    with sqlite3.connect(DB_NAME) as conexion:
        cursor = conexion.cursor()
        cursor.execute('''
            UPDATE productos 
            SET nombre = ?, descripcion = ?, cantidad = ?, precio = ?, categoria = ?
            WHERE id = ?
        ''', (nombre, descripcion, cantidad, precio, categoria, id_prod))
        return cursor.rowcount > 0

def borrar_producto(id_prod):
    with sqlite3.connect(DB_NAME) as conexion:
        cursor = conexion.cursor()
        cursor.execute("DELETE FROM productos WHERE id = ?", (id_prod,))
        return cursor.rowcount > 0

def buscar_por_id(id_prod):
    with sqlite3.connect(DB_NAME) as conexion:
        cursor = conexion.cursor()
        cursor.execute("SELECT * FROM productos WHERE id = ?", (id_prod,))
        return cursor.fetchone()

def consultar_bajo_stock(limite):
    with sqlite3.connect(DB_NAME) as conexion:
        cursor = conexion.cursor()
        cursor.execute("SELECT * FROM productos WHERE cantidad <= ?", (limite,))
        return cursor.fetchall()

# =========================================================
# FUNCIONES AUXILIARES DE VALIDACIÓN
# =========================================================

def pedir_entero(mensaje, permitir_vacio=False):
    while True:
        valor = input(mensaje).strip()
        if permitir_vacio and valor == "":
            return None
        try:
            return int(valor)
        except ValueError:
            print("Error: Debe ingresar un numero entero valido.")

def pedir_flotante(mensaje, permitir_vacio=False):
    while True:
        valor = input(mensaje).strip()
        if permitir_vacio and valor == "":
            return None
        try:
            return float(valor)
        except ValueError:
            print("Error: Ingrese un precio valido (ej: 1500 o 450.50).")

# =========================================================
# INTERFAZ POR TERMINAL (MENÚ PRINCIPAL)
# =========================================================

def mostrar_menu():
    crear_base_de_datos()

    while True:
        print("\n--- MENU PRINCIPAL - CONTROL DE INVENTARIO ---")
        print("1. Registrar nuevo producto")
        print("2. Visualizar todos los productos")
        print("3. Actualizar producto por ID")
        print("4. Eliminar producto por ID")
        print("5. Buscar producto por ID")
        print("6. Reporte de bajo stock")
        print("7. Salir")
        
        opcion = input("Escriba el numero de opcion: ").strip()

        if opcion == "1":
            print("\n-- REGISTRAR PRODUCTO --")
            nombre = input("Nombre del producto (obligatorio): ").strip()
            while not nombre:
                print("Error: El nombre no puede quedar vacio.")
                nombre = input("Nombre del producto (obligatorio): ").strip()

            descripcion = input("Descripcion breve: ").strip()
            cantidad = pedir_entero("Cantidad disponible (entero): ")
            precio = pedir_flotante("Precio del producto: ")
            categoria = input("Categoria: ").strip()

            guardar_producto(nombre, descripcion, cantidad, precio, categoria)
            print("¡Producto guardado correctamente!")

        elif opcion == "2":
            print("\n-- LISTADO COMPLETO DE PRODUCTOS --")
            todos = traer_todos_los_productos()
            if not todos:
                print("No hay productos cargados en la base de datos.")
            else:
                for p in todos:
                    print(f"ID: {p[0]} | Nombre: {p[1]} | Categoria: {p[5]} | Stock: {p[3]} | Precio: ${p[4]:.2f} | Detalle: {p[2]}")

        elif opcion == "3":
            print("\n-- MODIFICAR PRODUCTO --")
            id_prod = pedir_entero("Ingrese el ID del producto que quiere cambiar: ")
            prod_actual = buscar_por_id(id_prod)
            
            if prod_actual:
                print(f"Modificando producto: {prod_actual[1]} (Presione ENTER para mantener el valor actual)")
                
                nuevo_nombre = input(f"Nuevo nombre [{prod_actual[1]}]: ").strip() or prod_actual[1]
                nueva_desc = input(f"Nueva descripcion [{prod_actual[2]}]: ").strip() or prod_actual[2]
                
                cant_in = pedir_entero(f"Nueva cantidad [{prod_actual[3]}]: ", permitir_vacio=True)
                nueva_cantidad = cant_in if cant_in is not None else prod_actual[3]
                
                precio_in = pedir_flotante(f"Nuevo precio [${prod_actual[4]}]: ", permitir_vacio=True)
                nuevo_precio = precio_in if precio_in is not None else prod_actual[4]
                
                nueva_cat = input(f"Nueva categoria [{prod_actual[5]}]: ").strip() or prod_actual[5]

                modificar_producto(id_prod, nuevo_nombre, nueva_desc, nueva_cantidad, nuevo_precio, nueva_cat)
                print("¡Producto actualizado con exito!")
            else:
                print("No se encontro ningun producto con ese ID.")

        elif opcion == "4":
            print("\n-- ELIMINAR PRODUCTO --")
            id_eliminar = pedir_entero("Ingrese el ID del producto a borrar: ")
            if borrar_producto(id_eliminar):
                print("¡Producto borrado de la base de datos!")
            else:
                print("No se encontro ningun producto con ese ID.")

        elif opcion == "5":
            print("\n-- BUSQUEDA DE PRODUCTO --")
            id_buscar = pedir_entero("Ingrese el ID que busca: ")
            p = buscar_por_id(id_buscar)
            if p:
                print("\nProducto Encontrado:")
                print(f"ID: {p[0]}\nNombre: {p[1]}\nDescripcion: {p[2]}\nStock: {p[3]}\nPrecio: ${p[4]:.2f}\nCategoria: {p[5]}")
            else:
                print("No se encontro ese ID en el sistema.")

        elif opcion == "6":
            print("\n-- REPORTE ALERTA DE STOCK --")
            limite = pedir_entero("Ver productos con stock igual o menor a: ")
            bajos = consultar_bajo_stock(limite)
            if not bajos:
                print("Ningun producto esta por debajo de ese limite.")
            else:
                print(f"\nProductos criticos (Stock <= {limite}):")
                for p in bajos:
                    print(f"ID: {p[0]} - {p[1]} (Stock actual: {p[3]})")

        elif opcion == "7":
            print("Cerrando el sistema. ¡Buenas vibras!")
            break
        else:
            print("Opcion no valida. Intente con un numero del 1 al 7.")

if __name__ == "__main__":
    mostrar_menu()