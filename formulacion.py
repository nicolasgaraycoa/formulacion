import os
import pandas as pd
import numpy as np
import streamlit as st
import streamlit_authenticator as stauth
import scipy
from scipy.optimize import linprog

st.set_page_config(page_title="Formulacion", layout="wide")

st.title('Matriz de formulacion')

with st.sidebar:
    mp = st.file_uploader("Choose a file")
    if mp is not None:
        materia_prima = pd.read_csv(mp)



requerimientos = pd.DataFrame(
    {'parametro': ['grado_min', 'grado_max', 'acidez', 'esteres', 'aldehidos', 'alcoholes_superiores',
                   'metanol', 'furfural'],
    'R1': [74, 76, 15, 15, 1, 15, 10, 10],
    'R2': [74, 76, 20, 20, 1, 20, 10, 10],
    'R3': [74, 76, 25, 25, 1, 22.5, 10, 10],
    'R4': [74, 76, 30, 30, 1, 27.5, 10, 10],
    'R5': [74, 76, 35, 35, 1, 30.0, 10, 10],
    'R6': [74, 76, 40, 40, 1, 35.0, 10, 10],
    'R7': [74, 76, 45, 45, 1, 40.0, 10, 10],
    'R8': [69, 71, 47, 47, 1, 42.5, 10, 10],
    'R9': [69, 71, 50, 50, 1, 45.0, 10, 10],
    'R10': [69, 71, 52.5, 52.5, 1, 47.5, 10, 10],
    'R11': [69, 71, 56.2, 56.2, 1, 48.7, 10, 10],
    'R12': [69, 71, 60.0, 60.0, 1, 50.0, 10, 10]}
)

requerimientos = requerimientos.swapaxes("index", "columns")
requerimientos.columns = requerimientos.iloc[0]
requerimientos = requerimientos.iloc[1:]
requerimientos.reset_index(inplace=True)
requerimientos = requerimientos.rename(columns = {'index':'edad'})
requerimientos = requerimientos.rename_axis(None, axis=1)


costos = pd.DataFrame({
    'mp' : list(materia_prima.columns[1:]),
    'costo': [1.08, 1.06, 4.35, 0.001]
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

