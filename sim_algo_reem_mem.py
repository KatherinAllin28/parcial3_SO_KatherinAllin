from collections import deque

marcos_libres = [0x0,0x1,0x2]
reqs = [ 0x00, 0x12, 0x64, 0x65, 0x8D, 0x8F, 0x19, 0x18, 0xF1, 0x0B, 0xDF, 0x0A ]
segmentos =[ ('.text', 0x00, 0x1A),
             ('.data', 0x40, 0x28),
             ('.heap', 0x80, 0x1F),
             ('.stack', 0xC0, 0x22),
           ]
def procesar(segmentos, reqs, marcos_libres):
    tamanio_pagina = 16  
    tabla_paginas = {}   
    cola_marcos = deque(marcos_libres)
    uso_fifo = deque()
    resultados = []

    tabla_segmentos = {}
    for nombre, base, limite in segmentos:
        tabla_segmentos[nombre] = (base, base + limite - 1)

    for req in reqs:
        segmento_encontrado = None
        for nombre, (inicio, fin) in tabla_segmentos.items():
            if inicio <= req <= fin:
                segmento_encontrado = nombre
                base_segmento = inicio
                break

        if not segmento_encontrado:
            resultados.append((req, 0x1FF, "Segmention Fault"))
            break

        offset = req - base_segmento
        nro_pagina = offset // tamanio_pagina
        offset_en_pagina = offset % tamanio_pagina
        clave_pagina = (segmento_encontrado, nro_pagina)

        if clave_pagina in tabla_paginas:
            marco = tabla_paginas[clave_pagina]
            direccion_fisica = marco * tamanio_pagina + offset_en_pagina
            resultados.append((req, direccion_fisica, "Marco ya estaba asignado"))
        else:
            if cola_marcos:
                marco = cola_marcos.popleft()
                accion = "Marco libre asignado"
            else:
                pagina_reemplazada = uso_fifo.popleft()
                marco = tabla_paginas.pop(pagina_reemplazada)
                accion = "Marco asignado"

            tabla_paginas[clave_pagina] = marco
            uso_fifo.append(clave_pagina)
            direccion_fisica = marco * tamanio_pagina + offset_en_pagina
            resultados.append((req, direccion_fisica, accion))

    return resultados

def print_results(results):
    for result in results:
        print(f"Req: {result[0]:#04x} Direccion Fisica: {result[1]:#04x} Acción: {result[2]}")

if __name__ == '__main__':
    results = procesar(segmentos, reqs, marcos_libres)
    print_results(results)
