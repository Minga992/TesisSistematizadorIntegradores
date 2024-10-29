import argparse
import pandas as pd
import numpy as np
from scipy.interpolate import interp1d
from sklearn.metrics import mean_squared_error
from PMLGraphics import (
    QualityExperimentInformation,
    PMLGraphics,
)


description = """
Tabla hecha con Pandas, para poder manipular salida de Geant4.

Cada corrida con el experimentRunner.py deja un archivo relevantStats.csv . Si se corren
varios steppers diferentes se puede querer tener una tabla comparativa de todos ellos, y este programa
viene a satisfacer esa necesidad.

Se le deben pasar un csv de referencia, el nombre del example que representa, el nombre del sub example,
y el nombre del stepper utilizado. Por otro lado, se debe pasar una lista de csvs que se contrastaran
con el de referencia, una lista con los nombres de los examples de estos, una lista con los nombres de
los subexamples, y una lista de los nombres de los steppers.

e.g.
    python3 ExperimentCriticalInformation.py --tabNam tabla1 --physics FTFP_BERT --csvRef DopriB2A.csv --csvsCom QSSB2A.csv RK4B2A.csv --exNameRef B2 --subExNameRef A --stepperNameRef DopriT --exNamesCom B2 B2 --subExNamesCom A A --stepperNamesCom QSS2 RK4 --outputFormat EXCEL

"""

# Función para calcular el índice de desempeño M
def calcularIndiceDesempeno(time, error):
    if time * error == 0:
        return 'inf'
    return 1 / (time * error)

def calcularMaxErrorAbsoluto(valoresComun, valoresReferencia):
    errores = [abs(x - ref) for x, ref in zip(valoresComun, valoresReferencia)]
    maxError = max(errores)
    return maxError

parser = argparse.ArgumentParser(
    description=description, formatter_class=argparse.RawTextHelpFormatter
)

parser.set_defaults(parseOnly=False)

parser.add_argument(
    "-tn",
    "--tabNam",
    dest="tabNam",
    help="Table Name",
    required=True,
)

parser.add_argument(
    "-of",
    "--outputFormat",
    dest="outputFormat",
    help="Format of output. Could be EXCEL or none",
    required=True,
)

parser.add_argument(
    "-ph",
    "--physics",
    dest="physics",
    help="Physics",
    required=True,
)

parser.add_argument(
    "-cr",
    "--csvRef",
    dest="csvRef",
    help="Reference CSV",
    required=True,
)

parser.add_argument(
    "-pr",
    "--pmlRef",
    dest="pmlRef",
    help="Reference PML",
    required=False,
)

parser.add_argument(
    "-npr",
    "--namePmlRef",
    dest="namePmlRef",
    help="Name of Reference PML",
    required=False,
)

parser.add_argument(
    "-er",
    "--exNameRef",
    dest="exNameRef",
    help="Example Name Ref",
    required=True,
)

parser.add_argument(
    "-sr",
    "--subExNameRef",
    dest="subExNameRef",
    help="SubExample Name Ref",
    required=True,
)

parser.add_argument(
    "-str",
    "--stepperNameRef",
    dest="stepperNameRef",
    help="stepper Name Ref",
    required=True,
)

parser.add_argument(
    "-cc",
    "--csvsCom",
    nargs='*',
    dest="csvsCom",
    help="Commons CSVs",
    required=True,
)

parser.add_argument(
    "-pc",
    "--pmlsCom",
    nargs='*',
    dest="pmlsCom",
    help="pmls Common",
    required=False,
)
parser.add_argument(
    "-npc",
    "--namesPmlsCom",
    nargs='*',
    dest="namesPmlsCom",
    help="Names of pmls Common",
    required=False,
)

parser.add_argument(
    "-ec",
    "--exNamesCom",
    nargs='*',
    dest="exNamesCom",
    help="Example Name Common",
    required=False,
)

