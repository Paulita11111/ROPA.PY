import requests

class Producto:
    def __init__(self, index, product, category, sub_category, brand, sale_price, market_price, type, rating, description):
        self.index = index
        self.producto = product
        self.categoria = category
        self.sub_categoria = sub_category
        self.marca = brand
        self.precio_venta = sale_price
        self.precio_compra = market_price
        self.tipo = type
        self.puntaje = rating
        self.descripcion = description

#lo paso a diccionario aca porque sino lo voy a tener que hacer despues en cada metodo agregar, actualizar, elkminar, etc
#es mas sencillo ya tenerlo asi y hacerlo ua vez y no tener que hacerlo en cada metodo
    def describe(self):
        return {
            "index": self.index,
            "product": self.producto,
            "category": self.categoria,
            "sub_category": self.sub_categoria,            
            "brand": self.marca,
            "sale_price": self.precio_venta,
            "market_price": self.precio_compra,
            "type": self.tipo,
            "rating": self.puntaje,
            "description": self.descripcion
            }

def obtener_productos(base_url): #va a tener que tener un llamado a la API que creamos nosotos 
    url = f"{base_url}/products" #f es otra forma de concatenar strings
    response = requests.get(url)
    if response.status_code == 200:
        productos = response.json() #el backend me manda la lista de produtcos que se me guardan aca en productos
        productos_transformados = []
        for producto in productos:
            productos_transformados.append(crear_producto(producto))
        return productos_transformados
    return None


def obtener_producto_por_id(base_url, id_producto):
    response = requests.get(f"{base_url}/product/{id_producto}")
    if response.status_code == 200:
        return response.json()
    return None


#tomo un objeto de la clase producto como parametro
#convierto el objeto en el diccionario que cree arriba en productos_super
def agregar_producto(base_url, product_index, product_producto, product_category, product_sub_category, product_brand, product_sale_price, product_market_price, product_type, product_rating, product_description):
    url = f"{base_url}/products"
    payload = {"index": product_index, "product": product_producto, "category": product_category, "sub_category": product_sub_category, "brand": product_brand, "sale_price": product_sale_price, "market_price": product_market_price, "type": product_type, "rating": product_rating, "description": product_description}
    response = requests.post(url, json=payload)
#con el POST le estoy haciendo una solicitud a la API usando el request.post() para AGREGAR un producto nuevo a la base de datos
#esto lo hago a traves de la URL
    if response.status_code == 200:
        print("Producto agregado exitosamente")
    else:
        print("Error al agregar el producto")


#toma el diccionario de mi backend a traves del response.json() de obtener_productos para retornar un obejto producto con los datos del diccionario
def crear_producto(producto):
    return Producto(producto["index"], producto["product"], producto["category"], producto["sub_category"], producto["brand"], producto["sale_price"], producto["market_price"], producto["type"], producto["rating"], producto["description"])


def actualizar_producto(base_url, id_producto, producto_actualizado):
    url = f"{base_url}/products/{id_producto}"
    response = requests.put(url, json=producto_actualizado.describe())
    if response.status_code == 200:
        print("Producto actualizado exitosamente")
    else:
        print("Error al actualizar el producto")

def eliminar_producto(base_url, id_producto):
    url = f"{base_url}/products/{id_producto}"
    response = requests.delete(url)
    if response.status_code == 200:
        print("Producto eliminado exitosamente")
    else:
        print("Error al eliminar el producto")

def main():
    base_url = "http://127.0.0.1:4000"
    while True:
        print("Opciones")
        print("1: Ver todos los productos")
        print("2: Ver un producto por ID")
        print("3: Agregar un producto nuevo")
        print("4: Actualizar un producto existente")
        print("5: Eliminar un producto existente")
        print("6: Salir")
        
       
        opcion = int(input("Selecciona una opción: "))

      #para hacer esta parte tengo que ver como unir la parte del front con el back  
        if opcion == 1:
            print("Ver productos")
            productos = obtener_productos(base_url)
            if productos:
                for producto in productos:
                    print(producto.describe())
            else:
                print("No se pudieron obtener los productos")

        elif opcion == 2:
            try:
                id_producto = int(input("Ingrese el ID del producto que desea ver: "))
                producto = obtener_producto_por_id(base_url, id_producto)
                if producto:
                    print(f"Producto encontrado: {producto}")
                else:
                    print("Producto no encontrado")
            except ValueError:
                print("Error: Entrada de datos no válida")


        elif opcion == "3":
            print("Agregar un producto nuevo")
            try:
                producto = Producto(
                    float(input("Ingrese el numero de indice del producto: ")),
                    input("Ingrese el nombre del producto: "),
                    input("Ingrese la categoría del producto: "),
                    input("Ingrese la subcategoría del producto: "),
                    input("Ingrese la marca del producto: "),
                    float(input("Ingrese el precio de venta del producto: ")),
                    float(input("Ingrese el precio de compra del producto: ")),                    
                    input("Ingrese el tipo del producto (parte de arriba/parte de abajo): "),
                    float(input("Ingrese el puntaje del producto: ")),
                    input("Ingrese la descripción del producto: "))
                agregar_producto(base_url, producto)
            except ValueError:
                print("Error: Información no válida")

        elif opcion == "4":
            try:
                print("Actualizar producto existente")
                id_producto = int(input("Ingrese el ID del producto que desea actualizar: "))
                index = int(input("Ingrese el nuevo índice del producto: "))
                product = input("Ingrese el nuevo nombre del producto: ")
                category = input("Ingrese la nueva categoría del producto: ")
                sub_category = input("Ingrese la nueva subcategoría del producto: ")
                brand = input("Ingrese la nueva marca del producto: ")
                sale_price = float(input("Ingrese el nuevo precio de venta del producto: "))
                market_price = float(input("Ingrese el nuevo precio de compra del producto: "))
                tipo = input("Ingrese el nuevo tipo del producto: ")
                rating = float(input("Ingrese el nuevo puntaje del producto: "))
                description = input("Ingrese la nueva descripción del producto: ")
                producto_actualizado = Producto(
                    index,
                    product,
                    category,
                    sub_category,
                    brand,
                    sale_price,
                    market_price,
                    tipo,
                    rating,
                    description,
                )
                actualizar_producto(base_url, id_producto, producto_actualizado)
            except ValueError:
                print("Error: Información no válida")

        elif opcion == "5":
            try:
                print("Eliminar un producto existente")
                id_producto = int(input("Ingrese el ID del producto que desea eliminar: "))
                eliminar_producto(base_url, id_producto)
            except ValueError:
                print("Error: Entrada de datos no válida.")

        elif opcion == "6":
            print("Saliendo...")
            break

        if __name__ == "__main__":
            main()
       
