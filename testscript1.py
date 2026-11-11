from ApplicaciondeInventario.app import autenticar, modificar_cantidad, consultar_inventario

sesion = autenticar("user", "UserDemo2700!")

resultado = modificar_cantidad(sesion, "P001", "99")

print("Resultado:", resultado)

resultado = modificar_cantidad(None, "P001", "99")

print("Resultado:", resultado)

consultar_inventario(None)