import numpy as np
'''
Funciones esenciales
'''
# Matriz de transformación de coordenadas del sistema inercial al cuerpo
def T_L2B(psi,theta,phi):
    psi = np.radians(psi)
    theta = np.radians(theta)
    phi = np.radians(phi)
    return np.array(
        [
            [np.cos(theta)*np.cos(phi), np.cos(theta)*np.sin(phi), np.sin(theta)],
            [-np.sin(psi)*np.sin(theta)*np.cos(phi) - np.cos(psi)*np.sin(phi), -np.sin(psi)*np.sin(theta)*np.sin(phi) + np.cos(psi)*np.cos(phi), np.sin(psi)*np.cos(theta)],
            [np.cos(psi)*np.sin(theta)*np.cos(phi) - np.sin(psi)*np.sin(phi), -np.cos(psi)*np.sin(theta)*np.sin(phi) - np.sin(psi)*np.cos(phi), np.cos(psi)*np.cos(theta)]
        ]
    )

# Matriz de transformación de coordenadas del cuerpo al sistema inercial
def T_B2L(psi,theta,phi):
    psi = np.radians(psi)
    theta = np.radians(theta)
    phi = np.radians(phi)
    return np.array(
        [
            [np.cos(theta)*np.cos(phi), np.cos(psi)*np.sin(theta)*np.cos(phi) - np.sin(psi)*np.sin(phi), np.cos(psi)*np.sin(theta)*np.cos(phi) - np.sin(psi)*np.sin(phi)],
            [np.cos(theta)*np.sin(phi), -np.sin(psi)*np.sin(theta)*np.sin(phi) + np.cos(psi)*np.cos(phi), -np.cos(psi)*np.sin(theta)*np.sin(phi) - np.sin(psi)*np.cos(phi)],
            [np.sin(theta), np.sin(psi)*np.cos(theta), np.cos(psi)*np.cos(theta)]
        ]
    )


# Calculamos el centro de gravedad del proyectil completo
def centro_gravedad(masas, centros_de_gravedad):
    # Aseguramos que masas sea un arreglo columna para poder usar broadcasting correctamente
    masas = masas[:, np.newaxis]
    # Calculamos el centro de gravedad del sistema
    return np.sum(masas * centros_de_gravedad, axis=0) / np.sum(masas)

# Calculamos los momentos de inercia I_xx, I_yy, I_zz
def Momento_inercia(masa, h, r_2, r_1 = 0, dist_a_cm = 0):
    # Momento de inercia de un cilindro de radio exterior r_2, radio interior r_1 y altura h, con centro en su eje de simetría
    I_xx = 1/2*masa*(r_2**2 + r_1**2)**2
    # I_yy = I_zz ya que hay simetría en el eje x
    I_yy = 1/12*masa*(3*(r_2**2 + r_1**2)**2 + h**2) + masa*dist_a_cm**2 # Teorema de Steiner
    I_zz = I_yy
    return np.array([I_xx, I_yy, I_zz])

def der_Momento_inercia(m_dot, h, r_2, r_1 = 0, dist_a_cm = 0):
    # Derivada del momento de inercia respecto al tiempo
    I_xx_dot = 1/2*m_dot*(r_2**2 + r_1**2)**2
    I_yy_dot = 1/12*m_dot*(3*(r_2**2 + r_1**2)**2 + h**2) + m_dot*dist_a_cm**2
    I_zz_dot = I_yy_dot
    return np.array([I_xx_dot, I_yy_dot, I_zz_dot])

def torque(centro_de_gravedad, aplicacion_de_las_fuerzas, fuerzas):
    
    # Calculamos en qué punto se aplican cada una de las fuerzas con respecto al centro de gravedad
    distancias = centro_de_gravedad - aplicacion_de_las_fuerzas
    
    # Calculamos el torque total
    torque_total = np.zeros(3)
    for fuerza, distancia in zip(fuerzas, distancias):
        torque_total += np.cross(distancia, fuerza)
        
    return torque_total