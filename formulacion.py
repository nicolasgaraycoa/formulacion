import os
import pandas as pd
import numpy as np
import pandas_datareader as pdr
import streamlit as st
import streamlit_authenticator as stauth
import yaml 
from yaml.loader import SafeLoader
import scipy
from scipy.optimize import linprog
from st_aggrid import AgGrid

st.set_page_config(page_title="Formulacion", layout="wide")

st.title('Matriz de formulacion')

with st.sidebar:
    mp = st.file_uploader("Choose a file")
    if mp is not None:
        materia_prima = pd.read_csv(mp)



requerimientos = pd.DataFrame(
    {'parametro': ['grado_min', 'grado_max', 'acidez', 'esteres', 'aldehidos', 'alcoholes_superiores',
                   'metanol', 'furfural'],
    'R1': [65, 67, 150, 100, 150, 150, 100, 10],
    'R2': [65, 67, 200, 100, 200, 200, 100, 10],
    'R3': [65, 67, 250, 100, 250, 225, 100, 10],
    'R4': [65, 67, 300, 100, 300, 275, 100, 10],
    'R5': [65, 67, 350, 100, 350, 300, 100, 10],
    'R6': [65, 67, 400, 100, 400, 350, 100, 10],
    'R7': [65, 67, 450, 100, 450, 400, 100, 10],
    'R8': [60, 60, 475, 100, 475, 425, 100, 10],
    'R9': [60, 60, 500, 100, 500, 450, 100, 10],
    'R10': [60, 60, 525, 100, 525, 475, 100, 10],
    'R11': [60, 60, 562, 100, 562, 487, 100, 10],
    'R12': [60, 60, 600, 100, 600, 500, 100, 10]}
)

requerimientos = requerimientos.swapaxes("index", "columns")
requerimientos.columns = requerimientos.iloc[0]
requerimientos = requerimientos.iloc[1:]
requerimientos.reset_index(inplace=True)
requerimientos = requerimientos.rename(columns = {'index':'edad'})
requerimientos = requerimientos.rename_axis(None, axis=1)


costos = pd.DataFrame({
    'mp' : list(materia_prima.columns[1:]),
    'costo': [1.08, 1.06, 4.35, 0.01]
})


condiciones = pd.DataFrame({
    'parametro': list(requerimientos.columns[1:]),
    'mm': [1,0,1,1,0,1,0,0]})


obj = list(costos['costo'])

lhs_ineq = []
for i in range(len(materia_prima)):
    if i == 0:
        lhs_ineq.append([item * -1 for item in list(materia_prima.iloc[i][1:])])
        lhs_ineq.append(list(materia_prima.iloc[i][1:]))
    elif int(condiciones.iloc[i+1,1:])==1:
        lhs_ineq.append([item * -1 for item in list(materia_prima.iloc[i][1:])])
    else:
        lhs_ineq.append(list(materia_prima.iloc[i][1:]))

lhs_eq = [[1,1,1,1]]  
rhs_eq = [1] 
bnd = [(0, float("inf")), (0, float("inf")), 
       (0, float("inf")), (0, float("inf"))]


solucion = []
for j in range(len(requerimientos)):
    rhs_ineq =list(requerimientos.iloc[j][1:])
    for i in range(len(rhs_ineq)):
        if int(condiciones.iloc[i,1:])==1:
            rhs_ineq[i] = rhs_ineq[i]*-1
        else:
            rhs_ineq[i] = rhs_ineq[i]
    opt = linprog(c=obj, A_ub=lhs_ineq, b_ub=rhs_ineq,
                  A_eq=lhs_eq, b_eq=rhs_eq, bounds=bnd)
    if opt.x is None:
        solucion.append([None, None, None, None])
    else:
        solucion.append(opt.x)

solucion = pd.DataFrame(solucion, columns = list(materia_prima.columns[1:]))

recomendaciones = pd.DataFrame(['R'+str(i) for i in range(1,31,1)], columns=['edad'])
recomendaciones = pd.concat([recomendaciones, solucion], axis=1)


st.dataframe(recomendaciones, hide_index=True)



