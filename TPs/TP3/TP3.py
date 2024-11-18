"""
-------------------------------------------------------------------------------
-------------- Análisis Descriptivo y Predicción de Desocupación --------------

--      Machine Learning para Economistas - Universidad de San Andrés        --


-     @autores: Eitan Salischiker, Tomás Marotta y Juan Segundo Zapiola       -

-                      Fecha: 15 de Noviembre de 2024                         -
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
"""
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

# Métricas y evaluación de modelos
from sklearn.metrics import (
    confusion_matrix, 
    accuracy_score, 
    roc_curve, 
    auc
)

# Gráficos
import matplotlib.pyplot as plt

## Definimos el directorio de trabajo
os.chdir(r'/Users/juansegundozapiola/Documents/Maestria/Big Data/BigData/TPs/TP3')

'''
--------------------------------
 1. Parte I: Analizando la base
--------------------------------
'''

##### Inciso 2

### 2.a. Creamos la base de datos con la que vamos a trabajar

# Abrimos la base del primer trimestre para 2024 y 2004.
T1_2024 = pd.read_excel("usu_individual_T124.xlsx") 
T1_2004 = pd.read_stata("Individual_t104.dta")

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
    print("Columnas en T1_2024 pero no en T1_2004:", set(T1_2024.columns) - set(T1_2004.columns))
    print("Columnas en T1_2004 pero no en T1_2024:", set(T1_2004.columns) - set(T1_2024.columns))


# A partir del tercer trimestre del año 2010, las variables referidas al Plan 
# Jefes y Jefas de Hogar(Pj1_1, Pj2_1 y Pj3_1) dejaron de ser relevadas.

# Unimos ambos trimestres en una sola base: 
T1_2024_2004 = pd.concat([T1_2024, T1_2004], ignore_index=True)

##----Correcciones en agrupacion de bases:

# Mismo diccionario para ambas bases: Género
frecuencia_genero = T1_2024_2004['CH04'].value_counts()
print(frecuencia_genero) 
mapa_genero = {"Varón": 1, 
               "Mujer": 2}
T1_2024_2004['CH04'] = T1_2024_2004['CH04'].replace(mapa_genero)

# Convertir la columna 'CH06' a numérica, colocando NaN en valores no numéricos
T1_2024_2004['CH06'] = pd.to_numeric(T1_2024_2004['CH06'], errors='coerce')

# Mismo diccionario para ambas bases: Estado Civil
frecuencia_estado = T1_2024_2004['CH07'].value_counts()
print(frecuencia_estado) 
mapa_estado = { "Unido": 1, 
                "Casado": 2,
                "Separado o divorciado": 3, 
               "Viudo": 4, 
               "Soltero": 5}
T1_2024_2004['CH07'] = T1_2024_2004['CH07'].replace(mapa_estado)

# Mismo diccionario para ambas bases: Nivel Educativo
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

# Mismo diccionario para ambas bases: nivel_ed
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

# Mismo diccionario para ambas bases: Cobertura Médica
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

# Mismo diccionario para ambas bases: Condición de Actividad
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

# Mismo diccionario para ambas bases: Categoría de Inactividad
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

# Cambio el formato de las siguientes columnas para que me aparezcan números enteros
T1_2024_2004['ANO4'] = T1_2024_2004['ANO4'].astype(int)
T1_2024_2004['CH12'] = T1_2024_2004['CH12'].astype(int)
T1_2024_2004['CAT_INAC'] = T1_2024_2004['CAT_INAC'].astype(int)


### 2.b. Limpueza de la base de datos

# Veamos cuantos missings hay en cada variable:
missing_data = T1_2024_2004.isnull().sum()
print(missing_data)

# Eliminamos aquellas observaciones con missings o que no tienen sentido:   
    
# Monto de ingreso total individual - P47T:

T1_2024_2004 = T1_2024_2004[T1_2024_2004['P47T'] >= 0] #Elimino ingresos negativos y nan

#Edad Individuos - CH06:

T1_2024_2004 = T1_2024_2004[T1_2024_2004['CH06'] >= 0] #Elimino edades negativas y nan


### 2.c. Gráfico de barras mostrando la composición por sexo para 2004 y 2024

# Agrupamos y sumamos cantidad de individuos por género para cada año
comp_sexo = T1_2024_2004.groupby(['ANO4', 'CH04']).size().unstack()

