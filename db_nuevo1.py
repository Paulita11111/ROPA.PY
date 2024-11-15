import sqlite3
import requests
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from flask import Flask, jsonify, request

DATABASE = "base1.db"
CSV_FILE = "Updated_Clothing_Products.csv"  # Usando el archivo descargado

# Función para crear la tabla en la base de datos
def crear_tabla():
    with sqlite3.connect(DATABASE) as conn:
        c = conn.cursor()
        c.execute('DROP TABLE IF EXISTS product_catalog')
        c.execute(''' 
            CREATE TABLE IF NOT EXISTS product_catalog (
                index INTEGER PRIMARY KEY,
                product TEXT,
                category TEXT,
                sub_category TEXT,
                brand TEXT,
                sale_price REAL,
                market_price REAL,
                type TEXT,
                rating REAL,
                description TEXT,
                sale_price_euro REAL,
                market_price_euro REAL
            )
        ''')
        conn.commit()

# Función para importar los productos desde el CSV
def importar_productos():
    try:
        df = pd.read_csv(CSV_FILE, on_bad_lines='skip', delimiter=",")
        with sqlite3.connect(DATABASE) as conn:
            c = conn.cursor()
            for _, row in df.iterrows():
                c.execute(''' 
                    INSERT INTO product_catalog (
                        "index", product, category, sub_category, brand, sale_price, 
                        market_price, type, rating, description
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    row["index"], row["product"], row["category"], row["sub_category"],
                    row["brand"], row["sale_price"], row["market_price"], 
                    row["type"], row["rating"], row["description"]
                ))
            conn.commit()
    except Exception as e:
        print(f"Error al leer el archivo CSV: {e}")

# Función para obtener todos los productos
def get_products():
    with sqlite3.connect(DATABASE) as conn:
        conn.row_factory = sqlite3.Row
        products = conn.execute("SELECT * FROM product_catalog").fetchall()
        return products

# Función para obtener un producto por su ID
def get_product(id):
    with sqlite3.connect(DATABASE) as conn:
        conn.row_factory = sqlite3.Row
        product = conn.execute("SELECT rowid, * FROM product_catalog WHERE rowid = ?", (id,)).fetchone()
        if product is None:
            return {"message": "Product not found"}, 404
        return dict(product)

# Función para añadir un nuevo producto
def add_product(new_product):
    #new_product = request.get_json()
    with sqlite3.connect(DATABASE) as conn:
        conn.execute(''' 
            INSERT INTO product_catalog (
                "index", product, category, sub_category, brand, sale_price, 
                market_price, type, rating, description
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            new_product['index'], new_product['product'], new_product['category'], 
            new_product['sub_category'], new_product['brand'], new_product['sale_price'], 
            new_product['market_price'], new_product['type'], new_product['rating'], 
            new_product['description']
        ))
        conn.commit()

# Función para actualizar un producto existente
def update_product(id):
    product_details = request.get_json()
    with sqlite3.connect(DATABASE) as conn:
        conn.execute(''' 
            UPDATE product_catalog SET 
                "index" = ?, product = ?, category = ?, sub_category = ?, brand = ?, 
                sale_price = ?, market_price = ?, type = ?, rating = ?, description = ?
            WHERE rowid = ?
        ''', (
            product_details['index'], product_details['product'], product_details['category'], 
            product_details['sub_category'], product_details['brand'], product_details['sale_price'], 
            product_details['market_price'], product_details['type'], product_details['rating'], 
            product_details['description'], id
        ))
        conn.commit()

# Función para eliminar un producto
def delete_product(id):
    with sqlite3.connect(DATABASE) as conn:
        conn.execute("DELETE FROM product_catalog WHERE rowid = ?", (id,))
        conn.commit()

# Función para obtener el valor del dólar en euros desde la API
def obtener_valores_dolar():
    try:
        base_url = "https://api.bluelytics.com.ar/v2/latest"
        response = requests.get(base_url)
        data = response.json()
        # Extraemos el valor del dólar en euros desde la respuesta de la API
        dolar_rate = data["blue_dolar"]["value_sell"]
        return dolar_rate

# Función para convertir la base de datos a DataFrame
def db_to_dataframe():
    try:
        with sqlite3.connect(DATABASE) as conn:
            # Leemos todos los productos de la tabla en un DataFrame
            df = pd.read_sql_query("SELECT rowid, * FROM product_catalog", conn)
        return df
    except Exception as e:
        print(f"Error al convertir la base de datos a DataFrame: {e}")
        return None

