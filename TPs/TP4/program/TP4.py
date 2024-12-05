#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
-------------------------------------------------------------------------------
----------- Clasificación y Regularizacion de Desocupación en la EPH ----------

--      Machine Learning para Economistas - Universidad de San Andrés        --


-     @autores: Eitan Salischiker, Tomás Marotta y Juan Segundo Zapiola       -

-                      Fecha: 17 de Diciembre de 2024                         -
-------------------------------------------------------------------------------

----------
  ÍNDICE
----------

0. Seteo del espacio de trabajo
1. Parte I: Analizando la base
2. Parte II: Clasificación

--------------------------------
0. SETEO DEL ESPACIO DE TRABAJO 
--------------------------------
'''

## Importamos los paquetes necesarios

# Manejo de archivos y directorios
import os

# Visualización de datos
import seaborn as sns

# Manejo de datos
import pandas as pd
import numpy as np

# Modelos de Machine Learning
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.preprocessing import scale
from sklearn.linear_model import Lasso, LassoCV, Ridge, RidgeCV
from sklearn.metrics import mean_squared_error
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import GridSearchCV
from sklearn.model_selection import KFold


# Métricas y evaluación de modelos
from sklearn.metrics import (
    confusion_matrix, 
    accuracy_score, 
    roc_curve, 
    auc
)

# Gráficos
import matplotlib.pyplot as plt
import seaborn as sns

#pip install ISLP
from ISLP import load_data


## Definimos el directorio de trabajo
os.chdir(r'/Users/juansegundozapiola/Documents/Maestria/Big Data/BigData/TPs/TP4')



'''
--------------------------------
 1. Parte I: Analizando la base
