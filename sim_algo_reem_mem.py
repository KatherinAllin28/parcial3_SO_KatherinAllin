from collections import deque

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
        print(f"Req: {result[0]:#0{4}x} Direccion Fisica: {result[1]:#0{4}x} Acción: {result[2]}")

def parse_hex_list(input_str):
    return [int(x.strip(), 16) for x in input_str.split(',') if x.strip()]

def parse_segmentos(input_str):
    segmentos = []
    for s in input_str.split(';'):
        nombre, base, limite = s.strip().split(',')
        segmentos.append((nombre.strip(), int(base, 16), int(limite, 16)))
    return segmentos

if __name__ == '__main__':
    print("Ingresa los marcos libres (separados por comas, en hexadecimal, ej: 0x2,0x1,0x0):")
    marcos_input = input()
    marcos_libres = parse_hex_list(marcos_input)

    print("Ingresa los requerimientos (separados por comas, en hexadecimal, ej: 0x00,0x12,...):")
    reqs_input = input()
    reqs = parse_hex_list(reqs_input)

    print("Ingresa los segmentos como: nombre,base,limite separados por punto y coma. Ej: .text,0x00,0x1A;.data,0x40,0x28")
    segmentos_input = input()
    segmentos = parse_segmentos(segmentos_input)

    results = procesar(segmentos, reqs, marcos_libres)
    print_results(results)