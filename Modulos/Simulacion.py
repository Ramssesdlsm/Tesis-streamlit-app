
import numpy as np
import random
from .Fisica_Matematica import T_L2B, T_B2L, centro_gravedad, Momento_inercia, der_Momento_inercia, torque
from .PID import PID

'''
Simulación
'''
def simulacion_proyectil(masas, velocidad, angulos, centros_de_gravedad, radios_cuerpos, alturas_cuerpos, parametros_combustible, tiempo_integracion, parametros_control = [0.0, 0.0, 0.0],trayectoria = 0, escala_ruido = 0, ruido_hist = 0):

    # Definimos las variables locales
    m_parte_sup, m_combustible, m_proyectil = masas
    centro_gravedad_parte_sup, centro_gravedad_combustible, centro_gravedad_proyectil = centros_de_gravedad
    h_parte_sup, h_combustible, h_proyectil = alturas_cuerpos
    r_ext_parte_sup, r_ext_combustible, r_ext_proyectil, r_int_proyectil = radios_cuerpos
    g = 9.81
    
    # Obtenemos los parámetros relacionado a la quema de combustible
    m_dot_combustible, u_relativa, delta_P, A = parametros_combustible
    m_change = m_dot_combustible
    # Angulos con el vector de velocidad
    xy_angle, z_angle = angulos

    # Tamaño de paso
    dt = 0.01

    # Fuerza de empuje
    F_E = m_dot_combustible * u_relativa + delta_P*A

    # Ruido
    ruido = escala_ruido*F_E
    # Calculamos los ángulos de euler
    angulos_euler = np.array([
        [0.0],
        [z_angle],
        [xy_angle]
    ])
    # Velocidad angular
    omega = np.zeros((3,1))
    # Aceleracion angular del sistema
    omega_dot = np.zeros((3,1))

    # Velocidad angular (angulos de euler) (psi_dot, phi_dot, theta_dot
    velocidad_angular = np.zeros((3,1))

    # Vector de velocidad en el sistema inercial
    v_L = np.array([
        [velocidad*np.cos(xy_angle)*np.cos(z_angle)],
        [velocidad*np.sin(xy_angle)*np.cos(z_angle)],
        [velocidad*np.sin(z_angle)]
    ])

    # Posición en el sistema inercial
    p_L = np.zeros((3,1))

    # Posiciones deseadas para el control
    if trayectoria:
        x_c, y_c, z_c = trayectoria
    
    # Inicializamos los controladores PID para cada eje
    pid_x = PID(Kp=parametros_control[0], Ki=parametros_control[1], Kd=parametros_control[2])
    pid_y = PID(Kp=parametros_control[0], Ki=parametros_control[1], Kd=parametros_control[2])
    pid_z = PID(Kp=parametros_control[0], Ki=parametros_control[1], Kd=parametros_control[2])

    # Realizamos la simulación
    x, y, z = [], [], []
    i = 0
    guardar_ruido = []
    while tiempo_integracion > 0:
        psi = angulos_euler[0][0]
        theta = angulos_euler[1][0]
        phi = angulos_euler[2][0]
        
        # Calculo de la masa actual
        if m_combustible - m_dot_combustible*dt >= 0:
            m_combustible -= m_dot_combustible*dt
            m = m_proyectil + m_parte_sup + m_combustible
        else:
            m = m_proyectil + m_parte_sup
            m_change = 0
            F_E = 0
        
        

        '''
        Perturbación
        '''
        # Creamos una fuerza aleatoria de perturbación y el punto donde se aplica si no hay historial de ruido
        if not ruido_hist:
            F_px = random.uniform(-1,1)*ruido
            F_py = random.uniform(-1,1)*ruido
            F_pz = random.uniform(-1,1)*ruido
            # Generamos el punto en el proyectil donde se aplica la fuerza
            r_perturbacion = np.array([random.uniform(0,h_proyectil), 0.0, 0.0])
        else:
            F_px, F_py, F_pz, x_perturbacion = ruido_hist[i]
            r_perturbacion = np.array([x_perturbacion, 0.0, 0.0])
            
        guardar_ruido.append([F_px, F_py, F_pz, r_perturbacion[0]])

        '''
        Control
        '''
        if trayectoria:
            # Ajustamos los setpoints de los PID para el punto actual en la trayectoria
            pid_x.setpoint = x_c[i]
            pid_y.setpoint = y_c[i]
            pid_z.setpoint = z_c[i]

            # Controladores PID para ajustar los ángulos
            control_x = pid_x.compute(p_L[0][0], dt)
            control_y = pid_y.compute(p_L[1][0], dt)
            control_z = pid_z.compute(p_L[2][0], dt)
            
        else: 
            control_x = 0.0
            control_y = 0.0
            control_z = 0.0
        
        # Supondremos que las fuerzas de control se aplican en la base del proyectil
        r_control = np.array([0.0, 0.0, 0.0])

        #fuerza_control.append([control_x, control_y, control_z])

        '''
        Dinámica traslacional
        '''
        
        # Calculo de la fuerza en el sistema del cuerpo
        F_B = np.array([
            [F_E + F_px + control_x],
            [F_py + control_y],
            [F_pz + control_z]
        ])
        # Calculo de la fuerza en el sistema inercial sin tomar la gravedad
        F_L = np.dot(T_B2L(psi, theta, phi), F_B)

        # Calculo de la aceleración en el sistema inercial
        a_L = np.array([
            [F_L[0][0]/m],
            [F_L[1][0]/m],
            [(F_L[2][0]-m*g)/m]
        ])

        # Calculo de la velocidad en el sistema inercial
        v_L += a_L*dt

        # Calculo de la posición en el sistema inercial
        p_L += v_L*dt

        # No los utilizamos actualmente ya que no hay viento en el modelo
        a_B = np.dot(T_L2B(psi, theta, phi),a_L)+np.array([
            [omega[2][0]*v_L[1][0]-omega[1][0]*v_L[2][0]],
            [omega[0][0]*v_L[2][0]-omega[2][0]*v_L[0][0]],
            [omega[1][0]*v_L[0][0]-omega[0][0]*v_L[1][0]]
        ])
        v_B = np.dot(T_L2B(psi, theta, phi),v_L)

            
        '''
        Dinámica rotacional
        '''

        # Calculamos la posición del centro de gravedad
        cm = centro_gravedad(np.array([m_parte_sup, m_combustible, m_proyectil]), np.array([centro_gravedad_parte_sup, centro_gravedad_combustible, centro_gravedad_proyectil]))
        
        # Calculamos las posiciones del centro de gravedad de cada parte con respecto al centro de gravedad del sistema
        dist_cm_parte_sup = centro_gravedad_parte_sup[0] - cm[0]
        dist_cm_combustible = centro_gravedad_combustible[0] - cm[0]
        dist_cm_proyectil = centro_gravedad_proyectil[0] - cm[0]
        
        # Calculamos el momento de inercia total de las 3 masas
        I_parte_sup = Momento_inercia(m_parte_sup, h_parte_sup, r_ext_parte_sup, dist_a_cm=dist_cm_parte_sup)
        I_combustible = Momento_inercia(m_combustible, h_combustible, r_ext_combustible, dist_a_cm=dist_cm_combustible)
        I_proyectil = Momento_inercia(m_proyectil, h_proyectil, r_ext_proyectil, r_int_proyectil, dist_a_cm=dist_cm_proyectil)
        I_xx = I_parte_sup[0] + I_combustible[0] + I_proyectil[0]
        I_yy = I_parte_sup[1] + I_combustible[1] + I_proyectil[1]
        I_zz = I_parte_sup[2] + I_combustible[2] + I_proyectil[2]

        # Derivamos los momentos de inercia respecto al tiempo, la masa cambia por lo cual dm/dt = m_dot
        I_dot_parte_sup = [0.0,0.0,0.0] # La masa no varía
        I_dot_combustible = der_Momento_inercia(m_change, h_combustible, r_ext_combustible, dist_a_cm=dist_cm_combustible)
        I_dot_proyectil = [0.0,0.0,0.0] # La masa no varía
        I_xx_dot = I_dot_parte_sup[0] + I_dot_combustible[0] + I_dot_proyectil[0]
        I_yy_dot = I_dot_parte_sup[1] + I_dot_combustible[1] + I_dot_proyectil[1]
        I_zz_dot = I_dot_parte_sup[2] + I_dot_combustible[2] + I_dot_proyectil[2]
    
        # El torque debido al peso es cero
        M_total = [0.,0.,0.] 
        
        # Calculamos el torque debido a la fuerza de perturbacion y al control
        Torque_pyc = torque(cm, np.array([r_perturbacion, r_control]), np.array([[F_px, F_py, F_pz], [control_x, control_y, control_z]]))
        
        # Calculamos el torque total
        M_x = M_total[0] + Torque_pyc[0]
        M_y = M_total[1] + Torque_pyc[1]
        M_z = M_total[2] + Torque_pyc[2]
        
        # Calculamos la aceleración angular
        omega_dot = np.array([
            [((I_yy - I_zz)*omega[1][0]*omega[2][0] - I_xx_dot*omega[0][0] + M_x)/I_xx],
            [((I_zz - I_xx)*omega[0][0]*omega[2][0] - I_yy_dot*omega[1][0] + M_y)/I_yy],
            [((I_xx - I_yy)*omega[0][0]*omega[1][0] - I_zz_dot*omega[2][0] + M_z)/I_zz]
        ])
        
        # Actualizamos la velocidad angular (método de Euler)
        omega += omega_dot*dt
        
        # Calculamos la velocidad angular en el sistema de cuerpo
        velocidad_angular = np.array([
            [omega[0][0] - omega[1][0]*np.sin(psi)*np.tan(theta) - omega[2][0]*np.cos(psi)*np.tan(theta)],
            [omega[1][0]*np.cos(psi) - omega[2][0]*np.sin(psi)],
            [-omega[1][0]*np.sin(psi)/np.cos(theta) + omega[2][0]*np.cos(psi)/np.cos(theta)]
        ])
        
        # Actualizamos los angulos de Euler (método de Euler)
        angulos_euler += velocidad_angular*dt

        # Guardamos las posiciones actuales
        x.append(p_L[0][0])
        y.append(p_L[1][0])
        z.append(p_L[2][0])

        # if p_L[2][0] < 0:
        #     break
        
        tiempo_integracion -= dt
        i += 1
    return x, y, z, guardar_ruido