--------------------------------
'''


#Inciso 2

# Abrimos la base de HOGARES del primer trimestre para 2024 y 2004.
T1_2024 = pd.read_excel("input/usu_hogar_T124.xlsx") 
T1_2004 = pd.read_stata("input/hogar_t104.dta")

# Resumen de la información del Data Frame
T1_2024.info(verbose = True)
T1_2004.info(verbose = True)

# Identificamos el ID de el aglomerado de Gran Córdoba.
print(T1_2024['AGLOMERADO'].unique()) #13 es Gran Córdoba
print(T1_2004['aglomerado'].unique()) ##13 es Gran Córdoba

# Nos quedamos con las observaciones correspondientes al aglomerado de Gran Córdoba
T1_2024 = T1_2024[T1_2024['AGLOMERADO'] == 13]
T1_2004 = T1_2004[T1_2004['aglomerado'] == 'Gran Córdoba']

# Pasamos las variables de 2004 de lower case a upper case.
T1_2004.columns = T1_2004.columns.str.upper() 

# Vemos qué variables son diferentes en ambas bases:
if set(T1_2024.columns) == set(T1_2004.columns):
    print("Ambas bases tienen las mismas columnas.")
else:
    print("Las bases no tienen las mismas columnas.")
    print("Columnas en T1_2024 pero no en T1_2004:", set(T1_2024.columns) 
          - set(T1_2004.columns))
    print("Columnas en T1_2004 pero no en T1_2024:", set(T1_2004.columns) 
          - set(T1_2024.columns))

'''
Columnas en T1_2024 pero no en T1_2004: {'PONDIH'}
Columnas en T1_2004 pero no en T1_2024: {'IDIMPH'}
'''

#Unimos ambas bases en una
HOGAR_T1_2024_2004 = pd.concat([T1_2024, T1_2004], ignore_index=True)


# Abrimos la base INDIVIDUAL del primer trimestre para 2024 y 2004.
I_T1_2024 = pd.read_excel("input/usu_individual_T124.xlsx") 
I_T1_2004 = pd.read_stata("input/Individual_t104.dta")

# Resumen de la información del Data Frame
I_T1_2024.info(verbose = True)
I_T1_2004.info(verbose = True)

# Identificamos el ID de el aglomerado de Gran Córdoba.
print(I_T1_2024['AGLOMERADO'].unique()) #13 es Gran Córdoba
print(I_T1_2004['aglomerado'].unique()) ##13 es Gran Córdoba

# Nos quedamos con las observaciones correspondientes al aglomerado de Gran Córdoba
I_T1_2024 = I_T1_2024[I_T1_2024['AGLOMERADO'] == 13]
I_T1_2004 = I_T1_2004[I_T1_2004['aglomerado'] == 'Gran Córdoba']

# Pasamos las variables de 2004 de lower case a upper case.
I_T1_2004.columns = I_T1_2004.columns.str.upper() 


# Unimos ambos trimestres en una sola base: 
IND_T1_2024_2004 = pd.concat([I_T1_2024, I_T1_2004], ignore_index=True)


#MERGING: merge la base de HOGARES e INDIVIDUOS en una.

HOG_IND_T1_2024_2004 = pd.merge(
    IND_T1_2024_2004, 
    HOGAR_T1_2024_2004, 
    on=['CODUSU', 'NRO_HOGAR'], 
    how='inner'
)

##----Correcciones en agrupacion de bases:

# Mismo diccionario para ambas bases: Género
frecuencia_genero = HOG_IND_T1_2024_2004['CH04'].value_counts()
print(frecuencia_genero) 
mapa_genero = {"Varón": 1, 
               "Mujer": 2}
HOG_IND_T1_2024_2004['CH04'] = HOG_IND_T1_2024_2004['CH04'].replace(mapa_genero)

# Convertir la columna 'CH06' a numérica, colocando NaN en valores no numéricos
HOG_IND_T1_2024_2004['CH06'] = pd.to_numeric(HOG_IND_T1_2024_2004['CH06'], errors='coerce')

# Mismo diccionario para ambas bases: Estado Civil
frecuencia_estado = HOG_IND_T1_2024_2004['CH07'].value_counts()
print(frecuencia_estado) 
mapa_estado = { "Unido": 1, 
                "Casado": 2,
                "Separado o divorciado": 3, 
               "Viudo": 4, 
               "Soltero": 5}
HOG_IND_T1_2024_2004['CH07'] = HOG_IND_T1_2024_2004['CH07'].replace(mapa_estado)

# Mismo diccionario para ambas bases: Nivel Educativo
frecuencia_educacion = HOG_IND_T1_2024_2004['CH12'].value_counts()
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
HOG_IND_T1_2024_2004['CH12'] = HOG_IND_T1_2024_2004['CH12'].replace(mapa_educacion)

# Mismo diccionario para ambas bases: nivel_ed
frecuencia_instruccion = HOG_IND_T1_2024_2004['NIVEL_ED'].value_counts()
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
HOG_IND_T1_2024_2004['NIVEL_ED'] = HOG_IND_T1_2024_2004['NIVEL_ED'].replace(mapa_instruccion)

# Mismo diccionario para ambas bases: Cobertura Médica
frecuencia_cob = HOG_IND_T1_2024_2004['CH08'].value_counts()
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
HOG_IND_T1_2024_2004['CH08'] = HOG_IND_T1_2024_2004['CH08'].replace(mapa_cobertura_salud)

# Mismo diccionario para ambas bases: Condición de Actividad
frecuencia_EST = HOG_IND_T1_2024_2004['ESTADO'].value_counts()
print(frecuencia_EST) 
mapa_actividad = {
    "Entrevista individual no realizada (no respuesta al cuestion": 0,
    "Ocupado": 1,
    "Desocupado": 2,
    "Inactivo": 3,
    "Menor de 10 años": 4
}
HOG_IND_T1_2024_2004['ESTADO'] = HOG_IND_T1_2024_2004['ESTADO'].replace(mapa_actividad)

# Mismo diccionario para ambas bases: Categoría de Inactividad
frecuencia_CAT = HOG_IND_T1_2024_2004['CAT_INAC'].value_counts()
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
HOG_IND_T1_2024_2004['CAT_INAC'] = HOG_IND_T1_2024_2004['CAT_INAC'].replace(mapa_condicion)

# Mismo diccionario para ambas bases: V5
frecuencia_V5 = HOGAR_T1_2024_2004['V4'].value_counts()
print(frecuencia_V5) 
mapa_condicion = {
    "Sí": 1,
    "No": 2,
}
HOGAR_T1_2024_2004['V5'] = HOGAR_T1_2024_2004['V5'].replace(mapa_condicion)

# Mismo diccionario para ambas bases: V6
frecuencia_V6 = HOGAR_T1_2024_2004['V6'].value_counts()
print(frecuencia_V6) 
mapa_condicion = {
    "Sí": 1,
    "No": 2,
}
HOGAR_T1_2024_2004['V6'] = HOGAR_T1_2024_2004['V6'].replace(mapa_condicion)

# Mismo diccionario para ambas bases: V13
frecuencia_V13 = HOGAR_T1_2024_2004['V13'].value_counts()
print(frecuencia_V13) 
mapa_condicion = {
    "Sí": 1,
    "No": 2,
}
HOGAR_T1_2024_2004['V13'] = HOGAR_T1_2024_2004['V13'].replace(mapa_condicion)

# Mismo diccionario para ambas bases: V14
frecuencia_V14 = HOGAR_T1_2024_2004['V14'].value_counts()
print(frecuencia_V14) 
mapa_condicion = {
    "Sí": 1,
    "No": 2,
}
HOGAR_T1_2024_2004['V14'] = HOGAR_T1_2024_2004['V14'].replace(mapa_condicion)

# Mismo diccionario para ambas bases: V17
frecuencia_V17 = HOGAR_T1_2024_2004['V17'].value_counts()
print(frecuencia_V17) 
mapa_condicion = {
    "Sí": 1,
    "No": 2,
}
HOGAR_T1_2024_2004['V17'] = HOGAR_T1_2024_2004['V17'].replace(mapa_condicion)

# Mismo diccionario para ambas bases: V15
frecuencia_V15 = HOGAR_T1_2024_2004['V15'].value_counts()
print(frecuencia_V15) 
mapa_condicion = {
    "Sí": 1,
    "No": 2,
}
HOGAR_T1_2024_2004['V15'] = HOGAR_T1_2024_2004['V15'].replace(mapa_condicion)




# Cambio el formato de las siguientes columnas para que me aparezcan números enteros
HOG_IND_T1_2024_2004['ANO4_x'] = HOG_IND_T1_2024_2004['ANO4_x'].astype(int)
HOG_IND_T1_2024_2004['CH12'] = HOG_IND_T1_2024_2004['CH12'].astype(int)
HOG_IND_T1_2024_2004['CAT_INAC'] = HOG_IND_T1_2024_2004['CAT_INAC'].astype(int)




#Inciso 3: Limpieza Base de Datos

pd.set_option('display.max_rows', None)  # Show all rows
pd.set_option('display.max_columns', None)  # Show all columns

missing_data = HOG_IND_T1_2024_2004.isnull().sum()
print(missing_data)

# Eliminamos aquellas observaciones con missings o que no tienen sentido:   
    
# Monto de ingreso total individual - P47T & ITF:

HOG_IND_T1_2024_2004 = HOG_IND_T1_2024_2004[HOG_IND_T1_2024_2004['P47T'] >= 0] #Elimino ingresos negativos y nan
HOG_IND_T1_2024_2004 = HOG_IND_T1_2024_2004[HOG_IND_T1_2024_2004['ITF_x'] >= 0] #Elimino ingresos negativos y nan

#Edad Individuos - CH06:

HOG_IND_T1_2024_2004 = HOG_IND_T1_2024_2004[HOG_IND_T1_2024_2004['CH06'] >= 0] #Elimino edades negativas y nan



#Inciso 4



#1. Proporción de personas ocupadas en el hogar
# Crear una variable para identificar si una persona está ocupada (1: ocupado, 0: no ocupado)
HOG_IND_T1_2024_2004['OCUPADO'] = HOG_IND_T1_2024_2004['ESTADO'].apply(lambda x: 1 if x in [1] else 0)

#Vemos la cantidad de ocupados por año.
frecuencia_ocupado = HOG_IND_T1_2024_2004.groupby(['ANO4_x', 'OCUPADO']).size().unstack(fill_value=0)
print(frecuencia_ocupado) 

'''
OCUPADO     0    1
ANO4_x             
2004     1695  1056
2024     1125   959
'''

# Calcular la proporción de personas ocupadas en el hogar
HOG_IND_T1_2024_2004['TOTAL_HOGAR'] = HOG_IND_T1_2024_2004.groupby(['CODUSU', 'NRO_HOGAR'])['COMPONENTE'].transform('count')
HOG_IND_T1_2024_2004['TOTAL_OCUPADOS'] = HOG_IND_T1_2024_2004.groupby(['CODUSU', 'NRO_HOGAR'])['OCUPADO'].transform('sum')
HOG_IND_T1_2024_2004['PROPORCION_OCUPADOS'] = HOG_IND_T1_2024_2004['TOTAL_OCUPADOS'] / HOG_IND_T1_2024_2004['TOTAL_HOGAR']


#2. Proporción de personas en edad laboral en el hogar

# Creamos una variable para identificar si una persona está en edad laboral (15-65 años, por ejemplo)
HOG_IND_T1_2024_2004['PET'] = HOG_IND_T1_2024_2004['CH06'].apply(lambda x: 1 if 15 <= x <= 65 else 0)

# Calculamos la proporción de personas en edad laboral en el hogar
HOG_IND_T1_2024_2004['PROPORCION_EDAD_LABORAL'] = (
    HOG_IND_T1_2024_2004.groupby(['CODUSU', 'NRO_HOGAR'])['PET']
    .transform('sum') / HOG_IND_T1_2024_2004['TOTAL_HOGAR']
)


#3. Proporción de niños en el hogar. 

# Creamos una variable para identificar si una persona es un niño (<15 años)
HOG_IND_T1_2024_2004['ES_NIÑO'] = (HOG_IND_T1_2024_2004['CH06'] < 15).astype(int)

# Calculamos la proporción de niños en el hogar
HOG_IND_T1_2024_2004['PROPORCION_NIÑOS'] = (
    HOG_IND_T1_2024_2004.groupby(['CODUSU', 'NRO_HOGAR'])['ES_NIÑO']
    .transform('sum') / HOG_IND_T1_2024_2004['TOTAL_HOGAR']
)


#4. Proporción de personas con secundaria completa o mas. 

# Creamos una variable para identificar si una persona tiene secundaria completa o más
HOG_IND_T1_2024_2004['EDUCACION_SECUNDARIA_O_MAS'] = (
    HOG_IND_T1_2024_2004['CH12'].isin([4, 5, 6]).astype(int)
)

# Calculamos la proporción de personas con secundaria completa o más en el hogar
HOG_IND_T1_2024_2004['PROPORCION_EDUCACION_SECUNDARIA_O_MAS'] = (
    HOG_IND_T1_2024_2004.groupby(['CODUSU', 'NRO_HOGAR'])['EDUCACION_SECUNDARIA_O_MAS']
    .transform('sum') / HOG_IND_T1_2024_2004['TOTAL_HOGAR']
)




#Inciso 5

# Contar la cantidad de hogares para cada valor de la variable en cada año
counts = HOGAR_T1_2024_2004.groupby(['ANO4', 'V5'])['CODUSU'].count().unstack(fill_value=0)

# Crear el gráfico de barras apiladas para 2004 y 2024
counts.plot(kind='bar', stacked=True, figsize=(10, 6), color=['blue', 'green'], alpha=0.7)

# Añadir etiquetas y título
plt.xlabel('Año', fontsize=12)
plt.ylabel('Cantidad de Hogares', fontsize=12)
plt.title('Cantidad de Hogares que Reciben Subsidio o Ayuda Social.', fontsize=14)
plt.legend(title='', labels=['Reciben', 'No Reciben'])

# Mostrar el gráfico
plt.tight_layout()
plt.show()


# Contar la cantidad de hogares para cada valor de la variable en cada año
counts = HOGAR_T1_2024_2004.groupby(['ANO4', 'V6'])['CODUSU'].count().unstack(fill_value=0)

# Crear el gráfico de barras apiladas para 2004 y 2024
counts.plot(kind='bar', stacked=True, figsize=(10, 6), color=['purple', 'pink'], alpha=0.7)

# Añadir etiquetas y título
plt.xlabel('Año', fontsize=12)
plt.ylabel('Cantidad de Hogares', fontsize=12)
plt.title('Cantidad de Hogares que vive con mercaderías, ropa, alimentos del gobierno, iglesias, escuelas.', fontsize=14)
plt.legend(title='', labels=['Reciben', 'No Reciben'])

# Mostrar el gráfico
plt.tight_layout()
plt.show()


# Contar la cantidad de hogares para cada valor de la variable en cada año
counts = HOGAR_T1_2024_2004.groupby(['ANO4', 'V13'])['CODUSU'].count().unstack(fill_value=0)

# Crear el gráfico de barras apiladas para 2004 y 2024
counts.plot(kind='bar', stacked=True, figsize=(10, 6), color=['red', 'orange'], alpha=0.7)

# Añadir etiquetas y título
plt.xlabel('Año', fontsize=12)
plt.ylabel('Cantidad de Hogares', fontsize=12)
plt.title('Cantidad de Hogares que vive de gastar lo que tenían ahorrado.', fontsize=14)
plt.legend(title='', labels=['Gastan', 'No Gastan'])

# Mostrar el gráfico
plt.tight_layout()
plt.show()


# Contar la cantidad de hogares para cada valor de la variable en cada año
counts = HOGAR_T1_2024_2004.groupby(['ANO4', 'V14'])['CODUSU'].count().unstack(fill_value=0)

# Crear el gráfico de barras apiladas para 2004 y 2024
counts.plot(kind='bar', stacked=True, figsize=(10, 6), color=['blue', 'lightblue'], alpha=0.7)

# Añadir etiquetas y título
plt.xlabel('Año', fontsize=12)
plt.ylabel('Cantidad de Hogares', fontsize=12)
plt.title('Cantidad de Hogares que vive de pedir préstamos a familiares / amigos.', fontsize=14)
plt.legend(title='', labels=['Piden', 'No Piden'])

# Mostrar el gráfico
plt.tight_layout()
plt.show()


# Contar la cantidad de hogares para cada valor de la variable en cada año
counts = HOGAR_T1_2024_2004.groupby(['ANO4', 'V17'])['CODUSU'].count().unstack(fill_value=0)

# Crear el gráfico de barras apiladas para 2004 y 2024
counts.plot(kind='bar', stacked=True, figsize=(10, 6), color=['yellow', 'gray'], alpha=0.7)

# Añadir etiquetas y título
plt.xlabel('Año', fontsize=12)
plt.ylabel('Cantidad de Hogares', fontsize=12)
plt.title('Cantidad de Hogares que vive de vender alguna de sus pertenencias.', fontsize=14)
plt.legend(title='', labels=['Vende', 'No Vende'])

# Mostrar el gráfico
plt.tight_layout()
plt.show()



# Contar la cantidad de hogares para cada valor de la variable en cada año
counts = HOGAR_T1_2024_2004.groupby(['ANO4', 'V15'])['CODUSU'].count().unstack(fill_value=0)

# Crear el gráfico de barras apiladas para 2004 y 2024
counts.plot(kind='bar', stacked=True, figsize=(10, 6), color=['brown', 'black'], alpha=0.7)

# Añadir etiquetas y título
plt.xlabel('Año', fontsize=12)
plt.ylabel('Cantidad de Hogares', fontsize=12)
plt.title('Cantidad de Hogares que vive de pedir préstamos a bancos, financieras.', fontsize=14)
plt.legend(title='', labels=['Reciben', 'No Reciben'])

# Mostrar el gráfico
plt.tight_layout()
plt.show()




#Inciso 6

# Creamos una variable para identificar hogares con desocupación

HOG_IND_2024 = HOG_IND_T1_2024_2004[HOG_IND_T1_2024_2004['ANO4_x'] == 2024]

HOG_IND_2024['HOGAR_CON_DESOCUPACION'] = HOG_IND_2024.groupby('CODUSU')['ESTADO'].transform(
    lambda x: 1 if (x == 2).any() else 0
)

# Seleccionamos una sola observación por hogar (por ejemplo, el primer registro del hogar)
hogares = HOG_IND_2024.drop_duplicates(subset='CODUSU')

# Calculamos el total de hogares con desocupación
total_hogares = hogares['PONDERA_x'].sum()  # Total de hogares ponderados
hogares_desocupados = hogares.loc[hogares['HOGAR_CON_DESOCUPACION'] == 1, 'PONDERA_x'].sum()  # Hogares desocupados ponderados

# Calculamos la tasa
tasa_hogares_desocupados = (hogares_desocupados / total_hogares) * 100
print(f"Tasa de hogares con desocupación: {tasa_hogares_desocupados:.2f}%")

'''
Tasa de hogares con desocupación: 9.99%%
'''




'''
--------------------------------
2. Parte II: Clasificación
--------------------------------
'''


#Creamos la base Respondieron

conteo_estado_anual = HOG_IND_T1_2024_2004.groupby(['ANO4_x', 'ESTADO']).agg({"ESTADO": "count"})
print(conteo_estado_anual) 

respondieron = HOG_IND_T1_2024_2004[HOG_IND_T1_2024_2004['ESTADO'] != 0]
norespondieron = HOG_IND_T1_2024_2004[HOG_IND_T1_2024_2004['ESTADO'] == 0]

#Agregamos Variable desocupado

respondieron['DESOCUPADO'] = respondieron['ESTADO'].apply(lambda x: 1 if x in [2] else 0)

# Lista de columnas a eliminar(se repiten, o tienen todas missings)
columns_to_drop = [
    'ITF_y', 'DECIFR_y', 'IDECIFR_y', 'RDECIFR_y', 'GDECIFR_y', 'PDECIFR_y', 'ADECIFR_y', 
    'IPCF_y', 'DECCFR_y', 'IDECCFR_y', 'RDECCFR_y', 'GDECCFR_y', 'PDECCFR_y', 'ADECCFR_y', 
    'PONDIH_y', 'HOGAR_CON_DESOCUPACION', 'ANO4_y', 'TRIMESTRE_y', 'REALIZADA', 'REGION_y', 
    'MAS_500_y', 'AGLOMERADO_y', 'PONDERA_y', 'PJ1_1 ', 'PJ2_1', 'PJ3_1',   
]

# Eliminar las columnas del DataFrame
respondieron = respondieron.drop(columns=columns_to_drop, errors='ignore')
respondieron = respondieron.drop(columns=['PJ1_1'], errors='ignore')
respondieron = respondieron.drop(columns=['IMPUTA'], errors='ignore')
respondieron = respondieron.drop(columns=['PONDIIO'], errors='ignore')
respondieron = respondieron.drop(columns=['PONDII'], errors='ignore')
respondieron = respondieron.drop(columns=['PONDIH_x'], errors='ignore')

print(respondieron.info(verbose = True))

######


#Inciso 1

# Filtramos la base para cada año
respondieron_2004 = respondieron[respondieron['ANO4_x'] == 2004]
respondieron_2004.loc[:, 'TRIMESTRE_x'] = 1
respondieron_2024 = respondieron[respondieron['ANO4_x'] == 2024]


# Establecemos las variables dependientes e independientes
columns_to_select = (
    list(respondieron_2004.loc[:, 'CH03':'NIVEL_ED'].columns) + 
    ['ITF_x'] + 
    list(respondieron_2004.loc[:, 'V1':'V18'].columns) + 
    ['PROPORCION_OCUPADOS'] + 
    ['PROPORCION_EDAD_LABORAL'] + 
    ['PROPORCION_NIÑOS'] + 
    ['PROPORCION_EDUCACION_SECUNDARIA_O_MAS']
)

## Para 2004:
y_2004 = respondieron_2004.DESOCUPADO
x_2004 = respondieron_2004[columns_to_select].drop(columns=['CH15_COD', 'CH16_COD', 'CH05'], errors='ignore')

## Para 2024:
y_2024 = respondieron_2024.DESOCUPADO
x_2024 = respondieron_2024[columns_to_select].drop(columns=['CH15_COD', 'CH16_COD', 'CH05'], errors='ignore')

# Identificamos las variables categóricas y creamos dummies en base a sus valores
x_2004 = pd.get_dummies(x_2004, drop_first=True)
x_2024 = pd.get_dummies(x_2024, drop_first=True)

# Reseteamos los índices
x_2004 = x_2004.reset_index(drop=True)
x_2024 = x_2024.reset_index(drop=True)

# Agregamos columna de 1s a la matriz de independientes (x)
ones_2004 = pd.DataFrame(np.ones(x_2004.shape[0], dtype=int), columns=['Intercept'])
x_2004 = pd.concat([ones_2004, x_2004], axis=1)

ones_2024 = pd.DataFrame(np.ones(x_2024.shape[0], dtype=int), columns=['Intercept'])
x_2024 = pd.concat([ones_2024, x_2024], axis=1)

# Verificamos la información de los df de x
x_2004.info()
x_2024.info()

# Partimos cada base en dos y transformamos el vector x: 
x_2004_train, x_2004_test, y_2004_train, y_2004_test = train_test_split(x_2004, y_2004, test_size = 0.3, random_state = 101)
x_2024_train, x_2024_test, y_2024_train, y_2024_test = train_test_split(x_2024, y_2024, test_size = 0.3, random_state = 101)

# Revisamos cuantas observaciones quedaron para Test y cuantas para Entrenamiento.
print(f'Para el año 2004 tenemos un conjunto de entrenamiento de {len(x_2004_train)} observaciones y uno de test de {len(x_2004_test)} observaciones.')
print(f'Para el año 2024 tenemos un conjunto de entrenamiento de {len(x_2024_train)} observaciones y uno de test de {len(x_2024_test)} observaciones.')


#Inciso 2


#Inciso 3

# Estadisticas antes de estandarizar
x_2004_train.describe().T
x_2024_train.describe().T

# StandardScaler for 2004 dataset
sc_2004 = StandardScaler()
x_2004_train_transformed = pd.DataFrame(
    sc_2004.fit_transform(x_2004_train),
    index=x_2004_train.index,
    columns=x_2004_train.columns
)
x_2004_test_transformed = pd.DataFrame(
    sc_2004.transform(x_2004_test),
    index=x_2004_test.index,
    columns=x_2004_test.columns
)

# StandardScaler for 2024 dataset
sc_2024 = StandardScaler()
x_2024_train_transformed = pd.DataFrame(
    sc_2024.fit_transform(x_2024_train),
    index=x_2024_train.index,
    columns=x_2024_train.columns
)
x_2024_test_transformed = pd.DataFrame(
    sc_2024.transform(x_2024_test),
    index=x_2024_test.index,
    columns=x_2024_test.columns
)


# Estadisticas luego de estandarizar
x_2024_test_transformed.describe().T


#Inciso 4

#LASSO
# === Año 2004 === #

## Regresión Logística
log_reg_2004 = LogisticRegression(penalty='l1', solver='liblinear').fit(x_2004_train_transformed, y_2004_train)
y_pred_log_2004 = log_reg_2004.predict(x_2004_test_transformed)
y_pred_prob_log_2004 = log_reg_2004.predict_proba(x_2004_test_transformed)[:, 1]

# Métricas para Regresión Logística (2004)
fpr_log_2004, tpr_log_2004, _ = roc_curve(y_2004_test, y_pred_prob_log_2004)
roc_auc_log_2004 = auc(fpr_log_2004, tpr_log_2004)

print("Regresión Logística - Año 2004")
print(f"Accuracy: {accuracy_score(y_2004_test, y_pred_log_2004):.4f}")
print(f"AUC: {roc_auc_log_2004:.4f}")
print(f"Matriz de Confusión:\n{confusion_matrix(y_2004_test, y_pred_log_2004)}")

'''
Regresión Logística - Año 2004 - Penalidad Lasso
Accuracy: 0.9345
AUC: 0.8012
Matriz de Confusión:
[[765   7]
 [ 47   6]]
