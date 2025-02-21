#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
-------------------------------------------------------------------------------
------------------------- PONER TITULO TRABAJO ------------------------

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
#os.chdir('/Users/juansegundozapiola/Documents/Maestria/Big Data/BigData/RP')
os.chdir('/Users/tomasmarotta/Documents/GitHub/BigData/RP')


'''
--------------------------------
1. Estadísticas Descriptivas 
--------------------------------
'''

#Abrimos base de datos
MWI_adoption = pd.read_stata("input/MWI_final.dta")






















