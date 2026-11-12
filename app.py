"""BASE EDUCATIVA INSEGURA. Corregir los TODO antes de la entrega."""
import json
from seguridad import crear_hash, verificar_clave 
from pathlib import Path
from datetime import datetime


RAIZ = Path(__file__).resolve().parent
DATOS = RAIZ / "inventario.json"
USUARIOS = RAIZ / "usuarios.json"
LOG = RAIZ / "auditoria.jsonl"



def cargar_inventario():
    # TODO: controlar archivo ausente y JSON inválido. No sobrescribirlos.
    try:
        return json.loads(DATOS.read_text(encoding="utf-8"))

    except FileNotFoundError:
        print("Error: no se encontró el archivo de inventario.")
        return None

    except json.JSONDecodeError:
        print("Error: el archivo de inventario contiene JSON inválido.")
        return None




def guardar_inventario(productos):
    return DATOS.write_text(json.dumps(productos, indent=2,), encoding="utf-8")


def registrar_evento(usuario, accion, resultado, **detalles):
    # TODO: guardar un objeto JSON por línea; fecha/hora, usuario, acción,
    # resultado y detalles no sensibles. Nunca guardar contraseña ni hash.
      evento = {
        "fecha": datetime.now().isoformat(timespec="seconds"),
        "usuario": usuario,
        "accion": accion,
        "resultado": resultado
        }

      evento.update(detalles)

      with open(LOG, "a", encoding="utf-8") as archivo:
        archivo.write(json.dumps(evento, ensure_ascii=False) + "\n")


def autenticar(nombre, clave):
    # TODO: integrar seguridad.py y migrar usuarios.json sin claves legibles.
    usuarios = json.loads(USUARIOS.read_text(encoding="utf-8"))

    for usuario in usuarios:
        if usuario["usuario"] == nombre:
            if verificar_clave(usuario["clave_hash"], clave):
                registrar_evento(nombre, "login", "exitoso")
                return {
                    "usuario": nombre,
                    "rol": usuario["rol"]
                }
            break

    registrar_evento(nombre, "login", "fallido")
    print("Credenciales incorrectas.")
    return None


def consultar_inventario(sesion):
    # TODO: rechazar si no existe sesión válida.
    if sesion is None:
        print("Acceso denegado.")
        return

    productos = cargar_inventario()

    if productos is None:
        return

    for producto in productos:
        print(producto["id"], producto["nombre"], producto["cantidad"])


def modificar_cantidad(sesion, identificador, entrada):
    # TODO: verificar sesión y rol AQUÍ, antes de modificar.
    # TODO: validar entero entre 0 y 1000, sin interrumpir el programa.

    if sesion is None:
        print("Acceso denegado.")
        registrar_evento(
            "anonimo",
            "modificar",
            "rechazado",
            producto=identificador
        )
        return False

    if sesion["rol"] != "admin":
        print("No autorizado.")
        registrar_evento(
            sesion["usuario"],
            "modificar",
            "rechazado",
            producto=identificador
        )
        return False

    try:
        cantidad = int(entrada)

        if cantidad < 0 or cantidad > 1000:
            print("La cantidad debe estar entre 0 y 1000.")
            return False

    except ValueError:
        print("La cantidad debe ser un entero.")
        return False

    productos = cargar_inventario()

    if productos is None:
        return False

    for producto in productos:
        if producto["id"] == identificador:

            anterior = producto["cantidad"]
            producto["cantidad"] = cantidad

            guardar_inventario(productos)

            registrar_evento(
                sesion["usuario"],
                "modificar",
                "exitoso",
                producto=identificador,
                anterior=anterior,
                nueva=cantidad
            )

            print("Cantidad actualizada.")
            return True

    print("Producto no encontrado.")

    registrar_evento(
        sesion["usuario"],
        "modificar",
        "fallido",
        producto=identificador
    )

    return False


def main():
    print("Inventario académico — BASE CON DEBILIDADES")
    print("Estudiante:", input("Escriba su nombre: "))
    sesion = None
    while True:
        if sesion is None:
            nombre = input("Usuario (o salir): ")
            if nombre == "salir":
                break
            sesion = autenticar(nombre, input("Contraseña de prueba: "))
            continue
        print("1. Consultar | 2. Modificar | 3. Cerrar sesión | 0. Salir")
        opcion = input("Opción: ")
        if opcion == "1":
            consultar_inventario(sesion)
        elif opcion == "2":
            identificador = input("ID del producto: ")
            entrada = input("Nueva cantidad: ")
            modificar_cantidad(sesion, identificador, entrada)
        elif opcion == "3":
            sesion = None
        elif opcion == "0":
            break
        else:
            print("Opción inválida.")


if __name__ == "__main__":
    main()