'''

## Gráfico de Curvas ROC
plt.figure(figsize=(10, 6))
plt.plot(fpr_log_2004, tpr_log_2004, label=f"Reg. Logística (AUC = {roc_auc_log_2004:.4f})")
plt.plot([0, 1], [0, 1], 'k--', label="Random Classifier")
plt.title("Curvas ROC - Año 2004 - Regularización Lasso")
plt.xlabel("Tasa de Falsos Positivos (FPR)")
plt.ylabel("Tasa de Verdaderos Positivos (TPR)")
plt.legend(loc="lower right")
plt.show()  

# === Año 2024 === #

## Regresión Logística
log_reg_2024 = LogisticRegression(penalty='l1', solver='liblinear').fit(x_2024_train_transformed, y_2024_train)
y_pred_log_2024 = log_reg_2024.predict(x_2024_test_transformed)
y_pred_prob_log_2024 = log_reg_2024.predict_proba(x_2024_test_transformed)[:, 1]

# Métricas para Regresión Logística (2004)
fpr_log_2024, tpr_log_2024, _ = roc_curve(y_2024_test, y_pred_prob_log_2024)
roc_auc_log_2024 = auc(fpr_log_2024, tpr_log_2024)

print("Regresión Logística - Año 2024")
print(f"Accuracy: {accuracy_score(y_2024_test, y_pred_log_2024):.4f}")
print(f"AUC: {roc_auc_log_2024:.4f}")
print(f"Matriz de Confusión:\n{confusion_matrix(y_2024_test, y_pred_log_2024)}")

'''
Regresión Logística - Año 2024
Accuracy: 0.9585
AUC: 0.8566
Matriz de Confusión:
[[598   7]
 [ 19   2]]