# Creamos el gráfico de barras
ax = comp_sexo.plot(kind='bar', title='Composición del sexo para 1er Trimestre 2004 y 2024')
ax.set_xlabel('Año', color='grey')
ax.set_ylabel('Individuos Totales', color='grey')
ax.legend(["Mujeres", "Varones"])
plt.xticks(rotation=0)
plt.show()


### 2.d. Matriz de correlación para 2004 y 2024 con variables de interés

variables_interes = ['CH04', 'CH06', 'CH07', 'CH08', 'NIVEL_ED', 'ESTADO', 'CAT_INAC', 'IPCF']

# Filtramos los datos para 2004 y calculamos la correlación
data_2004 = T1_2024_2004[T1_2024_2004['ANO4'] == 2004][variables_interes]
corr_2004 = data_2004.corr()

# Replicamos para 2024
data_2024 = T1_2024_2004[T1_2024_2004['ANO4'] == 2024][variables_interes]
corr_2024 = data_2024.corr()

# Creamos el heatmap para 2004
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

# Creamos el heatmap para 2024
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


#2.e. Algunas estadísticas descriptivas

# Calcular el promedio de cada estado laboral por año
conteo_estado_anual = T1_2024_2004.groupby(['ANO4', 'ESTADO']).agg({"ESTADO": "count"})
print(conteo_estado_anual) 

#Hay 171 desocupados en 2004 y 86 en 2024.
#Hay 1065 unactivos en 2004 y 775 en 2024

IPCF_estado_anual = T1_2024_2004.groupby(['ANO4', 'ESTADO']).agg({"IPCF": "mean"})
print(IPCF_estado_anual) 

#2004: Ocupados (364.6), Desocupados (181.21) e Inactivos (260.30)
#2024: Ocupados (266394.39), Desocupados (134357.59) e Inactivos (187277.53)


#####Inciso 3

print(conteo_estado_anual) 
# Hay sólo una persona en el 2004 que no responde su condicion de actividad. 

# Guardamos en una base distinta aquellas obs que respondieron y las que no a la pregunta sobre su condición de actividad (ESTADO) 
respondieron = T1_2024_2004[T1_2024_2004['ESTADO'] != 0]
norespondieron = T1_2024_2004[T1_2024_2004['ESTADO'] == 0]


#####Inciso 4

# Nueva variable PEA si están ocupados o desocupados en ESTADO
respondieron['PEA'] = respondieron['ESTADO'].apply(lambda x: 1 if x in [1, 2] else 0)

# Gráfico de barras mostrando la composición por PEA para 2004 y 2024. 

PEA = respondieron.groupby(['ANO4', 'PEA']).size().unstack()

# Creo el gráfico de barras
ax = PEA.plot(kind='bar', title='Composición por PEA para el 1er Trimestre de 2004 y 2024')
ax.set_xlabel('Año', color='grey')
ax.set_ylabel('Individuos Totales', color='grey')
ax.legend(["PEA", "No PEA"])
plt.xticks(rotation=0)
plt.show()


#####Inciso 5

# Nueva variable PET que toma 1 si la persona tiene entre 15 y 65 años cumplidos
respondieron['PET'] = respondieron['CH06'].apply(lambda x: 1 if 15 <= x <= 65 else 0)

# Gráfico de barra mostrando la composición por PEA para 2004 y 2024

PEA_PET = respondieron.groupby(['ANO4', 'PEA', 'PET']).size().unstack(fill_value=0)
fig, ax = plt.subplots(figsize=(10, 6))
PEA_PET.plot(kind='bar', stacked=True, ax=ax, color=['#a6cee3', '#1f78b4'])

ax.set_title('Composición por PEA y PET para el 1er Trimestre de 2004 y 2024', fontsize=14)
ax.set_xlabel('Año y Estado PEA', color='grey', fontsize=12)
ax.set_ylabel('Individuos Totales', color='grey', fontsize=12)
ax.legend(["No PET", "PET"], title='Estado PET')
plt.xticks(rotation=45)
new_labels = []
for label in ax.get_xticklabels():
    text = label.get_text()
    year, pea = text.split(", ")
    pea_label = "No PEA" if pea.strip("()") == "0" else "PEA"
    new_labels.append(f"{year.strip('()')} - {pea_label}")

# Asignar las nuevas etiquetas
ax.set_xticklabels(new_labels, rotation=0)

plt.tight_layout()
plt.show()


#####Inciso 6

