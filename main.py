import streamlit as st
import numpy as np
from Modulos import simulacion_proyectil, recocido_simulado
# Importamos plotly
import plotly.graph_objects as go

st.title('Simulación de la trayectoria de un proyectil')

st.header('Condiciones iniciales')
seleccion_condiciones = st.selectbox('¿Desea trabajar con las condiciones iniciales por defecto', ('Sí', 'No'))
if seleccion_condiciones == 'Sí':
    cual_condicion = st.selectbox('Seleccione las condiciones iniciales con las que desea trabajar', ('Condiciones iniciales 2', 'Condiciones iniciales 1'))
    if cual_condicion == 'Condiciones iniciales 1':
        # Importamos las condiciones iniciales del archivo Condiciones_iniciales_sim_1.py
        from Condiciones_iniciales_sim_1 import masas, centros_de_gravedad, alturas_cuerpos, radios_cuerpos, parametros_combustible, velocidad, angulos, tiempo_integracion, escala_ruido
    else:
        # Importamos las condiciones iniciales del archivo Condiciones_iniciales_sim_2.py
        from Condiciones_iniciales_sim_2 import masas, centros_de_gravedad, alturas_cuerpos, radios_cuerpos, parametros_combustible, velocidad, angulos, tiempo_integracion, escala_ruido
else:
    # Pedimos que ingrese las condiciones iniciales, para ello crearemos una tabla para que el usuario ingrese allí los valores
    st.subheader('Ingrese las condiciones iniciales')
    st.write('Condiciones iniciales de los componentes del proyectil')
    g = 9.81
    masas = []
    centros_de_gravedad = []
    alturas_cuerpos = []
    radios_cuerpos = []
    parametros_combustible = []
    velocidad = 0.0
    angulos = []
    tiempo_integracion = 0.0
    escala_ruido = 0.0

    # Crear 3 columnas
    col1, col2, col3 = st.columns(3)

    # Lista de elementos
    elementos = ['parte_sup', 'combustible', 'proyectil']

    # Asignar cada elemento a una columna
    for i, elemento in enumerate(elementos):
        if i % 3 == 0:
            col = col1
        elif i % 3 == 1:
            col = col2
        else:
            col = col3

        with col:
            if elemento == 'proyectil':
                masas.append(st.number_input(f'Masa {elemento}', value=0.0, key=f'masa_{elemento}'))
                centros_de_gravedad.append(st.text_input(f'Centro de gravedad {elemento}', value='', key=f'cg_{elemento}'))
                alturas_cuerpos.append(st.number_input(f'Altura {elemento}', value=0.0, key=f'altura_{elemento}'))
                radios_cuerpos.append(st.number_input(f'Radio exterior {elemento}', value=0.0, key=f'radio_ext_{elemento}'))
                radios_cuerpos.append(st.number_input(f'Radio interior {elemento}', value=0.0, key=f'radio_int_{elemento}'))
            else:
                masas.append(st.number_input(f'Masa {elemento}', value=0.0, key=f'masa_{elemento}'))
                centros_de_gravedad.append(st.text_input(f'Centro de gravedad {elemento}', value='', key=f'cg_{elemento}'))
                alturas_cuerpos.append(st.number_input(f'Altura {elemento}', value=0.0, key=f'altura_{elemento}'))
                radios_cuerpos.append(st.number_input(f'Radio {elemento}', value=0.0, key=f'radio_{elemento}'))
    
    st.markdown("---")

    # Crear 3 columnas para las nuevas secciones
    col4, col5, col6 = st.columns(3)

    # Primera nueva sección
    with col4:
        st.write('Parámetros asociados al combustible')
        parametros_combustible.append(st.number_input('Tasa de perdida de masa del combustible', value=0.0))
        parametros_combustible.append(st.number_input('Velocidad de la masa eyectada', value=0.0))
        parametros_combustible.append(st.number_input('Diferencia de presión en Pa', value=0.0))
        parametros_combustible.append(st.number_input('Area de la tobera', value=0.0))

    # Segunda nueva sección
    with col5:
        st.write('Orientación y velocidad del proyectil')
        velocidad = st.number_input('Velocidad de salida del proyectil', value=0.0)
        angulos.append(np.radians(st.number_input('Ángulo XY', value=0.0)))
        angulos.append(np.radians(st.number_input('Ángulo Z', value=0.0)))

    # Tercera nueva sección
    with col6:
        st.write('Tiempo de integración y escala de ruido')
        tiempo_integracion = st.number_input('Tiempo de integración', value=0.0)
        escala_ruido = st.number_input('Escala de ruido', value=0.0)



st.header('Perturbaciones')

seleccion_perturbaciones = st.selectbox('¿Desea trabajar con las perturbaciones por defecto?', ('Sí', 'No'))
if seleccion_perturbaciones == 'Sí':
    cual_perturbacion = st.selectbox('Seleccione las perturbaciones con las que desea trabajar', ('Perturbaciones 2', 'Perturbaciones 1'))
    if cual_perturbacion == 'Perturbaciones 1':
        # Cargamos el archivo de perturbación 1
        ruido_hist = np.loadtxt('Ruido_sim_1.txt', delimiter=',').tolist()
    else:
        # Cargamos el archivo de perturbación 2
        ruido_hist = np.loadtxt('Ruido_sim_2.txt', delimiter=',').tolist()
else:
    seleccion_de_carga = st.selectbox('¿Desea cargar un archivo de perturbaciones?', ('No', 'Sí'))
    # Cargar archivo de perturbaciones
    if seleccion_de_carga == 'Sí':
        archivo = st.file_uploader('Seleccione el archivo de perturbaciones', type='txt')
        if archivo is not None:
            ruido_hist = np.loadtxt(archivo, delimiter=',').tolist()
    else:
        ruido_hist = 0