'''

## Gráfico de Curvas ROC
plt.figure(figsize=(10, 6))
plt.plot(fpr_log_2024, tpr_log_2024, label=f"Reg. Logística (AUC = {roc_auc_log_2024:.4f})")
plt.plot([0, 1], [0, 1], 'k--', label="Random Classifier")
plt.title("Curvas ROC - Año 2024 - Regularización Lasso")
plt.xlabel("Tasa de Falsos Positivos (FPR)")
plt.ylabel("Tasa de Verdaderos Positivos (TPR)")
plt.legend(loc="lower right")
plt.show()  



#RIDGE
# === Año 2004 === #

## Regresión Logística
log_reg_2004 = LogisticRegression(penalty='l2', solver='liblinear').fit(x_2004_train_transformed, y_2004_train)
y_pred_log_2004 = log_reg_2004.predict(x_2004_test_transformed)
y_pred_prob_log_2004 = log_reg_2004.predict_proba(x_2004_test_transformed)[:, 1]

# Métricas para Regresión Logística (2004)
fpr_log_2004, tpr_log_2004, _ = roc_curve(y_2004_test, y_pred_prob_log_2004)
roc_auc_log_2004 = auc(fpr_log_2004, tpr_log_2004)

print("Regresión Logística - Año 2004")
print(f"Accuracy: {accuracy_score(y_2004_test, y_pred_log_2004):.4f}")
print(f"AUC: {roc_auc_log_2004:.4f}")
print(f"Matriz de Confusión:\n{confusion_matrix(y_2004_test, y_pred_log_2004)}")

'''
Regresión Logística - Año 2004 - Regularización Ridge
Accuracy: 0.9333
AUC: 0.7950
Matriz de Confusión:
[[764   8]
 [ 47   6]]