# Función para crear los gráficos descriptivos
def graficos_descriptivos(df):
    # Gráfico de la proporción de productos por categoría (Pie chart)
    plt.figure(figsize=(8, 8))
    categoria_counts = df['category'].value_counts()
    plt.pie(categoria_counts, labels=categoria_counts.index, autopct='%1.1f%%', startangle=90, colors=sns.color_palette("Set3", len(categoria_counts)))
    plt.title("Proporción de Productos por Categoría", fontsize=16)
    plt.axis('equal')  # Asegura que el gráfico sea un círculo perfecto
    plt.show()

   # Gráfico de pastel: Proporción de productos por Marca
    plt.figure(figsize=(8, 8))
    brand_counts = df['brand'].value_counts()
    plt.pie(brand_counts, labels=brand_counts.index, autopct='%1.1f%%', colors=sns.color_palette('Set3', len(brand_counts)))
    plt.title("Proporción de Productos por Marca")
    plt.show()

    # Gráfico que relaciona la subcategoría con la cantidad de productos
    plt.figure(figsize=(10, 6))
    subcategoria_counts = df['sub_category'].value_counts()  # Contamos cuántos productos hay por subcategoría
    subcategoria_counts.plot(kind='bar', color='orange')  # Generamos el gráfico de barras
    plt.title("Cantidad de Productos por Subcategoría")  # Título del gráfico
    plt.xlabel("Subcategoría")  # Etiqueta del eje X
    plt.ylabel("Cantidad de Productos")  # Etiqueta del eje Y
    plt.xticks(rotation=45, ha='right')  # Rotamos las etiquetas del eje X para que no se solapen
    plt.show()

    # Gráfico de línea: Frecuencia de Precios de Venta por Marca
    plt.figure(figsize=(12, 6))
    price_by_brand = df.groupby(['brand', 'sale_price']).size().reset_index(name='count')
    sns.lineplot(x='sale_price', y='count', hue='brand', data=price_by_brand, marker='o')
    plt.title("Frecuencia de Precios de Venta por Marca")
    plt.xlabel("Precio de Venta")
    plt.ylabel("Frecuencia de Productos")
    plt.xticks(rotation=45, ha='right')  # Rotamos las marcas del eje X para mayor visibilidad
    plt.legend(title='Marca', bbox_to_anchor=(1.05, 1), loc='upper left')  # Para mejor visibilidad de las leyendas
    plt.tight_layout()  # Ajuste del layout para evitar que se recorten las etiquetas
    plt.show()



# Función para mostrar el DataFrame
def mostrar_dataframe():
    df = db_to_dataframe()
    if df is not None:
        print("Contenido de la base de datos:")
        print(df)  # Mostrar el DataFrame
    else:
        print("No se pudo convertir la base de datos a DataFrame.")

# Función para obtener productos con precios en euros
def get_products_in_eur():
    euro_rate = obtener_valores_dolar()
    if euro_rate:
        with sqlite3.connect(DATABASE) as conn:
            products = conn.execute("SELECT * FROM product_catalog").fetchall()
            products_in_eur = []
            for product in products:
                product_dict = dict(product)
                product_dict['sale_price_euro'] = product_dict['sale_price'] * euro_rate
                product_dict['market_price_euro'] = product_dict['market_price'] * euro_rate
                products_in_eur.append(product_dict)
            return products_in_eur
    else:
        print("No se pudo obtener el valor del euro.")
        return []

# Función principal para inicializar la base de datos y la importación de productos
def iniciar():
    try:
        crear_tabla()
        importar_productos()
        print("Database and table creation successful, and products imported.")
    except Exception as e:
        print(f"An error occurred: {e}")

# Menú interactivo
def menu_interactivo():
    textoMenu = """
    Ingrese una opción:
    1. Crear tablas
    2. Importar productos desde CSV
    3. Consultar todos los productos
    4. Consultar un producto por ID
    5. Añadir un nuevo producto
    6. Actualizar un producto existente
    7. Eliminar un producto
    8. Mostrar productos con precios en euros
    9. Mostrar productos como DataFrame
    10. Ver gráficos descriptivos
    11. Obtener productos con precios en euros

    0. Salir
    """
    opcion = -1
    while opcion != 0:
        print(textoMenu)
        try:
            opcion = int(input("Seleccione una opción: "))
            if opcion == 1:
                crear_tabla()
            elif opcion == 2:
                importar_productos()
            elif opcion == 3:
                products = get_products()
                for product in products:
                    print(dict(product))
            elif opcion == 4:
                id = int(input("Ingrese el ID del producto: "))
                product = get_product(id)
                print(product)
            elif opcion == 5:
                add_product()
            elif opcion == 6:
                id = int(input("Ingrese el ID del producto a actualizar: "))
                update_product(id)
            elif opcion == 7:
                id = int(input("Ingrese el ID del producto a eliminar: "))
                delete_product(id)
            elif opcion == 8:
                euro_rate = obtener_valores_dolar()
                if euro_rate:
                    with sqlite3.connect(DATABASE) as conn:
                        conn.execute(''' 
                            UPDATE product_catalog
                            SET sale_price_euro = sale_price * ?, 
                                market_price_euro = market_price * ?
                        ''', (euro_rate, euro_rate))
                        conn.commit()
                    products = get_products()
                    for product in products:
                        print(product)
            elif opcion == 9:
                mostrar_dataframe()  # Llamamos a la nueva función para mostrar el DataFrame
            elif opcion == 10:
                df = db_to_dataframe()
                if df is not None:
                    graficos_descriptivos(df)  # Llamamos a la función para graficar
                else:
                    print("No se pudo generar los gráficos.")
            elif opcion == 0:
                print("Saliendo...")
            else:
                print("Opción no válida.")
        except ValueError:
            print("Ingrese un número válido.")




if __name__ == "__main__":
    iniciar()
    menu_interactivo()
