from datetime import datetime

def obtener_fecha_actuacion_reciente(tabla_texto):
    """
    Procesa el texto de la tabla y si encuentra una fecha de actuación
    menor a 365 días imprime el mensaje y retorna la fecha encontrada.
    Si no hay, retorna None.
    """
    lineas = tabla_texto.split('\n')
    print("Líneas encontradas en la tabla:")
    for linea in lineas:
        print(f"-> {linea}")
        if linea.strip().startswith('20') and len(linea.strip()) >= 10:
            fecha_str = linea.strip()[:10]
            print(f"Intentando procesar fecha: {fecha_str}")
            try:
                fecha_actual = datetime.now()
                fecha_actuacion = datetime.strptime(fecha_str, "%Y-%m-%d")
                dias_diferencia = (fecha_actual - fecha_actuacion).days
                print(f"Diferencia de días: {dias_diferencia}")
                if dias_diferencia < 365:
                    print(f"\nSu radicación tuvo una actuación recientemente el día {fecha_str}")
                    return fecha_str
            except ValueError:
                print(f"Formato de fecha inválido: {fecha_str}")
                continue
    print("No se encontró actuación reciente.")
    return None