'''

## Gráfico de Curvas ROC
plt.figure(figsize=(10, 6))
plt.plot(fpr_log_2004, tpr_log_2004, label=f"Reg. Logística (AUC = {roc_auc_log_2004:.4f})")
plt.plot([0, 1], [0, 1], 'k--', label="Random Classifier")
plt.title("Curvas ROC - Año 2004 - Regularización Ridge")
plt.xlabel("Tasa de Falsos Positivos (FPR)")
plt.ylabel("Tasa de Verdaderos Positivos (TPR)")
plt.legend(loc="lower right")
plt.show()  

# === Año 2024 === #

## Regresión Logística
log_reg_2024 = LogisticRegression(penalty='l2', solver='liblinear').fit(x_2024_train_transformed, y_2024_train)
y_pred_log_2024 = log_reg_2024.predict(x_2024_test_transformed)
y_pred_prob_log_2024 = log_reg_2024.predict_proba(x_2024_test_transformed)[:, 1]

# Métricas para Regresión Logística (2004)
fpr_log_2024, tpr_log_2024, _ = roc_curve(y_2024_test, y_pred_prob_log_2024)
roc_auc_log_2024 = auc(fpr_log_2024, tpr_log_2024)

print("Regresión Logística - Año 2024")
print(f"Accuracy: {accuracy_score(y_2024_test, y_pred_log_2024):.4f}")
print(f"AUC: {roc_auc_log_2024:.4f}")
print(f"Matriz de Confusión:\n{confusion_matrix(y_2024_test, y_pred_log_2024)}")

'''
Regresión Logística - Año 2024 - Regularización Ridge
Accuracy: 0.9601
AUC: 0.8502
Matriz de Confusión:
[[599   6]
 [ 19   2]]
