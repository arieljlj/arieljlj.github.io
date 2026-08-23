#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Calculadora de Tamano de Muestra para Investigaciones de Mercado
Basada en el libro: "Making Monitoring and Evaluation Systems Work" (World Bank, 2009)
Especificamente en la Guia Tecnica C8-2: "Calculate a Sample Size"

Este script calcula el tamano de muestra (n) requerido para medir cambios y tendencias
en proporciones a lo largo de rondas sucesivas de encuestas (estudios longitudinales/de tendencias).
"""

import sys
import math

def calcular_muestra(p1, cambio, alpha=0.05, beta=0.20, D=1.0, non_response_rate=0.0):
    """
    Realiza el calculo de tamano de muestra exacto utilizando la formula del libro.

    Parametros:
    p1 (float): Proporcion o prevalencia estimada en la linea base (ej. 0.15 para 15%)
    cambio (float): Magnitud del cambio que se desea detectar (ej. 0.10 para un cambio de 10%)
    alpha (float): Nivel de significancia (probabilidad de error Tipo I, default 5%)
    beta (float): Probabilidad de error Tipo II (1 - Poder estadistico, default 20% para 80% de poder)
    D (float): Efecto de diseno (Design Effect, default 1.0 para muestreo aleatorio simple)
    non_response_rate (float): Tasa estimada de no respuesta/rechazo (ej. 0.10 para 10%)

    Retorna:
    dict: Resultados detallados del calculo
    """
    # Determinacion de p2 (proporcion esperada en el futuro)
    p2 = p1 + cambio
    if p2 < 0.0 or p2 > 1.0:
        p2 = p1 - cambio  # El cambio puede ser reduccion
        if p2 < 0.0 or p2 > 1.0:
            raise ValueError("La proporcion resultante (p2) debe estar entre 0 y 1.")

    # Proporcion promedio (P)
    p_promedio = (p1 + p2) / 2.0

    # Delta (diferencia esperada)
    delta = abs(p2 - p1)
    delta_sq = delta ** 2

    # Valores de z-score correspondientes para una sola cola (segun las tablas del libro)
    # alpha = 0.05 -> Z_1-alpha = 1.645 (o 1.65 redondeado en el libro)
    # beta = 0.20 -> Z_1-beta = 0.84
    # Usamos los z-scores estandar precisos que utiliza el libro para recrear su tabla:
    z_alpha = 1.645 if abs(alpha - 0.05) < 0.01 else 1.96  # Si es 0.05 usamos 1.645
    z_beta = 0.84 if abs(beta - 0.20) < 0.01 else 1.28

    # Calculo de los terminos del numerador
    termino1 = z_alpha * math.sqrt(2 * p_promedio * (1.0 - p_promedio))
    termino2 = z_beta * math.sqrt(p1 * (1.0 - p1) + p2 * (1.0 - p2))

    numerador = (termino1 + termino2) ** 2

    # Tamano de muestra base (n_base)
    n_base = D * numerador / delta_sq

    # Ajuste por tasa de no respuesta
    if non_response_rate > 0.0:
        n_final = n_base / (1.0 - non_response_rate)
    else:
        n_final = n_base

    return {
        "p1": p1,
        "p2": p2,
        "p_promedio": p_promedio,
        "delta": delta,
        "z_alpha": z_alpha,
        "z_beta": z_beta,
        "n_base_exacta": n_base,
        "n_base_redondeada": round(n_base),
        "n_final_exacta": n_final,
        "n_final_redondeada": math.ceil(n_final)
    }

def mostrar_tabla_referencia():
    """Genera la tabla de referencia rapida equivalente a la Tabla C8-5 del libro."""
    prevalencias = [0.10, 0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80]
    cambios = [0.05, 0.10, 0.15, 0.20]

    print("\n" + "="*80)
    print("  TABLA DE REFERENCIA RAPIDA: TAMANO DE MUESTRA REQUERIDO (Formula del Libro)")
    print("  (Asume 95% Confianza (Z=1.645), 80% Poder (Z=0.84), D=1, Sin No-Respuesta)")
    print("="*80)
    print(f"{'Prevalencia':<15} | {'Cambio 5%':<12} | {'Cambio 10%':<12} | {'Cambio 15%':<12} | {'Cambio 20%':<12}")
    print("-"*80)

    for p1 in prevalencias:
        fila = [f"{int(p1*100):>3}%"]
        for c in cambios:
            try:
                res = calcular_muestra(p1, c)
                fila.append(f"{res['n_base_redondeada']:^12}")
            except Exception:
                fila.append(f"{'N/A':^12}")
        print(" | ".join(fila))
    print("="*80)

def main():
    # Si se pasan argumentos, procesarlos. Si no, correr demo e interactividad si aplica.
    import argparse
    parser = argparse.ArgumentParser(description="Calculadora de Muestra - M&E Systems")
    parser.add_argument("--p1", type=float, help="Prevalencia base (0.01 - 0.99)")
    parser.add_argument("--cambio", type=float, help="Cambio minimo detectable (0.01 - 0.50)")
    parser.add_argument("--deff", type=float, default=1.0, help="Efecto de diseno (D, default 1.0)")
    parser.add_argument("--nores", type=float, default=0.0, help="Tasa de no respuesta (0.00 - 0.90, default 0.00)")
    parser.add_argument("--tabla", action="store_true", help="Mostrar la tabla de referencia del libro")

    # Manejo para evitar error si no hay argumentos en el entorno offline
    if len(sys.argv) == 1:
        # Modo interactivo amigable o demostracion por defecto
        print("\n=== CALCULADORA DE MUESTRA PARA INVESTIGACION DE MERCADOS ===")
        print("Formula matematica oficial de 'Making M&E Systems Work' (Banco Mundial, 2009)\n")

        # Ejemplo de ejecucion por defecto (reproduce una celda de la Tabla C8-5)
        p1_demo = 0.20
        cambio_demo = 0.10
        res = calcular_muestra(p1_demo, cambio_demo)

        print("EJEMPLO DE CALCULO:")
        print(f"  * Prevalencia en Linea Base (P1): {p1_demo*100:.0f}%")
        print(f"  * Cambio minimo que se desea detectar: {cambio_demo*100:.0f}% (P2 = {res['p2']*100:.0f}%)")
        print(f"  * Nivel de confianza: 95% (Z_alpha = {res['z_alpha']})")
        print(f"  * Poder estadistico: 80% (Z_beta = {res['z_beta']})")
        print(f"  * Tamano de muestra teorico necesario (D=1): {res['n_base_redondeada']} encuestas.")

        mostrar_tabla_referencia()

        print("\nPara ejecutar este script de forma interactiva desde la terminal, use:")
        print("python3 calculadora_muestra.py --p1 0.15 --cambio 0.05 --deff 2.0 --nores 0.10")
        print("O pase '--tabla' para visualizar la matriz completa de tamanos de muestra del libro.")
        return

    args = parser.parse_args()

    if args.tabla:
        mostrar_tabla_referencia()
        return

    if args.p1 is None or args.cambio is None:
        parser.print_help()
        return

    try:
        res = calcular_muestra(args.p1, args.cambio, D=args.deff, non_response_rate=args.nores)
        print("\n" + "="*50)
        print("          RESULTADO DEL CALCULO DE MUESTRA")
        print("="*50)
        print(f"Prevalencia Linea Base (P1):  {res['p1']*100:.2f}%")
        print(f"Prevalencia Objetivo   (P2):  {res['p2']*100:.2f}%")
        print(f"Cambio Minimo Detectable:     {res['delta']*100:.2f}%")
        print(f"Proporcion Promedio (P):      {res['p_promedio']*100:.2f}%")
        print(f"Efecto de Diseno (D):         {args.deff:.2f}")
        print(f"Tasa de No Respuesta:         {args.nores*100:.2f}%")
        print("-"*50)
        print(f"Z-score Confianza (95%):      {res['z_alpha']}")
        print(f"Z-score Poder     (80%):      {res['z_beta']}")
        print("-"*50)
        print(f"Tamano Muestra Base (Teorico): {res['n_base_redondeada']}")
        print(f"Tamano Muestra Final Ajustado: {res['n_final_redondeada']} (recomendado)")
        print("="*50)
    except Exception as e:
        print(f"\nError al calcular: {e}", file=sys.stderr)

if __name__ == "__main__":
    main()