parser.add_argument(
    "-sc",
    "--subExNamesCom",
    nargs='*',
    dest="subExNamesCom",
    help="SubExample Name Com",
    required=False,
)

parser.add_argument(
    "-stc",
    "--stepperNamesCom",
    nargs='*',
    dest="stepperNamesCom",
    help="stepper Name Com",
    required=False,
)

args = parser.parse_args()

# Config
# general
tabNam = args.tabNam
outputFormat = args.outputFormat
physics = args.physics

# ref Info
csvRef = args.csvRef
pmlRef = args.pmlRef
namePmlRef = args.namePmlRef
exNameRef = args.exNameRef
subExNameRef = args.subExNameRef
stepperNameRef = args.stepperNameRef

# Commono Info
pmlsCom = args.pmlsCom or []
namesPmlsCom = args.namesPmlsCom or []
csvsCom = args.csvsCom or []
exNamesCom = args.exNamesCom or []
subExNamesCom = args.subExNamesCom or []
stepperNamesCom = args.stepperNamesCom or []

# Verificar que la cantidad de elementos sea igual en todas las listas
if len(csvsCom) != len(exNamesCom) or len(csvsCom) != len(subExNamesCom) or len(csvsCom) != len(stepperNamesCom):
    raise ValueError("La cantidad de elementos en csvsCom, exNamesCom, subExNamesCom y stepperNamesCom debe ser la misma.")

if len(pmlsCom) != len(namesPmlsCom):
    raise ValueError("La cantidad de pmlsCom no councide con la cantidad de namesPmlsCom")

"""Correr experimento"""

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)

# Leer el CSV de referencia
df_referencia = pd.read_csv(csvRef)

# Leer los CSV comunes si se proporcionan
dfs_comunes = [pd.read_csv(csv_comun) for csv_comun in csvsCom] if csvsCom else []

#Validacion sobre los PMLs

flagMustPutMSEs = True
if pmlRef is None:
    flagMustPutMSEs = False
else:
    total_filas_common = sum(len(pd.read_csv(csv)) for csv in csvsCom)
    total_filas_ref = len(df_referencia)
    total_filas = total_filas_ref + total_filas_common

    total_pmls_ref = 1 #is not a list, only one can come
    total_pmls_common = len(pmlsCom)
    total_pmls = total_pmls_ref + total_pmls_common

    if total_filas != total_pmls:
        mensaje = f"La cantidad de PMLs aportados({total_pmls}) no es igual a la cantidad de filas de todos los csv({total_filas})."
        raise ValueError(mensaje)

arrayOfMSEsX = [0]
arrayOfMSEsY = [0]
arrayOfMSEsZ = [0]
arrayOfMSEsTrackLength = [0]
arrayOfQualityExperimentInformationRef = []
arrayOfQualityExperimentInformationCommon = []
arrayOfMaxErrorsX = ['NA']
arrayOfMaxErrorsY = ['NA']
arrayOfMaxErrorsZ = ['NA']