'''

## Gráfico de Curvas ROC
plt.figure(figsize=(10, 6))
plt.plot(fpr_log_2024, tpr_log_2024, label=f"Reg. Logística (AUC = {roc_auc_log_2024:.4f})")
plt.plot([0, 1], [0, 1], 'k--', label="Random Classifier")
plt.title("Curvas ROC - Año 2024 - Regularización Ridge")
plt.xlabel("Tasa de Falsos Positivos (FPR)")
plt.ylabel("Tasa de Verdaderos Positivos (TPR)")
plt.legend(loc="lower right")
plt.show()  





#Inciso 5


# Generamos los valores de alpha como potencias de 10 entre -5 y 5
alphas = 10 ** np.linspace(-5, 5, 50)
np.set_printoptions(suppress = True)
alphas


# === Año 2004 === #

#RIDGE
ridgecv = RidgeCV(alphas=alphas, cv=10).fit(x_2004_train_transformed, y_2004_train)
print("El mejor alpha:", ridgecv.alpha_)

'''
El mejor alpha: 355.64803062231283
'''
# Ahora con el alpha óptimo, volvemos a estimar nuestro modelo
ridge = Ridge(alpha=ridgecv.alpha_)
ridge = ridge.fit(x_2004_train_transformed, y_2004_train)
ridge_pred = ridge.predict(x_2004_test_transformed)
ecm_ridge = mean_squared_error(y_2004_test, ridge_pred)

print("Error cuadrático medio: ", ecm_ridge)   

'''
Error cuadrático medio:  0.056185197535755474
'''

print("Coeficientes del mejor modelo:")
print(pd.Series(ridgecv.coef_, index = x_2004_train_transformed.columns)) 


#LASSO
lassocv = LassoCV(alphas=alphas, cv=10, max_iter=100000, random_state=100)
lassocv.fit(x_2004_train_transformed, y_2004_train)
print("Alpha óptimo:", lassocv.alpha_)

'''
Alpha óptimo: 0.002811768697974231
'''

lasso = Lasso(alpha=lassocv.alpha_)
lasso.fit(x_2004_train_transformed, y_2004_train)
lasso_pred = lasso.predict(x_2004_test_transformed)

print("Error cuadrático medio: ", mean_squared_error(y_2004_test, lasso_pred))

'''
Error cuadrático medio:  0.05545939186646115
'''

print("Coeficientes del mejor modelo:")
pd.Series(lasso.coef_, index=x_2004_train_transformed.columns)





# === Año 2024 === #

#RIDGE
ridgecv = RidgeCV(alphas=alphas, cv=10).fit(x_2024_train_transformed, y_2024_train)
print("El mejor alpha:", ridgecv.alpha_)

'''
El mejor alpha: 568.9866029018305
'''

# Ahora con el alpha óptimo, volvemos a estimar nuestro modelo
ridge = Ridge(alpha=ridgecv.alpha_)
ridge = ridge.fit(x_2004_train_transformed, y_2004_train)
ridge_pred = ridge.predict(x_2004_test_transformed)
ecm_ridge = mean_squared_error(y_2024_test, ridge_pred)

print("Error cuadrático medio: ", ecm_ridge)   

'''
Error cuadrático medio:  0.05621142830452838
'''

print("Coeficientes del mejor modelo:")
print(pd.Series(ridgecv.coef_, index = x_2024_train_transformed.columns)) 



#LASSO
lassocv = LassoCV(alphas=alphas, cv=10, max_iter=100000, random_state=100)
lassocv.fit(x_2024_train_transformed, y_2024_train)
print("Alpha óptimo:", lassocv.alpha_)

'''
Alpha óptimo: 0.004498432668969444
'''

lasso = Lasso(alpha=lassocv.alpha_)
lasso.fit(x_2024_train_transformed, y_2024_train)
lasso_pred = lasso.predict(x_2024_test_transformed)

print("Error cuadrático medio: ", mean_squared_error(y_2024_test, lasso_pred))

'''
Error cuadrático medio:  0.03023828910250078
'''

print("Coeficientes del mejor modelo:")
pd.Series(lasso.coef_, index=x_2024_train_transformed.columns)



# === Configuración para validación cruzada para 2004 ===
kf = KFold(n_splits=10, shuffle=True, random_state=100)

# === Inicializar estructuras para almacenar errores y proporción de variables ignoradas ===
ridge_errors_dict = {}
lasso_errors_dict = {}
lasso_proportion_ignored = []

# === Ridge: Calcular errores para todos los alphas ===
for alpha in alphas:
    ridge = Ridge(alpha=alpha)
    errors = []
    for train_index, test_index in kf.split(x_2004_train_transformed):
        X_train_fold = x_2004_train_transformed.iloc[train_index]
        y_train_fold = y_2004_train.iloc[train_index]
        X_test_fold = x_2004_train_transformed.iloc[test_index]
        y_test_fold = y_2004_train.iloc[test_index]

        ridge.fit(X_train_fold, y_train_fold)
        pred = ridge.predict(X_test_fold)
        error = mean_squared_error(y_test_fold, pred)
        errors.append(error)

    ridge_errors_dict[alpha] = errors

# === Lasso: Calcular errores y proporción de variables ignoradas para todos los alphas ===
for alpha in alphas:
    lasso = Lasso(alpha=alpha, max_iter=100000)
    errors = []
    proportions_zero = []
    for train_index, test_index in kf.split(x_2004_train_transformed):
        X_train_fold = x_2004_train_transformed.iloc[train_index]
        y_train_fold = y_2004_train.iloc[train_index]
        X_test_fold = x_2004_train_transformed.iloc[test_index]
        y_test_fold = y_2004_train.iloc[test_index]

        lasso.fit(X_train_fold, y_train_fold)
        pred = lasso.predict(X_test_fold)
        error = mean_squared_error(y_test_fold, pred)
        errors.append(error)

        # Calcular la proporción de coeficientes cero
        proportion_zero = np.mean(lasso.coef_ == 0)
        proportions_zero.append(proportion_zero)

    lasso_errors_dict[alpha] = errors
    # Promedio de la proporción de variables ignoradas para este alpha
    lasso_proportion_ignored.append(np.mean(proportions_zero))

# === Preparar DataFrames para los errores de Ridge ===
ridge_errors_df = pd.DataFrame(ridge_errors_dict)
ridge_errors_long = ridge_errors_df.melt(var_name='Alpha', value_name='Error_Medio_Validación')
ridge_errors_long['Modelo'] = 'Ridge'

# === Preparar DataFrames para los errores de Lasso ===
lasso_errors_df = pd.DataFrame(lasso_errors_dict)
lasso_errors_long = lasso_errors_df.melt(var_name='Alpha', value_name='Error_Medio_Validación')
lasso_errors_long['Modelo'] = 'Lasso'

# === Combinar los resultados de Ridge y Lasso ===
errors_combined = pd.concat([ridge_errors_long, lasso_errors_long], ignore_index=True)

# Convertir Alpha a cadena para facilitar la visualización en el gráfico
errors_combined['Alpha'] = errors_combined['Alpha'].astype(str)

# === Generar el boxplot ===
errors_combined['Alpha'] = errors_combined['Alpha'].astype(float)  # Convertir a flotante para formateo
unique_alphas = sorted(errors_combined['Alpha'].unique())  # Obtener valores únicos y ordenarlos
alpha_labels = [f"{alpha:.4f}" for alpha in unique_alphas]  # Formatear con 2 decimales

# Generar el boxplot
plt.figure(figsize=(16, 8))
sns.boxplot(x='Alpha', y='Error_Medio_Validación', hue='Modelo', data=errors_combined)
plt.xlabel('Alpha (λ)', fontsize=12)
plt.ylabel('Error Medio de Validación', fontsize=12)
plt.title('Distribución del Error de Validación para Cada Alpha en Ridge y Lasso (Año 2004)', fontsize=14)
plt.xticks(ticks=range(len(unique_alphas)), labels=alpha_labels, rotation=90)  # Aplicar etiquetas redondeadas
plt.legend(title='Modelo')
plt.tight_layout()
plt.show()

# === Generar el line plot para la proporción de variables ignoradas en Lasso 2004 ===
plt.figure(figsize=(10, 6))
plt.plot(alphas, lasso_proportion_ignored, marker='o', linestyle='-', label='Proporción de Variables Ignoradas')
plt.xscale('log')
plt.xlabel('Alpha (λ)', fontsize=12)
plt.ylabel('Proporción de Variables Ignoradas', fontsize=12)
plt.title('Proporción de Variables Ignoradas por Lasso en Función de Alpha (Año 2004)', fontsize=14)
plt.grid(True, which='both', linestyle='--', linewidth=0.5)
plt.legend()
plt.tight_layout()
plt.show()



# === Configuración para validación cruzada para 2024 ===
kf = KFold(n_splits=10, shuffle=True, random_state=100)

# === Inicializar estructuras para almacenar errores y proporción de variables ignoradas ===
ridge_errors_dict_2024 = {}
lasso_errors_dict_2024 = {}
lasso_proportion_ignored_2024 = []

# === Ridge: Calcular errores para todos los alphas (2024) ===
for alpha in alphas:
    ridge = Ridge(alpha=alpha)
    errors = []
    for train_index, test_index in kf.split(x_2024_train_transformed):
        X_train_fold = x_2024_train_transformed.iloc[train_index]
        y_train_fold = y_2024_train.iloc[train_index]
        X_test_fold = x_2024_train_transformed.iloc[test_index]
        y_test_fold = y_2024_train.iloc[test_index]

        ridge.fit(X_train_fold, y_train_fold)
        pred = ridge.predict(X_test_fold)
        error = mean_squared_error(y_test_fold, pred)
        errors.append(error)

    ridge_errors_dict_2024[alpha] = errors

# === Lasso: Calcular errores y proporción de variables ignoradas para todos los alphas (2024) ===
for alpha in alphas:
    lasso = Lasso(alpha=alpha, max_iter=100000)
    errors = []
    proportions_zero = []
    for train_index, test_index in kf.split(x_2024_train_transformed):
        X_train_fold = x_2024_train_transformed.iloc[train_index]
        y_train_fold = y_2024_train.iloc[train_index]
        X_test_fold = x_2024_train_transformed.iloc[test_index]
        y_test_fold = y_2024_train.iloc[test_index]

        lasso.fit(X_train_fold, y_train_fold)
        pred = lasso.predict(X_test_fold)
        error = mean_squared_error(y_test_fold, pred)
        errors.append(error)

        # Calcular la proporción de coeficientes cero
        proportion_zero = np.mean(lasso.coef_ == 0)
        proportions_zero.append(proportion_zero)

    lasso_errors_dict_2024[alpha] = errors
    # Promedio de la proporción de variables ignoradas para este alpha
    lasso_proportion_ignored_2024.append(np.mean(proportions_zero))

# === Preparar DataFrames para los errores de Ridge ===
ridge_errors_df_2024 = pd.DataFrame(ridge_errors_dict_2024)
ridge_errors_long_2024 = ridge_errors_df_2024.melt(var_name='Alpha', value_name='Error_Medio_Validación')
ridge_errors_long_2024['Modelo'] = 'Ridge'

# === Preparar DataFrames para los errores de Lasso ===
lasso_errors_df_2024 = pd.DataFrame(lasso_errors_dict_2024)
lasso_errors_long_2024 = lasso_errors_df_2024.melt(var_name='Alpha', value_name='Error_Medio_Validación')
lasso_errors_long_2024['Modelo'] = 'Lasso'

# === Combinar los resultados de Ridge y Lasso ===
errors_combined_2024 = pd.concat([ridge_errors_long_2024, lasso_errors_long_2024], ignore_index=True)

# === Generar el boxplot ===
errors_combined_2024['Alpha'] = errors_combined_2024['Alpha'].astype(float)  # Convertir a flotante para formateo
unique_alphas_2024 = sorted(errors_combined_2024['Alpha'].unique())  # Obtener valores únicos y ordenarlos
alpha_labels_2024 = [f"{alpha:.4f}" for alpha in unique_alphas_2024]  # Formatear con 2 decimales

# Generar el boxplot
plt.figure(figsize=(16, 8))
sns.boxplot(x='Alpha', y='Error_Medio_Validación', hue='Modelo', data=errors_combined_2024)
plt.xlabel('Alpha (λ)', fontsize=12)
plt.ylabel('Error Medio de Validación', fontsize=12)
plt.title('Distribución del Error de Validación para Cada Alpha en Ridge y Lasso (Año 2024)', fontsize=14)
plt.xticks(ticks=range(len(unique_alphas_2024)), labels=alpha_labels_2024, rotation=90)  # Aplicar etiquetas redondeadas
plt.legend(title='Modelo')
plt.tight_layout()
plt.show()


# === Generar el line plot para la proporción de variables ignoradas en Lasso 2024 ===
plt.figure(figsize=(10, 6))
plt.plot(alphas, lasso_proportion_ignored_2024, marker='o', linestyle='-', label='Proporción de Variables Ignoradas')
plt.xscale('log')
plt.xlabel('Alpha (λ)', fontsize=12)
plt.ylabel('Proporción de Variables Ignoradas', fontsize=12)
plt.title('Proporción de Variables Ignoradas por Lasso en Función de Alpha (Año 2024)', fontsize=14)
plt.grid(True, which='both', linestyle='--', linewidth=0.5)
plt.legend()
plt.tight_layout()
plt.show()





#Inciso 6


#LASSO
lassocv = LassoCV(alphas=alphas, cv=10, max_iter=100000, random_state=100)
lassocv.fit(x_2004_train_transformed, y_2004_train)
print("Alpha óptimo:", lassocv.alpha_)

'''
Alpha óptimo: 0.002811768697974231
'''

lasso = Lasso(alpha=lassocv.alpha_)
lasso.fit(x_2004_train_transformed, y_2004_train)
lasso_pred = lasso.predict(x_2004_test_transformed)

print("Error cuadrático medio: ", mean_squared_error(y_2004_test, lasso_pred))

'''
Error cuadrático medio:  0.05545939186646115
'''

print("Coeficientes del mejor modelo:")
pd.Series(lasso.coef_, index=x_2004_train_transformed.columns)

'''
Variables con coeficiente igual a 0:
['Intercept', 'CH04', 'ITF_x', 'PROPORCION_EDUCACION_SECUNDARIA_O_MAS', 'CH03_Hermano', 'CH03_Suegro', 
 'CH03_Yerno/Nuera', 'CH09_No', 'CH10_Nunca asistió', 'CH10_Sí, asiste', 'CH11_Privado', 'CH11_Público', 
 'CH13_No', 'CH13_Sí', 'CH14_00', 'CH14_03', 'CH14_04', 'CH14_99', 'CH15_En otra localidad', 
 'CH15_En otra provincia (especificar)', 'CH15_En otro país', 'CH16_No había nacido', 'V5_Sí', 'V6_Sí', 
 'V8_Sí', 'V9_Sí', 'V10_Sí', 'V12_Sí', 'V14_Sí', 'V15_Sí']
