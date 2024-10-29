#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
-------------------------------------------------------------------------------
-------------- Análisis Descriptivo y Predicción de Desocupación --------------

--      Machine Learning para Economistas - Universidad de San Andrés        --


-     @autores: Eitan Salischiker, Tomás Marotta y Juan Segundo Zapiola       -

-                      Fecha: 15 de Noviembre de 2024                         -
-------------------------------------------------------------------------------
"""


import os
import pandas as pd
import matplotlib.pyplot as plt

os.chdir('/Users/juansegundozapiola/Documents/Maestria/Big Data/BigData/TPs/TP3')


'''
Parte I: Analizando la base
'''

#####Inciso 1 (ver documento)

#####Inciso 2

#2.a)

#Abrimos la base del primer trimestre para 2024 y 2004.

T1_2024 = pd.read_excel("usu_individual_T124.xlsx") 
T1_2004 = pd.read_stata("Individual_t104.dta")

T1_2024.info(verbose = True)
T1_2004.info(verbose = True)


print(T1_2024['AGLOMERADO'].unique()) #13 es Gran Córdoba
print(T1_2004['aglomerado'].unique()) ##13 es Gran Córdoba


#Nos quedamos con las observaciones correspondientes al aglomerado de Gran Córdoba

T1_2024 = T1_2024[T1_2024['AGLOMERADO'] == 13]
T1_2004 = T1_2004[T1_2004['aglomerado'] == 'Gran Córdoba']

T1_2004.columns = T1_2004.columns.str.upper() #las variables de 2004 estan en lower case las pasamos a upper case. 

#Veo que variables hay diferentes en ambas bases:

if set(T1_2024.columns) == set(T1_2004.columns):
    print("Ambas bases tienen las mismas columnas.")
else:
    print("Las bases no tienen las mismas columnas.")
    print("Columnas en T1_2024 pero no en T1_2004:", set(T1_2024.columns) - set(T1_2004.columns))
    print("Columnas en T1_2004 pero no en T1_2024:", set(T1_2004.columns) - set(T1_2024.columns))


# A partir del tercer trimestre del año 2010, las variables referidas al Plan Jefes y Jefas de Hogar(Pj1_1, Pj2_1 y Pj3_1) dejaron de ser relevadas


#Unimos ambos trimestres en una sola base: 

T1_2024_2004 = pd.concat([T1_2024, T1_2004], ignore_index=True)


#Correcciones para mejorar la base:

#mismo diccionario para ambas bases: Genero
frecuencia_genero = T1_2024_2004['CH04'].value_counts()
print(frecuencia_genero) 
mapa_genero = {1: "Varón", 
               2: "Mujer"}
T1_2024_2004['CH04'] = T1_2024_2004['CH04'].replace(mapa_genero)


# Convertir la columna 'CH06' a numérica, colocando NaN en valores no numéricos
T1_2024_2004['CH06'] = pd.to_numeric(T1_2024_2004['CH06'], errors='coerce')


#mismo diccionario para ambas bases: estado civil
frecuencia_estado = T1_2024_2004['CH07'].value_counts()
print(frecuencia_estado) 
mapa_estado = {1: "Unido", 
               2: "Casado",
               3: "Separado o divorciado", 
               4:"Viudo", 
               5:"Soltero"}
T1_2024_2004['CH07'] = T1_2024_2004['CH07'].replace(mapa_estado)

#mismo diccionario para ambas bases: nivel educativo
frecuencia_educacion = T1_2024_2004['CH12'].value_counts()
print(frecuencia_educacion) 
mapa_educacion = {
    1: "Jardín/preescolar",
    2: "Primario",
    3: "EGB",
    4: "Secundario",
    5: "Polimodal",
    6: "Terciario",
    7: "Universitario",
    8: "Posgrado universitario",
    9: "Educación especial (discapacitado)"
}
T1_2024_2004['CH12'] = T1_2024_2004['CH12'].replace(mapa_educacion)


#mismo diccionario para ambas bases: nivel_ed
frecuencia_instruccion = T1_2024_2004['NIVEL_ED'].value_counts()
print(frecuencia_instruccion) 
mapa_instruccion = {
    1: "Primario incompleto (incluye educación especial)",
    2: "Primario completo",
    3: "Secundario incompleto",
    4: "Secundario completo",
    5: "Superior universitario incompleto",
    6: "Superior universitario completo",
    7: "Sin instrucción",
    9: "Ns/Nr"
}
T1_2024_2004['NIVEL_ED'] = T1_2024_2004['NIVEL_ED'].replace(mapa_instruccion)

#Quiero esta columna como enteros
T1_2024_2004['ANO4'] = T1_2024_2004['ANO4'].astype(int)

#2.b)

#veamos cuantos missings hay en cada variable:
missing_data = T1_2024_2004.isnull().sum()
print(missing_data)

#Eliminamos aquellas observaciones con missings o que no tienen sentido:   
    
#Monto de ingreso total individual - P47T:

T1_2024_2004 = T1_2024_2004[T1_2024_2004['P47T'] >= 0] #Elimino ingresos negativos y nan

#Edad Individuos - CH06:

T1_2024_2004 = T1_2024_2004[T1_2024_2004['CH06'] >= 0] #Elimino edades negativas y nan



#2.c)


#Gráfico de barras mostrando la composición por sexo para 2004 y 2024

# Agrupar y sumar ingresos por año y género
comp_sexo = T1_2024_2004.groupby(['ANO4', 'CH04']).size().unstack()

# Crear el gráfico de barras
ax = comp_sexo.plot(kind='bar', title='Composición del sexo para 2004 y 2024')
ax.set_xlabel('Año', color='grey')
ax.set_ylabel('Individuos Totales', color='grey')
ax.legend(["Mujeres", "Varones"])
plt.xticks(rotation=0)

plt.show()


#2.d)

