if flagMustPutMSEs:
    dataPmlRef = np.loadtxt(pmlRef, skiprows=1)
    posx1, posy1, posz1, t1, trackLength1 = dataPmlRef[:, 0], dataPmlRef[:, 1], dataPmlRef[:, 2], dataPmlRef[:, 3], dataPmlRef[:, 4]

    for i, pmlCommon in enumerate(pmlsCom):
        dataPmlCom = np.loadtxt(pmlCommon, skiprows=1)

        # extraer posiciones y tiempos de ambos conjuntos de datos
        posx2, posy2, posz2, t2, trackLength2 = dataPmlCom[:, 0], dataPmlCom[:, 1], dataPmlCom[:, 2], dataPmlCom[:, 3], dataPmlCom[:, 4]

        # determinar un conjunto de tiempos comunes en el que se realizará la interpolación
        t_common = np.union1d(t1, t2)

        # interpolar las posiciones de ambos programas en el conjunto de tiempos comunes
        posx1_interp = interp1d(t1, posx1, fill_value="extrapolate")(t_common)
        posx2_interp = interp1d(t2, posx2, fill_value="extrapolate")(t_common)

        posy1_interp = interp1d(t1, posy1, fill_value="extrapolate")(t_common)
        posy2_interp = interp1d(t2, posy2, fill_value="extrapolate")(t_common)

        posz1_interp = interp1d(t1, posz1, fill_value="extrapolate")(t_common)
        posz2_interp = interp1d(t2, posz2, fill_value="extrapolate")(t_common)

        trackLength1_interp = interp1d(t1, trackLength1, fill_value="extrapolate")(t_common)
        trackLength2_interp = interp1d(t2, trackLength2, fill_value="extrapolate")(t_common)

        qualityExperimentInformationRef = QualityExperimentInformation(expName = stepperNameRef, posX= posx1, posY=posy1, posZ=posz1, time=t1, trackLength=trackLength1, posXInterpolated=posx1_interp, posYInterpolated=posy1_interp, posZInterpolated=posz1_interp, commonTime=t_common, trackLengthInterpolated=trackLength1_interp)
        qualityExperimentInformationCommon = QualityExperimentInformation(expName = namesPmlsCom[i], posX= posx2, posY=posy2, posZ=posz2, time=t2, trackLength=trackLength2, posXInterpolated=posx2_interp, posYInterpolated=posy2_interp, posZInterpolated=posz2_interp, commonTime=t_common, trackLengthInterpolated=trackLength2_interp)

        arrayOfQualityExperimentInformationRef.append(qualityExperimentInformationRef)
        arrayOfQualityExperimentInformationCommon.append(qualityExperimentInformationCommon)
        # calcular el MSE entre las posiciones interpoladas de ambos programas
        msex = mean_squared_error(posx1_interp, posx2_interp)
        msey = mean_squared_error(posy1_interp, posy2_interp)
        msez = mean_squared_error(posz1_interp, posz2_interp)
        msetrackLength = mean_squared_error(trackLength1_interp, trackLength2_interp)

        maxErrorX = calcularMaxErrorAbsoluto(posx1_interp, posx2_interp)
        maxErrorY = calcularMaxErrorAbsoluto(posy1_interp, posy2_interp)
        maxErrorZ = calcularMaxErrorAbsoluto(posz1_interp, posz2_interp)

        arrayOfMSEsX.append(msex)
        arrayOfMSEsY.append(msey)
        arrayOfMSEsZ.append(msez)
        arrayOfMSEsTrackLength.append(msetrackLength)
        arrayOfMaxErrorsX.append(maxErrorX)
        arrayOfMaxErrorsY.append(maxErrorY)
        arrayOfMaxErrorsZ.append(maxErrorZ)

# Modificaciones al CSV de referencia
df_referencia['Example'] = exNameRef
df_referencia['subExample'] = subExNameRef
df_referencia['Obs'] = stepperNameRef
df_referencia['physics'] = physics
df_referencia.rename(columns={
    "Profit User Time vs Dopri": "SpeedUp User Time vs "+stepperNameRef,
    "Profit Real Time vs Dopri": "SpeedUp Real Time vs "+stepperNameRef,
    "Profit System Time vs Dopri": "SpeedUp System Time vs "+stepperNameRef,
    "Obs": "Stepper Name"
}, inplace=True)
df_referencia.drop("Macro Name", axis=1, inplace=True)
df_referencia.drop("Experiment Folder", axis=1, inplace=True)