'''

#LASSO 2024
lassocv = LassoCV(alphas=alphas, cv=10, max_iter=100000, random_state=100)
lassocv.fit(x_2024_train_transformed, y_2024_train)
print("Alpha óptimo:", lassocv.alpha_)

'''
Alpha óptimo: 0.004498432668969444
'''

lasso = Lasso(alpha=lassocv.alpha_)
lasso.fit(x_2024_train_transformed, y_2024_train)
lasso_pred = lasso.predict(x_2024_test_transformed)

print("Error cuadrático medio: ", mean_squared_error(y_2024_test, lasso_pred))

'''
Error cuadrático medio:  0.03023828910250078
'''

print("Coeficientes del mejor modelo:")
pd.Series(lasso.coef_, index=x_2024_train_transformed.columns)

'''
Variables con coeficiente igual a 0:
['Intercept', 'CH04', 'CH07', 'NIVEL_ED', 'ITF_x', 'PROPORCION_NIÑOS', 'CH03_4', 'CH03_5', 'CH03_6', 
 'CH03_7', 'CH03_10', 'CH09_3', 'CH10_1', 'CH10_3', 'CH11_2', 'CH13_2', 'CH14_2.0', 'CH14_3.0', 
 'CH14_4.0', 'CH14_6.0', 'CH14_8.0', 'CH14_98.0', 'CH14_99.0', 'CH15_2', 'CH15_5', 'CH16_3', 
 'CH16_5', 'V1_2', 'V2_2', 'V21_2', 'V22_2', 'V7_2', 'V8_2', 'V9_2', 'V10_2', 'V12_2', 'V15_2']