# Nueva variable desocupado, si esta desocupado toma valor 1 else 0.
respondieron['DESOCUPADO'] = respondieron['ESTADO'].apply(lambda x: 1 if x in [2] else 0)

# Vemos cuantos son los deocupados por año
frecuencia_desocupado = respondieron.groupby(['ANO4', 'DESOCUPADO']).size().unstack(fill_value=0)
print(frecuencia_desocupado) 

#2004: 171
#2024: 86

# Desocupación por nivel educativo:   
des_educ = respondieron.groupby(['ANO4', 'NIVEL_ED', 'DESOCUPADO']).size().unstack(fill_value=0)

# Invierto el diccionario que cree de educación para hacer la tabla mas prolija
mapa_instruccion_invertido = {v: k for k, v in mapa_instruccion.items()}
des_educ.rename(index=mapa_instruccion_invertido, level=1, inplace=True)
des_educ['Proporción_Desocupados'] = ((des_educ[1] / des_educ.sum(axis=1)) * 100).round(2)

print(des_educ[['Proporción_Desocupados']])


# Crear una nueva columna 'CH06_grupos' con los intervalos de edad de 10 en 10 años
respondieron['CH06_grupos'] = pd.cut(
    respondieron['CH06'],
    bins=range(0, 111, 10),  # Intervalos de 10 en 10 años, hasta 110
    right=False,              # Excluir el límite derecho en cada intervalo
    labels=[f"{i}-{i+10}" for i in range(0, 110, 10)]  # Etiquetas para cada grupo
)

# Chequeamos que el resultado sea el correcto
print(respondieron[['CH06', 'CH06_grupos']].head())

#TM: juanse comenta estas dos lineas
des_edad = respondieron.groupby(['ANO4', 'CH06_grupos', 'DESOCUPADO']).size().unstack(fill_value=0)
print(des_edad)


'''
----------------------------
 2. Parte II: Clasificación
----------------------------
'''

##### Inciso 1 

# Filtramos la base para cada año
respondieron_2004 = respondieron[respondieron['ANO4'] == 2004]
respondieron_2004.loc[:, 'TRIMESTRE'] = 1
respondieron_2024 = respondieron[respondieron['ANO4'] == 2024]

# Establecemos las variables dependientes e independientes

## Para 2004:
y_2004 = respondieron_2004.DESOCUPADO
x_2004 = respondieron_2004.loc[:, 'CH03':'NIVEL_ED'].drop(columns=['CH15_COD', 'CH16_COD']) 
## Para 2024:
y_2024 = respondieron_2024.DESOCUPADO
x_2024 = respondieron_2024.loc[:, 'CH03':'NIVEL_ED'].drop(columns=['CH15_COD', 'CH16_COD']) 

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


##### Inciso 2

# === Año 2004 === #

## Regresión Logística
log_reg_2004 = LogisticRegression(penalty=None).fit(x_2004_train, y_2004_train)
y_pred_log_2004 = log_reg_2004.predict(x_2004_test)
y_pred_prob_log_2004 = log_reg_2004.predict_proba(x_2004_test)[:, 1]

# Métricas para Regresión Logística (2004)
fpr_log_2004, tpr_log_2004, _ = roc_curve(y_2004_test, y_pred_prob_log_2004)
roc_auc_log_2004 = auc(fpr_log_2004, tpr_log_2004)

print("Regresión Logística - Año 2004")
print(f"Accuracy: {accuracy_score(y_2004_test, y_pred_log_2004):.4f}")
print(f"AUC: {roc_auc_log_2004:.4f}")
print(f"Matriz de Confusión:\n{confusion_matrix(y_2004_test, y_pred_log_2004)}")

## Análisis Discriminante Lineal (LDA, por sus siglas en inglés)
lda_2004 = LinearDiscriminantAnalysis()
lda_2004.fit(x_2004_train, y_2004_train)
y_pred_lda_2004 = lda_2004.predict(x_2004_test)
y_pred_prob_lda_2004 = lda_2004.predict_proba(x_2004_test)[:, 1]

# Métricas para LDA (2004)
fpr_lda_2004, tpr_lda_2004, _ = roc_curve(y_2004_test, y_pred_prob_lda_2004)
roc_auc_lda_2004 = auc(fpr_lda_2004, tpr_lda_2004)

print("\nAnálisis Discriminante Lineal - Año 2004")
print(f"Accuracy: {accuracy_score(y_2004_test, y_pred_lda_2004):.4f}")
print(f"AUC: {roc_auc_lda_2004:.4f}")
print(f"Matriz de Confusión:\n{confusion_matrix(y_2004_test, y_pred_lda_2004)}")

