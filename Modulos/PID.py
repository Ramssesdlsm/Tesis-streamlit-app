import random
import numpy as np
from math import exp

'''
Control PID
'''
class PID:
    def __init__(self, Kp, Ki, Kd, setpoint=0):
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd
        self.setpoint = setpoint
        self._last_error = 0
        self._integral = 0
    
    def compute(self, current_value, dt):
        error = self.setpoint - current_value
        self._integral += error * dt
        derivative = (error - self._last_error) / dt
        output = self.Kp * error + self.Ki * self._integral + self.Kd * derivative
        self._last_error = error
        return output
    
'''
    Busqueda de los nuevos parametros de control
'''
# Buscaremos los mejores parámetros de control utilizando el algoritmo de recodido simulado
# La función a minimizar en este caso es la distancia al cuadrado promedio entre la trayectoria con control y la trayectoria deseada
# Definimos la función de costo
def costo(x, y, z, x_d, y_d, z_d):
    # Convertimos las listas a numpy
    x = np.array(x)
    y = np.array(y)
    z = np.array(z)
    x_d = np.array(x_d)
    y_d = np.array(y_d)
    z_d = np.array(z_d)
    return np.mean((x - x_d)**2 + (y - y_d)**2 + (z - z_d)**2)/(np.mean(x_d**2 + y_d**2 + z_d**2))

# Definimos la función de aceptación
def recocido_simulado(parametros_control, x_con_control, y_con_control, z_con_control, x_p, y_p, z_p, T, T_min, alpha, rango_numeros, indice, masas, velocidad, angulos, centros_de_gravedad, radios_cuerpos, alturas_cuerpos, parametros_combustible, tiempo_integracion, trayectoria, escala_ruido, ruido_hist):
    from .Simulacion import simulacion_proyectil
    s_0 = costo(x_con_control, y_con_control, z_con_control, x_p, y_p, z_p)
    parametros_s0 = parametros_control
    while T > T_min:
        # No perturbaremos todos los parámetros al mismo tiempo, primero perturbaremos el primer parámetro[0] y veamos si mejora, si no, perturbaremos el segundo parámetro[1] y así sucesivamente
        for i in range(3):
            parametros_s_n = parametros_s0.copy()
            parametros_s_n[i] = random.uniform(0, rango_numeros)
            x_con_control, y_con_control, z_con_control, aux = simulacion_proyectil(masas, velocidad, angulos, centros_de_gravedad, radios_cuerpos, alturas_cuerpos, parametros_combustible, tiempo_integracion, parametros_s_n,trayectoria=trayectoria, escala_ruido=escala_ruido, ruido_hist=ruido_hist) 
            s_n = costo(x_con_control[:indice], y_con_control[:indice], z_con_control[:indice], x_p, y_p, z_p)
            delta_E = s_n - s_0
            if delta_E <= 0:
                s_0 = s_n
                parametros_s0 = parametros_s_n.copy()
            else:
                if random.random() < exp(-delta_E/T):
                    s_0 = s_n
                    parametros_s0 = parametros_s_n.copy()
        T *= alpha
    return s_0, parametros_s0