'''


#Inciso 7


# === Año 2004 === #

#RIDGE
ridgecv = RidgeCV(alphas=alphas, cv=10).fit(x_2004_train_transformed, y_2004_train)
print("El mejor alpha:", ridgecv.alpha_)

'''
El mejor alpha: 355.64803062231283
'''
# Ahora con el alpha óptimo, volvemos a estimar nuestro modelo
ridge = Ridge(alpha=ridgecv.alpha_)
ridge = ridge.fit(x_2004_train_transformed, y_2004_train)
ridge_pred = ridge.predict(x_2004_test_transformed)
ecm_ridge = mean_squared_error(y_2004_test, ridge_pred)

print("Error cuadrático medio: ", ecm_ridge)   

'''
Error cuadrático medio:  0.056185197535755474
'''

print("Coeficientes del mejor modelo:")
print(pd.Series(ridgecv.coef_, index = x_2004_train_transformed.columns)) 


#LASSO
lassocv = LassoCV(alphas=alphas, cv=10, max_iter=100000, random_state=100)
lassocv.fit(x_2004_train_transformed, y_2004_train)
print("Alpha óptimo:", lassocv.alpha_)

'''
Alpha óptimo: 0.002811768697974231
'''

lasso = Lasso(alpha=lassocv.alpha_)
lasso.fit(x_2004_train_transformed, y_2004_train)
lasso_pred = lasso.predict(x_2004_test_transformed)

print("Error cuadrático medio: ", mean_squared_error(y_2004_test, lasso_pred))

'''
Error cuadrático medio:  0.05545939186646115
'''

print("Coeficientes del mejor modelo:")
pd.Series(lasso.coef_, index=x_2004_train_transformed.columns)





# === Año 2024 === #

#RIDGE
ridgecv = RidgeCV(alphas=alphas, cv=10).fit(x_2024_train_transformed, y_2024_train)
print("El mejor alpha:", ridgecv.alpha_)

'''
El mejor alpha: 568.9866029018305
'''

# Ahora con el alpha óptimo, volvemos a estimar nuestro modelo
ridge = Ridge(alpha=ridgecv.alpha_)
ridge = ridge.fit(x_2004_train_transformed, y_2004_train)
ridge_pred = ridge.predict(x_2004_test_transformed)
ecm_ridge = mean_squared_error(y_2024_test, ridge_pred)

print("Error cuadrático medio: ", ecm_ridge)   

'''
Error cuadrático medio:  0.05621142830452838
'''

print("Coeficientes del mejor modelo:")
print(pd.Series(ridgecv.coef_, index = x_2024_train_transformed.columns)) 



#LASSO
lassocv = LassoCV(alphas=alphas, cv=10, max_iter=100000, random_state=100)
lassocv.fit(x_2024_train_transformed, y_2024_train)
print("Alpha óptimo:", lassocv.alpha_)

'''
Alpha óptimo: 0.004498432668969444
'''

lasso = Lasso(alpha=lassocv.alpha_)
lasso.fit(x_2024_train_transformed, y_2024_train)
lasso_pred = lasso.predict(x_2024_test_transformed)

print("Error cuadrático medio: ", mean_squared_error(y_2024_test, lasso_pred))

'''
Error cuadrático medio:  0.03023828910250078
'''

print("Coeficientes del mejor modelo:")
pd.Series(lasso.coef_, index=x_2024_train_transformed.columns)



'''
Para 2004: LASSO funciona mejor
Para 2024: LASSO funciona mejor
'''


