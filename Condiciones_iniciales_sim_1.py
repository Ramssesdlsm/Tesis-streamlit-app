import numpy as np

'''
    Condiciones iniciales
'''

# Masa de cada componente
m_parte_sup = 1.0
m_combustible = 2.0
m_proyectil = 1.0

# Agregamos las masas en un arreglo
masas = [m_parte_sup, m_combustible, m_proyectil]

# Tasa de perdida de masa del combustible
m_dot_combustible = 0.1

# Gravedad
g = 9.81

# Centro de gravedad inicial respecto a la base del proyectil
centro_gravedad_parte_sup = np.array([1.5, 0.0, 0.0])
centro_gravedad_combustible = np.array([0.5, 0.0, 0.0])
centro_gravedad_proyectil = np.array([1.0, 0.0, 0.0])

# Agregamos los centros de gravedad en un arreglo
centros_de_gravedad = [centro_gravedad_parte_sup, centro_gravedad_combustible, centro_gravedad_proyectil]

# Altura de cada parte
h_parte_sup = 1.0
h_combustible = 1.0
h_proyectil = 2.0

# Agregamos las alturas en un arreglo
alturas_cuerpos = [h_parte_sup, h_combustible, h_proyectil]

# Radios de cada parte
r_ext_parte_sup = 0.1
r_ext_combustible = 0.1
r_ext_proyectil = 0.2
r_int_proyectil = 0.15

# Agregamos los radios en un arreglo
radios_cuerpos = [r_ext_parte_sup, r_ext_combustible, r_ext_proyectil, r_int_proyectil]

# Escala de ruido (en porcentaje del empuje)
escala_ruido = 0.20

# Velocidad de la masa eyectada
u_relativa = 10.0
# Diferencia de presión en Pa
delta_P = 1000.0
# Area de la tobera
A = 0.03
# Agregamos los parámetros del combustible en un arreglo
parametros_combustible = [m_dot_combustible, u_relativa, delta_P, A]

# Magnitud de la velocidad de traslación
velocidad = 100.0
# Angulos iniciales
xy_angle = np.radians(45)
z_angle = np.radians(75)
# Agregamos los angulos en un arreglo
angulos = [xy_angle, z_angle]

# Tiempo de integración
tiempo_integracion = 25.0