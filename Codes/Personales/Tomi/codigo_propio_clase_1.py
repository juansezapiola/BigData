# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

# Listas
paises = ['ARG', 'BOL', 'BRA', 'CHI', 'PRY', 'URY']
pob_millones = [46,12,214,19,13,3.5]

# Hacemos loops
lista_paises = ['Argentina', 'Bolivia', 'Chile']

print(lista_paises[0])
print(lista_paises[1])
print(lista_paises[2])

# O lo puedo hacer de manera iterativa (loop)

for pais in lista_paises: 
    print('Nombre: ' + pais)
    
# Acá digo cuando termina el loop con las sangrías

for pais in lista_paises: 
    print('Nombre: ' + pais)
    print('hola')

for pais in lista_paises: 
    print('Nombre: ' + pais)
print('hola') # Acá me ejecuta el loop pero no mete el 'hola' dentro del loop

# Otra forma de hacer el loop

for pais in enumerate(lista_paises):
    print(pais)
# Me imprime una tupla


for n, pais in enumerate(lista_paises): # n es el número que tenía la tupla
    print(n, ":", pais)
    
    
for n, pais in enumerate(paises):
    print(pais, ":", pob_millones[n])
    
# Iterar a través de números 

for i in range(2,8,2): # iterame entre el número 2 y el 8 en intervalos de a 2 
    print(i)  
# No imprime el 8 porque el último nunca lo incluye

## WHILE LOOP --> repetí el loop hasta que pase determinada condición
x = 0
while x < 3: 
    print(x)
    x +=1 #esto es x = a lo que era x + 1 
    
## CONDICIONALES

edad = 25 

if edad < 18: 
    print("Menor de edad")
elif edad >= 18 or edad <= 30 :
    print("Mayor de edad")
else:
    print("No se admiten mayores de 30")
    
#

listado_numeros = [10,11,12,23]

for numero in listado_numeros: 
    if numero %2 == 0 and numero % 3 == 0:
        print(numero, 'es divisible por 6')
    elif numero % 2 == 0: # "%"significa resto
        print(numero, "es par")
    else:
        print(numero, "es impar")
        
        
## FUNCIONES

def pbi_per_capita(pbi_millones, pob_millones):
    pbi_pc = pbi_millones / pob_millones
    return pbi_pc

# Ver código tomi
# Si quiero cambiar de orden de como pongo los argumentos de la función tengo que especificar 


def pbi_per_capita2(pbi, pob, pbi_mm = False): 
    if pbi_mm == True: 
        pbi_pc = round(pbi*1000/pob) #round para redondear el número
    else: 
        pbi_pc = round(pbi/pob)
    return pbi_pc

print(pbi_per_capita2(1810612, 211))
print(pbi_per_capita2(1810.612, 211, pbi_mm = True))

def pbi_per_capita(pbi_millones, pob_millones):
    """
    Esta función calcula el PBI per capita

    Parameters
    ----------
    pbi_millones : es el pBI en millones del país 'X'
    pob_millones : Es la población en millos del país 'X'

    Returns
    -------
    La función devuelve el PBI per capita del país 'X'
    """

print(pbi_per_capita.__doc__)


# Siempre es importante ir imprimiendo para ir viendo lo que uno va haciendo.








        
