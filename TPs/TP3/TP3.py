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
import seaborn as sns

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


##----Correcciones en agrupacion de bases:

#mismo diccionario para ambas bases: Genero
frecuencia_genero = T1_2024_2004['CH04'].value_counts()
print(frecuencia_genero) 
mapa_genero = {"Varón": 1, 
               "Mujer": 2}
T1_2024_2004['CH04'] = T1_2024_2004['CH04'].replace(mapa_genero)


# Convertir la columna 'CH06' a numérica, colocando NaN en valores no numéricos
T1_2024_2004['CH06'] = pd.to_numeric(T1_2024_2004['CH06'], errors='coerce')


#mismo diccionario para ambas bases: estado civil
frecuencia_estado = T1_2024_2004['CH07'].value_counts()
print(frecuencia_estado) 
mapa_estado = { "Unido": 1, 
                "Casado": 2,
                "Separado o divorciado": 3, 
               "Viudo": 4, 
               "Soltero": 5}
T1_2024_2004['CH07'] = T1_2024_2004['CH07'].replace(mapa_estado)

#mismo diccionario para ambas bases: nivel educativo
frecuencia_educacion = T1_2024_2004['CH12'].value_counts()
print(frecuencia_educacion) 
mapa_educacion = {
    "Jardín/Preescolar": 1,
    "Primario": 2,
    "EGB": 3,
    "Secundario": 4,
    "Polimodal": 5,
    "Terciario": 6,
    "Universitario": 7,
    "Posgrado Universitario": 8,
    "Educación especial (discapacitado)": 9
}
T1_2024_2004['CH12'] = T1_2024_2004['CH12'].replace(mapa_educacion)


#mismo diccionario para ambas bases: nivel_ed
frecuencia_instruccion = T1_2024_2004['NIVEL_ED'].value_counts()
print(frecuencia_instruccion) 
mapa_instruccion = {
    "Primaria Incompleta (incluye educación especial)": 1,
    "Primaria Completa": 2,
    "Secundaria Incompleta": 3,
    "Secundaria Completa": 4,
    "Superior Universitaria Incompleta": 5,
    "Superior Universitaria Completa": 6,
    "Sin instrucción": 7,
    "Ns/Nr": 9
}
T1_2024_2004['NIVEL_ED'] = T1_2024_2004['NIVEL_ED'].replace(mapa_instruccion)

#mismo diccionario para ambas bases: cobertura médica
frecuencia_cob = T1_2024_2004['CH08'].value_counts()
print(frecuencia_cob) 
mapa_cobertura_salud = {
    "Obra social (incluye PAMI)": 1,
    "Mutual/Prepaga/Servicio de emergencia": 2,
    "Planes y seguros públicos": 3,
    "No paga ni le descuentan": 4,
    "Ns./Nr.": 9,
    "Obra social y mutual/prepaga/servicio de emergencia": 12,
    "Obra social y planes y seguros públicos": 13,
    "Mutual/prepaga/servicio de emergencia/Planes y seguros públicos": 23,
    "Obra social, mutual/prepaga/servicio de emergencia y planes y seguros públicos": 123
}

T1_2024_2004['CH08'] = T1_2024_2004['CH08'].replace(mapa_cobertura_salud)


frecuencia_EST = T1_2024_2004['ESTADO'].value_counts()
print(frecuencia_EST) 
mapa_actividad = {
    "Entrevista individual no realizada (no respuesta al cuestion": 0,
    "Ocupado": 1,
    "Desocupado": 2,
    "Inactivo": 3,
    "Menor de 10 años": 4
}
T1_2024_2004['ESTADO'] = T1_2024_2004['ESTADO'].replace(mapa_actividad)

frecuencia_CAT = T1_2024_2004['CAT_INAC'].value_counts()
print(frecuencia_CAT) 
mapa_condicion = {
    "Jubilado/pensionado": 1,
    "Rentista": 2,
    "Estudiante": 3,
    "Ama de casa": 4,
    "Menor de 6 años": 5,
    "Discapacitado": 6,
    "Otros": 7
}
T1_2024_2004['CAT_INAC'] = T1_2024_2004['CAT_INAC'].replace(mapa_condicion)


#Quiero esta columna como enteros
T1_2024_2004['ANO4'] = T1_2024_2004['ANO4'].astype(int)
T1_2024_2004['CH12'] = T1_2024_2004['CH12'].astype(int)
T1_2024_2004['CAT_INAC'] = T1_2024_2004['CAT_INAC'].astype(int)

##----


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

# Agrupo y sumo cantidad de individuos por género para cada año
comp_sexo = T1_2024_2004.groupby(['ANO4', 'CH04']).size().unstack()

# Creo el gráfico de barras
ax = comp_sexo.plot(kind='bar', title='Composición del sexo para 1er Trimestre 2004 y 2024')
ax.set_xlabel('Año', color='grey')
ax.set_ylabel('Individuos Totales', color='grey')
ax.legend(["Mujeres", "Varones"])
plt.xticks(rotation=0)
plt.show()


#2.d)

variables_interes = ['CH04', 'CH06', 'CH07', 'CH08', 'NIVEL_ED', 'ESTADO', 'CAT_INAC', 'IPCF']

# Filtro los datos para 2004 y calculo la correlación
data_2004 = T1_2024_2004[T1_2024_2004['ANO4'] == 2004][variables_interes]
corr_2004 = data_2004.corr()

#Mismo para 2024
data_2024 = T1_2024_2004[T1_2024_2004['ANO4'] == 2024][variables_interes]
corr_2024 = data_2024.corr()

# Crear el heatmap para 2004
plt.figure(figsize=(10, 8))
ax1 = sns.heatmap(
    corr_2004, 
    vmin=-1, vmax=1, center=0,
    cmap=sns.diverging_palette(20, 220, n=200),
    square=True,
    annot=True,  # Opcional: muestra los valores de correlación en el heatmap
    fmt=".2f"    # Formato para mostrar los valores con 2 decimales
)
ax1.set_xticklabels(ax1.get_xticklabels(), rotation=45, horizontalalignment='right')
ax1.set_title('Matriz de Correlación - Año 2004')
plt.show()

# Crear el heatmap para 2024
plt.figure(figsize=(10, 8))
ax2 = sns.heatmap(
    corr_2024, 
    vmin=-1, vmax=1, center=0,
    cmap=sns.diverging_palette(20, 220, n=200),
    square=True,
    annot=True,  # Opcional: muestra los valores de correlación en el heatmap
    fmt=".2f"    # Formato para mostrar los valores con 2 decimales
)
ax2.set_xticklabels(ax2.get_xticklabels(), rotation=45, horizontalalignment='right')
ax2.set_title('Matriz de Correlación - Año 2024')
plt.show()