## KNN (k=3) 
knn_2004 = KNeighborsClassifier(n_neighbors=3)
knn_2004.fit(x_2004_train, y_2004_train)
y_pred_knn_2004 = knn_2004.predict(x_2004_test)
y_pred_prob_knn_2004 = knn_2004.predict_proba(x_2004_test)[:, 1]

# Métricas para KNN (2004)
fpr_knn_2004, tpr_knn_2004, _ = roc_curve(y_2004_test, y_pred_prob_knn_2004)
roc_auc_knn_2004 = auc(fpr_knn_2004, tpr_knn_2004)

print("\nKNN (k=3) - Año 2004")
print(f"Accuracy: {accuracy_score(y_2004_test, y_pred_knn_2004):.4f}")
print(f"AUC: {roc_auc_knn_2004:.4f}")
print(f"Matriz de Confusión:\n{confusion_matrix(y_2004_test, y_pred_knn_2004)}")

## Naive Bayes
nb_2004 = GaussianNB()
nb_2004.fit(x_2004_train, y_2004_train)
y_pred_nb_2004 = nb_2004.predict(x_2004_test)
y_pred_prob_nb_2004 = nb_2004.predict_proba(x_2004_test)[:, 1]

# Métricas para Naive Bayes (2004)
fpr_nb_2004, tpr_nb_2004, _ = roc_curve(y_2004_test, y_pred_prob_nb_2004)
roc_auc_nb_2004 = auc(fpr_nb_2004, tpr_nb_2004)

print("\nNaive Bayes - Año 2004")
print(f"Accuracy: {accuracy_score(y_2004_test, y_pred_nb_2004):.4f}")
print(f"AUC: {roc_auc_nb_2004:.4f}")
print(f"Matriz de Confusión:\n{confusion_matrix(y_2004_test, y_pred_nb_2004)}")

## Gráfico de Curvas ROC
plt.figure(figsize=(10, 6))
plt.plot(fpr_log_2004, tpr_log_2004, label=f"Reg. Logística (AUC = {roc_auc_log_2004:.4f})")
plt.plot(fpr_lda_2004, tpr_lda_2004, label=f"LDA (AUC = {roc_auc_lda_2004:.4f})")
plt.plot(fpr_knn_2004, tpr_knn_2004, label=f"KNN (AUC = {roc_auc_knn_2004:.4f})")
plt.plot(fpr_nb_2004, tpr_nb_2004, label=f"Naive Bayes (AUC = {roc_auc_nb_2004:.4f})")
plt.plot([0, 1], [0, 1], 'k--', label="Random Classifier")
plt.title("Curvas ROC - Año 2004")
plt.xlabel("Tasa de Falsos Positivos (FPR)")
plt.ylabel("Tasa de Verdaderos Positivos (TPR)")
plt.legend(loc="lower right")
plt.show()

# === Año 2024 === #

## Regresión Logística
log_reg_2024 = LogisticRegression(penalty=None).fit(x_2024_train, y_2024_train)
y_pred_log_2024 = log_reg_2024.predict(x_2024_test)
y_pred_prob_log_2024 = log_reg_2024.predict_proba(x_2024_test)[:, 1]

# Métricas para Regresión Logística (2024)
fpr_log_2024, tpr_log_2024, _ = roc_curve(y_2024_test, y_pred_prob_log_2024)
roc_auc_log_2024 = auc(fpr_log_2024, tpr_log_2024)

print("Regresión Logística - Año 2024")
print(f"Accuracy: {accuracy_score(y_2024_test, y_pred_log_2024):.4f}")
print(f"AUC: {roc_auc_log_2024:.4f}")
print(f"Matriz de Confusión:\n{confusion_matrix(y_2024_test, y_pred_log_2024)}")

## Análisis Discriminante Lineal (LDA, por sus siglas en inglés)
lda_2024 = LinearDiscriminantAnalysis()
lda_2024.fit(x_2024_train, y_2024_train)
y_pred_lda_2024 = lda_2024.predict(x_2024_test)
y_pred_prob_lda_2024 = lda_2024.predict_proba(x_2024_test)[:, 1]

# Métricas para LDA (2024)
fpr_lda_2024, tpr_lda_2024, _ = roc_curve(y_2024_test, y_pred_prob_lda_2024)
roc_auc_lda_2024 = auc(fpr_lda_2024, tpr_lda_2024)

