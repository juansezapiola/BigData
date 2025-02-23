#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
-------------------------------------------------------------------------------
------------------------- PREDICCIÓN DE ADOPCIÓN DE SEMILLAS GM ------------------------

--     Machine Learning para Economistas - Universidad de San Andrés         --


-  @authors: Tomás Marotta, Eitan Salischiker, Juan Segundo Zapiola           -

-                           Date: February 28, 2025                            -
-------------------------------------------------------------------------------
"""

'''
----------
  INDEX
----------

0. SETEO DEL ESPACIO DE TRABAJO 
1. Estadísticas Descriptivas
2. Modelado y Predicción

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
from sklearn.linear_model import LogisticRegression, LassoCV, RidgeCV, Lasso, Ridge
from sklearn.impute import SimpleImputer  # Para manejar valores NaN
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import confusion_matrix, accuracy_score, roc_curve, auc, mean_squared_error

# Gráficos
import matplotlib.pyplot as plt

## Definimos el directorio de trabajo
os.chdir('C:/Users/marottat/Desktop/')

'''
--------------------------------
1. Estadísticas Descriptivas 
--------------------------------
'''

# Abrimos la base de datos
MWI_adoption = pd.read_stata("MWI_final.dta")

# Verificamos la estructura del dataset
print(MWI_adoption.info())
print(MWI_adoption.describe())

# Frecuencia de la variable dependiente
print(MWI_adoption["hh_improved"].value_counts())

'''
--------------------------------
2. Modelado y Predicción
--------------------------------
'''

# Definimos la variable dependiente y las predictoras
target = "hh_improved"  # Variable a predecir
features = [col for col in MWI_adoption.columns if col != target]  # Todas las demás como predictoras

# Dividir en conjunto de entrenamiento y prueba
X = MWI_adoption[features]
y = MWI_adoption[target]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=101)

# Manejo de valores NaN: imputación con la media
imputer = SimpleImputer(strategy="mean")
X_train = imputer.fit_transform(X_train)
X_test = imputer.transform(X_test)

# Estandarización de variables
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

'''
--------------------------------
Regresión Logística con Regularización
--------------------------------
'''

# Entrenar modelo de regresión logística con regularización Lasso
lasso = LassoCV(cv=10, max_iter=10000, random_state=101)
lasso.fit(X_train_scaled, y_train)
y_pred_lasso = lasso.predict(X_test_scaled)

# Evaluación de Lasso
mse_lasso = mean_squared_error(y_test, y_pred_lasso)
print(f"Error Cuadrático Medio (Lasso): {mse_lasso:.4f}")

# Entrenar modelo de regresión logística con regularización Ridge
ridge = RidgeCV(alphas=np.logspace(-5, 5, 50), cv=10)
ridge.fit(X_train_scaled, y_train)
y_pred_ridge = ridge.predict(X_test_scaled)

# Evaluación de Ridge
mse_ridge = mean_squared_error(y_test, y_pred_ridge)
print(f"Error Cuadrático Medio (Ridge): {mse_ridge:.4f}")

# Obtener la mejor penalización (lambda) para Lasso y Ridge
print(f"Lambda óptima Lasso: {lasso.alpha_:.4f}")
print(f"Lambda óptima Ridge: {ridge.alpha_:.4f}")

'''
--------------------------------
Métricas de Desempeño
--------------------------------
'''

# Convertir predicciones continuas en clasificación binaria
y_pred_lasso_binary = (y_pred_lasso > 0.5).astype(int)
y_pred_ridge_binary = (y_pred_ridge > 0.5).astype(int)

# Matriz de Confusión
conf_matrix_lasso = confusion_matrix(y_test, y_pred_lasso_binary)
conf_matrix_ridge = confusion_matrix(y_test, y_pred_ridge_binary)

print("Matriz de Confusión - Lasso:\n", conf_matrix_lasso)
print("Matriz de Confusión - Ridge:\n", conf_matrix_ridge)

'''
--------------------------------
Curvas ROC
--------------------------------
'''

# Calcular Curvas ROC
fpr_lasso, tpr_lasso, _ = roc_curve(y_test, y_pred_lasso)
fpr_ridge, tpr_ridge, _ = roc_curve(y_test, y_pred_ridge)

roc_auc_lasso = auc(fpr_lasso, tpr_lasso)
roc_auc_ridge = auc(fpr_ridge, tpr_ridge)


# Graficar Curvas ROC
plt.figure(figsize=(8, 6))
plt.plot(fpr_lasso, tpr_lasso, label=f"Lasso (AUC = {roc_auc_lasso:.4f})", linestyle='--')
plt.plot(fpr_ridge, tpr_ridge, label=f"Ridge (AUC = {roc_auc_ridge:.4f})", linestyle='-')
plt.plot([0, 1], [0, 1], 'k--', label="Random Classifier")
plt.xlabel("Tasa de Falsos Positivos (FPR)")
plt.ylabel("Tasa de Verdaderos Positivos (TPR)")
plt.title("Curvas ROC para Lasso y Ridge")
plt.legend()
plt.grid()
plt.show()