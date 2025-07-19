from datetime import datetime

def obtener_fecha_actuacion_reciente(tabla_texto):
    """
    Procesa el texto de la tabla y retorna solo la fecha de actuación más reciente
    (la última fecha encontrada que cumpla la condición). Si no hay, retorna None.
    """
    lineas = tabla_texto.split('\n')
    fechas = []
    for linea in lineas:
        if linea.strip().startswith('20') and len(linea.strip()) >= 10:
            fecha_str = linea.strip()[:10]
            try:
                fecha_actual = datetime.now()
                fecha_actuacion = datetime.strptime(fecha_str, "%Y-%m-%d")
                dias_diferencia = (fecha_actual - fecha_actuacion).days
                if dias_diferencia <= 75:  # Considera fechas dentro de los últimos 75 días
                    fechas.append((fecha_actuacion, fecha_str))
            except ValueError:
                continue
    if fechas:
        # Selecciona la fecha más reciente (la de mayor valor)
        fecha_mas_reciente = max(fechas, key=lambda x: x[0])[1]
        print(f"\nSu radicación tuvo una actuación recientemente el día {fecha_mas_reciente}")
        return fecha_mas_reciente
    print("No se encontró actuación reciente.")
    return None