print("\nAnálisis Discriminante Lineal - Año 2024")
print(f"Accuracy: {accuracy_score(y_2024_test, y_pred_lda_2024):.4f}")
print(f"AUC: {roc_auc_lda_2024:.4f}")
print(f"Matriz de Confusión:\n{confusion_matrix(y_2024_test, y_pred_lda_2024)}")

## KNN (k=3) 
knn_2024 = KNeighborsClassifier(n_neighbors=3)
knn_2024.fit(x_2024_train, y_2024_train)
y_pred_knn_2024 = knn_2024.predict(x_2024_test)
y_pred_prob_knn_2024 = knn_2024.predict_proba(x_2024_test)[:, 1]

# Métricas para KNN (2024)
fpr_knn_2024, tpr_knn_2024, _ = roc_curve(y_2024_test, y_pred_prob_knn_2024)
roc_auc_knn_2024 = auc(fpr_knn_2024, tpr_knn_2024)

print("\nKNN (k=3) - Año 2024")
print(f"Accuracy: {accuracy_score(y_2024_test, y_pred_knn_2024):.4f}")
print(f"AUC: {roc_auc_knn_2024:.4f}")
print(f"Matriz de Confusión:\n{confusion_matrix(y_2024_test, y_pred_knn_2024)}")

## Naive Bayes
nb_2024 = GaussianNB()
nb_2024.fit(x_2024_train, y_2024_train)
y_pred_nb_2024 = nb_2024.predict(x_2024_test)
y_pred_prob_nb_2024 = nb_2024.predict_proba(x_2024_test)[:, 1]

# Métricas para Naive Bayes (2024)
fpr_nb_2024, tpr_nb_2024, _ = roc_curve(y_2024_test, y_pred_prob_nb_2024)
roc_auc_nb_2024 = auc(fpr_nb_2024, tpr_nb_2024)

print("\nNaive Bayes - Año 2024")
print(f"Accuracy: {accuracy_score(y_2024_test, y_pred_nb_2024):.4f}")
print(f"AUC: {roc_auc_nb_2024:.4f}")
print(f"Matriz de Confusión:\n{confusion_matrix(y_2024_test, y_pred_nb_2024)}")

## Gráfico de Curvas ROC (2024)
plt.figure(figsize=(10, 6))
plt.plot(fpr_log_2024, tpr_log_2024, label=f"Reg. Logística (AUC = {roc_auc_log_2024:.4f})")
plt.plot(fpr_lda_2024, tpr_lda_2024, label=f"LDA (AUC = {roc_auc_lda_2024:.4f})")
plt.plot(fpr_knn_2024, tpr_knn_2024, label=f"KNN (AUC = {roc_auc_knn_2024:.4f})")
plt.plot(fpr_nb_2024, tpr_nb_2024, label=f"Naive Bayes (AUC = {roc_auc_nb_2024:.4f})")
plt.plot([0, 1], [0, 1], 'k--', label="Random Classifier")
plt.title("Curvas ROC - Año 2024")
plt.xlabel("Tasa de Falsos Positivos (FPR)")
plt.ylabel("Tasa de Verdaderos Positivos (TPR)")
plt.legend(loc="lower right")
plt.show()


#####Inciso 4

# Seleccionamos variables independientes en norespondieron  
x_noresp = norespondieron.loc[:, 'CH03':'NIVEL_ED'].drop(columns=['CH15_COD', 'CH16_COD'])

# Creamos variables dummies asegurando consistencia
x_noresp = pd.get_dummies(x_noresp, drop_first=True)

# Reindexamos para alinear las columnas con x_2024 y garantizar compatibilidad en el modelo
x_noresp = x_noresp.reindex(columns=x_2004.columns, fill_value=0)  

# Asegurar que el orden y las columnas sean consistentes
x_noresp = x_noresp[x_2004.columns]

# Reindexar las columnas de x_noresp para que coincidan con las columnas utilizadas en el modelo
x_noresp = x_noresp.reindex(columns=x_2004.columns, fill_value=0)

# Predecimos la probabilidad de desocupación en norespondieron usando el modelo entrenado
y_pred_noresp = knn_2004.predict(x_noresp)

# Calcular la proporción de desocupados en la base norespondieron
proporcion_desocupados = np.mean(y_pred_noresp)

print(f"Proporción de personas identificadas como desocupadas en la base norespondieron: {proporcion_desocupados:.2%}")