st.header('Control')
# Pedimos que ingrese los parámetros de control
st.write('Ingrese los parámetros de control') # Estos son los default [0.05, 0.01, 0.01]
# Los ponemos en columnas
col1, col2, col3 = st.columns(3)
with col1:
    K_p = st.number_input('K_p', value=0.05)
with col2:
    K_i = st.number_input('K_i', value=0.01)
with col3:
    K_d = st.number_input('K_d', value=0.01)

parametros_control = [K_p, K_i, K_d]

st.header('Resultados')

try:
    #'''
    #    Trayectoria deseada
    #'''
    # Posiciones del proyectil y ruido (en este caso es 0 ya que no añadimos ruido a la trayectoria original)
    x_p, y_p, z_p, ruido = simulacion_proyectil(masas, velocidad, angulos, centros_de_gravedad, radios_cuerpos, alturas_cuerpos, parametros_combustible, tiempo_integracion, escala_ruido=0.0)
    # Añadimos la trayectoria a seguir
    trayectoria = [x_p.copy(), y_p.copy(), z_p.copy()]
    # Limitamos a solo valores positivos en z
    j = 0
    for z in z_p:
        if z < 0:
            break
        j += 1
    x_p = x_p[:j-1]
    y_p = y_p[:j-1]
    z_p = z_p[:j-1]

    # '''
    #     Trayectoria con perturbaciones
    # '''
    x_con_pert, y_con_pert, z_con_pert, ruido_aux = simulacion_proyectil(masas, velocidad, angulos, centros_de_gravedad, radios_cuerpos, alturas_cuerpos, parametros_combustible, tiempo_integracion, escala_ruido=0.2, ruido_hist=ruido_hist)
    # Limitamos a solo valores positivos en z
    j = 0
    for z in z_con_pert:
        if z < 0:
            break
        j += 1
    x_con_pert = x_con_pert[:j-1]
    y_con_pert = y_con_pert[:j-1]
    z_con_pert = z_con_pert[:j-1]
    
    # '''
    #     Trayectoria con control
    # '''
    # Posiciones del proyectil con la semilla de los parámetros de control dados
    x_con_control, y_con_control, z_con_control, aux = simulacion_proyectil(masas, velocidad, angulos, centros_de_gravedad, radios_cuerpos, alturas_cuerpos, parametros_combustible, tiempo_integracion, parametros_control, trayectoria=trayectoria, escala_ruido=escala_ruido, ruido_hist=ruido_aux)
    j = 0
    for z in z_con_control:
        if z < 0:
            break
        j += 1
    x_con_control = x_con_control[:j-1]
    y_con_control = y_con_control[:j-1]
    z_con_control = z_con_control[:j-1]

    # Graficamos las tres trayectorias en el mismo gráfico
    st.subheader('Sin ajuste de parámetros de control')
    fig = go.Figure(data=[go.Scatter3d(x=x_p, y=y_p, z=z_p, mode='lines', name='Sin perturbaciones'),
                          go.Scatter3d(x=x_con_pert, y=y_con_pert, z=z_con_pert, mode='lines', name='Con perturbaciones'),
                          go.Scatter3d(x=x_con_control, y=y_con_control, z=z_con_control, mode='lines', name='Con control')])
    st.plotly_chart(fig)

    st.subheader('Con ajuste de parámetros de control')
    # Le pedimos al usuario que seleccione el alpha para el recocido simulado y el rango de generación de números aleatorios
    alpha = st.number_input('Alpha', value=0.9)
    T = st.number_input('Temperatura inicial', value=10000)
    T_min = st.number_input('Temperatura mínima', value=0.01)
    rango_numeros = st.number_input('Rango de generación de números aleatorios (de 0.0 al número elegido)', value=10.0)
    boton = st.button('Iniciar ajuste de parámetros de control')
    if boton:
        with st.spinner('Wait for it...'):
            # Busqueda de los nuevos parametros de control
            indice = min(len(x_p), len(x_con_control))
            error, nuevos_parametros_control, = recocido_simulado(parametros_control, x_con_control[:indice].copy(), y_con_control[:indice].copy(), z_con_control[:indice].copy(), x_p[:indice].copy(), y_p[:indice].copy(), z_p[:indice].copy(), T, T_min, alpha, rango_numeros, indice, masas, velocidad, angulos, centros_de_gravedad, radios_cuerpos, alturas_cuerpos, parametros_combustible, tiempo_integracion, trayectoria, escala_ruido, ruido_hist)
            # Posiciones del proyectil con los nuevos parámetros de control
            x_con_control, y_con_control, z_con_control, aux = simulacion_proyectil(masas, velocidad, angulos, centros_de_gravedad, radios_cuerpos, alturas_cuerpos, parametros_combustible, tiempo_integracion, nuevos_parametros_control, trayectoria=trayectoria, escala_ruido=escala_ruido, ruido_hist=ruido_aux)
            j = 0
            for z in z_con_control:
                if z < 0:
                    break
                j += 1
            x_con_control = x_con_control[:j-1]
            y_con_control = y_con_control[:j-1]
            z_con_control = z_con_control[:j-1]

            # Graficamos las tres trayectorias en el mismo gráfico
            fig = go.Figure(data=[go.Scatter3d(x=x_p, y=y_p, z=z_p, mode='lines', name='Sin perturbaciones'),
                                go.Scatter3d(x=x_con_pert, y=y_con_pert, z=z_con_pert, mode='lines', name='Con perturbaciones'),
                                go.Scatter3d(x=x_con_control, y=y_con_control, z=z_con_control, mode='lines', name='Con control')])
        st.plotly_chart(fig)
except:
    pass