# Modificaciones para cada CSV común
for i, df_comun in enumerate(dfs_comunes):
    df_comun['Profit User Time vs Dopri'] = 1 - (df_comun['User Time(seg)'] / df_referencia.at[0, 'User Time(seg)'])
    df_comun['Profit Real Time vs Dopri'] = 1 - (df_comun['Real Time(seg)'] / df_referencia.at[0, 'Real Time(seg)'])
    df_comun['Profit System Time vs Dopri'] = 1 - (df_comun['System Time(seg)'] / df_referencia.at[0, 'System Time(seg)'])
    df_comun['Example'] = exNamesCom[i]
    df_comun['subExample'] = subExNamesCom[i]
    df_comun['Obs'] = stepperNamesCom[i]
    df_comun['physics'] = physics
    df_comun.rename(columns={
        "Profit User Time vs Dopri": "SpeedUp User Time vs "+stepperNameRef,
        "Profit Real Time vs Dopri": "SpeedUp Real Time vs "+stepperNameRef,
        "Profit System Time vs Dopri": "SpeedUp System Time vs "+stepperNameRef,
        "Obs": "Stepper Name"
    }, inplace=True)
    df_comun.drop("Macro Name", axis=1, inplace=True)
    df_comun.drop("Experiment Folder", axis=1, inplace=True)

for i in range(len(arrayOfQualityExperimentInformationRef)):
    dirNameForQuality = arrayOfQualityExperimentInformationCommon[i].expName + 'VS' + arrayOfQualityExperimentInformationRef[i].expName
    PMLGraphics(outputDir = dirNameForQuality, qualityExperimentInformation1 = arrayOfQualityExperimentInformationCommon[i], qualityExperimentInformation2 = arrayOfQualityExperimentInformationRef[i]).plot()

# Combina el DataFrame de referencia con los DataFrames comunes
df_combined = pd.concat([df_referencia] + dfs_comunes, sort=False)

# De ser requerido se agregan los MSEs
if flagMustPutMSEs:
    df_combined.insert(len(df_combined.columns), 'MSE x', arrayOfMSEsX)
    df_combined.insert(len(df_combined.columns), 'MSE y', arrayOfMSEsY)
    df_combined.insert(len(df_combined.columns), 'MSE z', arrayOfMSEsZ)
    df_combined.insert(len(df_combined.columns), 'MSE trackLength', arrayOfMSEsTrackLength)
    df_combined = df_combined.reset_index(drop=True)
    df_combined['Indice de desempeño M en X'] = ['NA'] + [calcularIndiceDesempeno(df_combined['Real Time(seg)'][i], arrayOfMaxErrorsX[i]) for i in range(1, len(df_combined))]
    df_combined['Indice de desempeño M en Y'] = ['NA'] + [calcularIndiceDesempeno(df_combined['Real Time(seg)'][i], arrayOfMaxErrorsY[i]) for i in range(1, len(df_combined))]
    df_combined['Indice de desempeño M en Z'] = ['NA'] + [calcularIndiceDesempeno(df_combined['Real Time(seg)'][i], arrayOfMaxErrorsZ[i]) for i in range(1, len(df_combined))]
    df_combined['Indice de desempeño MSE en X'] = ['NA'] + [calcularIndiceDesempeno(df_combined['Real Time(seg)'][i], arrayOfMSEsX[i]) for i in range(1, len(df_combined))]
    df_combined['Indice de desempeño MSE en Y'] = ['NA'] + [calcularIndiceDesempeno(df_combined['Real Time(seg)'][i], arrayOfMSEsY[i]) for i in range(1, len(df_combined))]
    df_combined['Indice de desempeño MSE en Z'] = ['NA'] + [calcularIndiceDesempeno(df_combined['Real Time(seg)'][i], arrayOfMSEsZ[i]) for i in range(1, len(df_combined))]

# Muestra Tabla
if outputFormat == "EXCEL":
    df_combined.to_excel(tabNam + '.xlsx', engine='openpyxl', index=False)
else:
    print(df_combined)



# Aplica el formato de color a la columna 'Profit User Time vs Dopri'
#styled_df = df_combined.style.applymap(color_negative_red, subset=['Profit User Time vs Dopri'])

# Muestra la tabla con el formato de color
#styled_df.to_excel('styled_table.xlsx', engine='openpyxl', index=False)

