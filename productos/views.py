import math
from bson import ObjectId
from bson.errors import InvalidId
from django.contrib import messages
from django.shortcuts import render, redirect
from pymongo.errors import PyMongoError
from .db import coleccion_productos

def validar_producto(datos):
    """Valida los datos recibidos del formulario."""
    nombre = datos.get("nombre", "").strip()
    precio_texto = datos.get("precio", "").strip()
    cantidad_texto = datos.get("cantidad", "").strip()

    errores = []

    if not nombre:
        errores.append("El nombre es obligatorio.")
    elif len(nombre) > 100:
        errores.append("El nombre no puede superar 100 caracteres.")

    try:
        precio = float(precio_texto)
        if not math.isfinite(precio) or precio < 0:
            errores.append("El precio debe ser un número válido y no negativo.")
    except ValueError:
        precio = None
        errores.append("Ingresa un precio válido.")

    try:
        cantidad = int(cantidad_texto)
        if cantidad < 0:
            errores.append("La cantidad no puede ser negativa.")
    except ValueError:
        cantidad = None
        errores.append("La cantidad debe ser un número grueso entero.")

    producto = {
        "nombre": nombre,
        "precio": precio,
        "cantidad": cantidad,
    }

    return producto, errores

def listar(request):
    """Consulta, mapea y muestra los productos."""
    try:
        datos = []
        for producto in coleccion_productos.find().sort("nombre", 1):
            # Cambiamos "id_str" por "id"
            producto["id"] = str(producto["_id"])
            datos.append(producto)

        return render(request, "productos/lista.html", {"productos": datos})
    except PyMongoError:
        messages.error(request, "Error de comunicación con MongoDB Atlas. Verifica accesos de red de tu clúster.")
        return render(request, "productos/lista.html", {"productos": []})

def crear(request):
    """Registra un producto."""
    if request.method == "POST":
        producto, errores = validar_producto(request.POST)

        if errores:
            for error in errores:
                messages.error(request, error)
            return render(request, "productos/formulario.html", {"producto": producto})

        try:
            coleccion_productos.insert_one(producto)
            messages.success(request, "Producto registrado correctamente.")
            return redirect("productos:listar")
        except PyMongoError:
            messages.error(request, "No fue posible guardar el producto.")
            return render(request, "productos/formulario.html", {"producto": producto})

    return render(request, "productos/formulario.html")

def editar(request, id):
    """Actualiza un producto existente asignando llaves limpias."""
    try:
        identificador = ObjectId(id)
    except (InvalidId, TypeError):
        messages.error(request, "El identificador no es válido.")
        return redirect("productos:listar")

    try:
        producto_actual = coleccion_productos.find_one({"_id": identificador})

        if producto_actual is None:
            messages.error(request, "El producto solicitado no existe.")
            return redirect("productos:listar")

        if request.method == "POST":
            producto, errores = validar_producto(request.POST)

            if errores:
                for error in errores:
                    messages.error(request, error)
                producto["id_str"] = str(identificador)
                return render(request, "productos/formulario.html", {"producto": producto})

            coleccion_productos.update_one({"_id": identificador}, {"$set": producto})
            messages.success(request, "Producto actualizado correctamente.")
            return redirect("productos:listar")

        producto_actual["id_str"] = str(producto_actual["_id"])
        return render(request, "productos/formulario.html", {"producto": producto_actual})
    except PyMongoError:
        messages.error(request, "Error al procesar la actualización.")
        return redirect("productos:listar")

def eliminar(request, id):
    """Elimina un producto mediante POST."""
    if request.method != "POST":
        messages.error(request, "La eliminación requiere peticiones seguras.")
        return redirect("productos:listar")

    try:
        identificador = ObjectId(id)
        resultado = coleccion_productos.delete_one({"_id": identificador})
        if resultado.deleted_count == 1:
            messages.success(request, "Producto eliminado correctamente.")
        else:
            messages.error(request, "El producto ya no se encuentra en el sistema.")
    except PyMongoError:
        messages.error(request, "No se pudo completar la eliminación.")

    return redirect("productos:listar")


