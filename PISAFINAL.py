import pandas as pd
import pyarrow.parquet as pq
import json
import numpy as np
import seaborn as sns 
import matplotlib.pyplot as plt


#-----------LEYENDO LOS DATOS-------------
parquet_folder = "/Users/marissaluna/Documents/PISA"
parquet_file = ["DataTEC-11-01-to-11-30","DataTEC-01-01-to-01-31"]
file_path = f"{parquet_folder}/{parquet_file[0]}" #Noviembre
file_path2= f"{parquet_folder}/{parquet_file[1]}" #Enero

df = pq.read_table(file_path).to_pandas()
df2 = pq.read_table(file_path2).to_pandas()

print("El data frame o tiene: ",df.shape[0], "observaciones")
print("El data frame o tiene: ",df2.shape[0], "observaciones")

df_total = pd.concat([df, df2], ignore_index=True)

#Para qver que se haya concatenado bien 
df_total.head(5)  
df_total.tail(5)  

print("El data frame o tiene: ",df_total.shape[0], "observaciones")

variables_filtradas = [
    # Energía
    "CONTIFORM_MMA.CONTIFORM_MMA1.EnergyState.0",
    "CONTIFORM_MMA.CONTIFORM_MMA1.EnergyMeasurement_kWh_ElectPower_MainMachine.0",
    "CONTIFORM_MMA.CONTIFORM_MMA1.ElectricalData_UPSPower.0",
    "CONTIFORM_MMA.CONTIFORM_MMA1.ElectricalData_MainMachine.0",

    # Temperatura de la preforma en diferentes capas
    "CONTIFORM_MMA.CONTIFORM_MMA1.PreformTemperatureLayer.1",
    "CONTIFORM_MMA.CONTIFORM_MMA1.PreformTemperatureLayer.3",
    "CONTIFORM_MMA.CONTIFORM_MMA1.PreformTemperatureLayer.5",
    "CONTIFORM_MMA.CONTIFORM_MMA1.PreformTemperatureLayer.7",
    "CONTIFORM_MMA.CONTIFORM_MMA1.PreformTemperatureLayer.9",

    # Otras temperaturas relevantes
    "CONTIFORM_MMA.CONTIFORM_MMA1.CurrentTemperatureRotaryJoint.0",
    "CONTIFORM_MMA.CONTIFORM_MMA1.CurrentPreformNeckFinishTemperature.0",
    "CONTIFORM_MMA.CONTIFORM_MMA1.CurrentTemperatureBrake.1",
    "CONTIFORM_MMA.CONTIFORM_MMA1.CurrentTemperatureBrake.2",
    "CONTIFORM_MMA.CONTIFORM_MMA1.CurrentPreformTemperatureOvenInfeed.0",
    "CONTIFORM_MMA.CONTIFORM_MMA1.ActualTemperatureCoolingCircuit2.0",
    "CONTIFORM_MMA.CONTIFORM_MMA1.CurrentTemperaturePressureDewPoint.0",

    # Enfriamiento y control de aire
    "CONTIFORM_MMA.CONTIFORM_MMA1.CoolingAirTemperatureActualValue.0",
    "CONTIFORM_MMA.CONTIFORM_MMA1.ContollerFactorCoolingCircuit1.0",
    "CONTIFORM_MMA.CONTIFORM_MMA1.AirWizardBasicController.0",
    "CONTIFORM_MMA.CONTIFORM_MMA1.AirWizardPlusController.0",

    # Presión
    "CONTIFORM_MMA.CONTIFORM_MMA1.PressureCompensationChamberPressureActualValue.0",
    "CONTIFORM_MMA.CONTIFORM_MMA1.FinalBlowingPressureActualValue.0",

    # Velocidad
    "CONTIFORM_MMA.CONTIFORM_MMA1.WS_Cur_Mach_Spd.0",
    "CONTIFORM_MMA.CONTIFORM_MMA1.BeltDriveSpeedSetPoint.0",

    # Producción y rechazos
    "CONTIFORM_MMA.CONTIFORM_MMA1.WS_Tot_Rej.0",
    "CONTIFORM_MMA.CONTIFORM_MMA1.WS_Tot_Bottles.0",

    # Otros parámetros operativos
    "CONTIFORM_MMA.CONTIFORM_MMA1.ActualHeightBaseCooling.0",
    "CONTIFORM_MMA.CONTIFORM_MMA1.CurrentProcessType_ConfigValue.0"
]


df_vars = df_total[df_total["variable"].isin(variables_filtradas)].copy()


print("El data frame o tiene: ",df_vars.shape[0], "observaciones")


df_vars.shape[0]/df_total.shape[0]

print ("Es una muestra del",round((df_vars.shape[0]/df_total.shape[0])*100), "% de las observaciones ")

#--------------------RESTANDO HORAS-------------------
# Convertir 'user_ts' a tipo datetime 
df_vars["user_ts"] = pd.to_datetime(df_vars["user_ts"])
# Restar 6 horas
df_vars["user_ts"] = df_vars["user_ts"] - pd.Timedelta(hours=6)
df_vars.head(20)
df_vars.tail(20)



#----------------------HACIENDO DFs--------------------------
# Crear un diccionario para almacenar un DataFrame por cada variable
filtered_dfs = {var.replace(".", "_"): df_vars[df_vars["variable"] == var].copy() for var in variables_filtradas}
# Guardar los DataFrames en variables individuales 
df_names = {}
for var, df_var in filtered_dfs.items():
    globals()[f"df_{var}"] = df_var
    df_names[f"df_{var}"] = df_var

print("DataFrames creados:")
for name in df_names.keys():
    print(name)

#NUMERO DE OBSERVACIONES POR VARIABLE EN DF TOTAL 
df_observaciones = {name: df.shape[0] for name, df in filtered_dfs.items()}
df_observaciones_ordenado = dict(sorted(df_observaciones.items(), key=lambda item: item[1]))
df_observaciones_ordenado

#PORCENTAJE POR VARIABLE EN DF TOTAL 
proporcion_datos = {name: (df.shape[0] / df_total.shape[0])*100 for name, df in filtered_dfs.items()}
df_proporcion_ordenado = dict(sorted(proporcion_datos.items(), key=lambda item: item[1]))
df_proporcion_ordenado

variables_desechables = [ #Eliminamos 8 
    'CONTIFORM_MMA_CONTIFORM_MMA1_CurrentProcessType_ConfigValue_0',
    'CONTIFORM_MMA_CONTIFORM_MMA1_ContollerFactorCoolingCircuit1_0',
    'CONTIFORM_MMA_CONTIFORM_MMA1_BeltDriveSpeedSetPoint_0',
    'CONTIFORM_MMA_CONTIFORM_MMA1_ActualHeightBaseCooling_0',
    'CONTIFORM_MMA_CONTIFORM_MMA1_WS_Cur_Mach_Spd_0',
    'CONTIFORM_MMA_CONTIFORM_MMA1_EnergyState_0',
    'CONTIFORM_MMA_CONTIFORM_MMA1_CoolingAirTemperatureActualValue_0',
    'CONTIFORM_MMA_CONTIFORM_MMA1_WS_Tot_Rej_0'
]

#ELIMINAMOS VARIABLES NO REPRESENTATIVAS < 0.1%
for var in variables_desechables:
    filtered_dfs.pop(var, None)

print("Variables restantes en filtered_dfs:")
for name in filtered_dfs.keys():
    print(name)



# ------------------- CREAR CHUNKS DE LOS DFs ------------------
def chunk_dataframe(df, chunk_size=100000):
    """Divide un DataFrame en chunks más pequeños."""
    num_chunks = len(df) // chunk_size + (1 if len(df) % chunk_size != 0 else 0)
    return [df.iloc[i * chunk_size:(i + 1) * chunk_size] for i in range(num_chunks)]

# Crear chunks para cada DataFrame
chunked_dfs = {name: chunk_dataframe(df_var) for name, df_var in filtered_dfs.items()}

print("Chunks creados por DataFrame:")
for name, chunks in chunked_dfs.items():
    print(f"{name}: {len(chunks)} chunks")


# ------------------- FUNCIONES PARA DETECTAR RELEVANCIA Y RELACIONAR ------------------
def calcular_variabilidad(df, column):
    std_dev = df[column].std()
    iqr = df[column].quantile(0.75) - df[column].quantile(0.25)
    return {"Desviación Estándar": std_dev, "IQR": iqr}

def detectar_outliers(df, column):
    Q1 = df[column].quantile(0.25)
    Q3 = df[column].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    outliers = df[(df[column] < lower_bound) | (df[column] > upper_bound)]
    return len(outliers)


def calcular_proporcion_datos(df, column):
    return df[column].count() / df_total.shape[0]

def descomprimir_message_primer_chunk(chunked_dfs):
    
    for name, chunks in chunked_dfs.items():
        if chunks and "message" in chunks[0].columns:  # Verifica que haya chunks y que 'message' esté en el primero
            chunk = chunks[0]

            # Filtrar solo los valores no nulos en 'message'
            if chunk["message"].notna().any():
                chunk = chunk.copy()  

                # Convertir a JSON si es string
                chunk["message"] = chunk["message"].apply(lambda x: json.loads(x) if isinstance(x, str) else {})

                # Extraer los datos
                columnas_extraidas = set()
                for mensaje in chunk["message"]:
                    if isinstance(mensaje, dict):  
                        columnas_extraidas.update(mensaje.keys())

                # Crear nuevas columnas y llenarlas con los valores del JSON
                for col in columnas_extraidas:
                    chunk[col] = chunk["message"].apply(lambda x: x.get(col, None) if isinstance(x, dict) else None)

                # Eliminar la columna 'message' después de extraer la información
                chunk.drop(columns=["message"], inplace=True)

                # Guardar el chunk actualizado en la estructura original
                chunked_dfs[name][0] = chunk  

    return chunked_dfs

#-------------------USAMOS PRIMER CHUNK PARA VER QUE PEDO, DESCOMPRIMIMOS EN EL PRIMER CHUNK----------------------
chunked_dfs = descomprimir_message_primer_chunk(chunked_dfs)
# Verificar los primeros 5 registros de cada primer chunk en chunked_dfs
for name, chunks in chunked_dfs.items():
    if chunks:  # Verificar que haya al menos un chunk disponible
        print(f"Primer chunk de {name}:")
        display(chunks[0].head(10))  # Mostrar las primeras filas del primer chunk
        print("-" * 50)

#---------------APLICAMOS FUNCIONES A CHUNK DE LAS VARIABLES-----------------
#funci[on de funciones 
def evaluar_todos_los_chunks(chunked_dfs):
    """Aplica funciones de relevancia a todas las columnas de los primeros chunks de cada variable."""
    resultados = {}
    for name, chunks in chunked_dfs.items():
        if chunks:  # Verifica que haya al menos un chunk disponible
            chunk = chunks[0]  # Toma el primer chunk
            resultados[name] = {}
            for column in chunk.columns:
                if chunk[column].dtype in [np.float64, np.int64]:  # Solo analizar variables numéricas
                    var_result = calcular_variabilidad(chunk, column)
                    num_outliers = detectar_outliers(chunk, column)
                    prop_datos = calcular_proporcion_datos(chunk, column)
                    resultados[name][column] = {
                        "Desviación Estándar": var_result["Desviación Estándar"],
                        "IQR": var_result["IQR"],
                        "Número de Outliers": num_outliers,
                        "Proporción de Datos": prop_datos
                    }
    return resultados

resultados_relevancia = evaluar_todos_los_chunks(chunked_dfs)
import pprint
pprint.pprint(resultados_relevancia)

#--------------DESPUÉS DE ANALIZAR LAS MÉTRICAS---------------------

# Lista de variables con baja variabilidad
variables_baja_variabilidad = [
    "CONTIFORM_MMA_CONTIFORM_MMA1_AirWizardBasicController_0", 
    "CONTIFORM_MMA_CONTIFORM_MMA1_AirWizardPlusController_0",
    "CONTIFORM_MMA_CONTIFORM_MMA1_ElectricalData_MainMachine_0.voltageMaxL1",
    "CONTIFORM_MMA_CONTIFORM_MMA1_ElectricalData_UPSPower_0"
]

#GRAFICA TODAS UNA POR UNA
for var in variables_baja_variabilidad:
    for name, chunks in chunked_dfs.items():
        if name == var and chunks:
            chunk = chunks[0]  # Primer chunk
            for column in chunk.columns:
                if column not in ["user_ts", "variable"]: 
                    plt.figure(figsize=(10, 5))
                    if "user_ts" in chunk.columns:
                        plt.plot(chunk["user_ts"], chunk[column], marker='o', linestyle='-', alpha=0.5)
                        plt.xlabel("Tiempo (user_ts)")
                    else:
                        plt.plot(chunk.index, chunk[column], marker='o', linestyle='-', alpha=0.5)
                        plt.xlabel("Índice")
                    plt.title(f"Evolución de {column} en {var} (primer chunk)")
                    plt.ylabel(column)
                    plt.xticks(rotation=45)
                    plt.grid(True)
                    plt.show()

#GRÁFICAS AGRUPADAS 
for var in variables_baja_variabilidad:
    for name, chunks in chunked_dfs.items():
        if name == var and chunks:
            chunk = chunks[0]  # Primer chunk
            plt.figure(figsize=(12, 6))
            for column in chunk.columns:
                if column not in ["user_ts", "variable"]: 
                    if "user_ts" in chunk.columns:
                        plt.plot(chunk["user_ts"], chunk[column], marker='o', linestyle='-', alpha=0.5, label=column)
                    else:
                        plt.plot(chunk.index, chunk[column], marker='o', linestyle='-', alpha=0.5, label=column)
            plt.xlabel("Tiempo (user_ts)" if "user_ts" in chunk.columns else "Índice")
            plt.title(f"Evolución de todas las columnas en {var} (primer chunk)")
            plt.ylabel("Valor")
            plt.xticks(rotation=45)
            plt.grid(True)
            plt.legend()
            plt.show()


#--------------------DF A CSV DE LAS CON LAS QUE VAMOS A TRABAJAR---------------------
'''
variables_para_exportar = [
    "CONTIFORM_MMA.CONTIFORM_MMA1.PreformTemperatureLayer.1",
    "CONTIFORM_MMA.CONTIFORM_MMA1.PreformTemperatureLayer.3",
    "CONTIFORM_MMA.CONTIFORM_MMA1.PreformTemperatureLayer.5",
    "CONTIFORM_MMA.CONTIFORM_MMA1.PreformTemperatureLayer.7",
    "CONTIFORM_MMA.CONTIFORM_MMA1.PreformTemperatureLayer.9",
    "CONTIFORM_MMA.CONTIFORM_MMA1.FinalBlowingPressureActualValue.0",
    "CONTIFORM_MMA.CONTIFORM_MMA1.PressureCompensationChamberPressureActualValue.0"
]

observaciones_por_df = {var: filtered_dfs[var.replace(".", "_")].shape[0] for var in variables_para_exportar if var.replace(".", "_") in filtered_dfs}

# Mostrar el resultado
for var, num_obs in observaciones_por_df.items():
    print(f"{var}: {num_obs} observaciones")

for var in variables_para_exportar:
    var_formateada = var.replace(".", "_")  # Reemplazar puntos por guiones bajos
    if var_formateada in filtered_dfs:  # Verificar si existe en los DataFrames
        file_name = f"{var_formateada}.csv"
        filtered_dfs[var_formateada].to_csv(file_name, index=False)
        print(f"Guardado: {file_name}")

'''
#-------------------------------------------------------------------
#LAS DOS VARIABLES QUE ME TOCA ANALIZAR AMOO AMOO

df_CONTIFORM_MMA_CONTIFORM_MMA1_FinalBlowingPressureActualValue_0.head()
df_CONTIFORM_MMA_CONTIFORM_MMA1_PressureCompensationChamberPressureActualValue_0.head()


df_CONTIFORM_MMA_CONTIFORM_MMA1_FinalBlowingPressureActualValue_0.drop(columns='message')

df_CONTIFORM_MMA_CONTIFORM_MMA1_PressureCompensationChamberPressureActualValue_0.drop(columns='message')

#---------------------AHORA SÍ A ANALIZAR-------------------
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import zscore

#estilo
sns.set_style("whitegrid")


data_pressure_soplado = df_CONTIFORM_MMA_CONTIFORM_MMA1_FinalBlowingPressureActualValue_0.copy()
data_pressure_compensado= df_CONTIFORM_MMA_CONTIFORM_MMA1_PressureCompensationChamberPressureActualValue_0.copy()

#-------------------------------PRESSURE SOPLADO -------------------------
# ---- Análisis Descriptivo Inicial ----
print("Información del dataset:")
print(data_pressure_soplado.info())
print("\nValores nulos:")
print(data_pressure_soplado.isnull().sum())
print("\nValores duplicados:")
print(data_pressure_soplado.duplicated().sum())
#data_pressure_soplado.drop(columns= 'message', inplace=True)
# Resumen estadístico
print("\nResumen estadístico:")
print(data_pressure_soplado.describe(percentiles=[0.25, 0.5, 0.75]))
data_pressure_soplado.shape[0]
data_pressure_soplado.head(20)
data_pressure_compensado.shape[0]

# ---- Distribución y Detección de Outliers ----

col='value'
plt.figure(figsize=(5, 5))
plt.figure()
sns.histplot(data_pressure_soplado[col], kde=True, bins=20)
plt.title(f"Distribución de Presión de Soplado Final")
plt.show()
    
plt.figure()
sns.boxplot(y=data_pressure_soplado[col])
plt.title(f"Boxplot de Presión de Soplado Final")
plt.show()
print(col)

# IQR  para detectar outliers

Q1 = data_pressure_soplado[col].quantile(0.25)
Q3 = data_pressure_soplado[col].quantile(0.75)
IQR = Q3 - Q1
outliers = data_pressure_soplado[(data_pressure_soplado[col] < (Q1 - 1.5 * IQR)) | (data_pressure_soplado[col] > (Q3 + 1.5 * IQR))]
print(f"Valores atípicos detectados en {col} por IQR:")
print(outliers[[col]])
print(col)

# ----  Análisis Temporal y Tendencias ----
data_pressure_soplado["user_ts"] = pd.to_datetime(data_pressure_soplado["user_ts"])
data_pressure_soplado = data_pressure_soplado.sort_values(by="user_ts")
plt.figure(figsize=(10, 4))
plt.plot(data_pressure_soplado["user_ts"], data_pressure_soplado[col], label=col)
plt.title(f"Serie de tiempo de {col}")
plt.legend()
plt.show()
    

plt.figure(figsize=(10, 4))
plt.plot(data_pressure_soplado["user_ts"], data_pressure_soplado[col].rolling(window=30).mean(), label="Rolling Mean")
plt.plot(data_pressure_soplado["user_ts"], data_pressure_soplado[col].rolling(window=30).std(), label="Rolling Std")
plt.title(f"Rolling Mean & Std de {col} FinalBlowingPressureActualValue ")
plt.legend()
plt.show()


#-------------------------PRESSURE COMPENSADO--------------------
# ---- 1.1. Análisis Descriptivo Inicial ----
print("Información del dataset:")
print(data_pressure_compensado.info())
print("\nValores nulos:")
print(data_pressure_compensado.isnull().sum())
print("\nValores duplicados:")
print(data_pressure_compensado.duplicated().sum())
#data_pressure_soplado.drop(columns= 'message', inplace=True)
# Resumen estadístico
print("\nResumen estadístico:")
print(data_pressure_compensado.describe(percentiles=[0.25, 0.5, 0.75]))

# ---- Análisis de Distribución y Detección de Outliers ----

col='value'
plt.figure(figsize=(5, 5))
plt.figure()
sns.histplot(data_pressure_compensado[col], kde=True, bins=10)
plt.title(f"Distribución de Presión de la cámara de compensación:")
plt.show()
    
plt.figure()
sns.boxplot(y=data_pressure_compensado[col])
plt.title(f"Boxplot de Presión de la cámara de compensación:")
plt.show()
print(col)

# IQR  para detectar outliers
Q1 = data_pressure_compensado[col].quantile(0.25)
Q3 = data_pressure_compensado[col].quantile(0.75)
IQR = Q3 - Q1
outliers = data_pressure_compensado[(data_pressure_compensado[col] < (Q1 - 1.5 * IQR)) | (data_pressure_soplado[col] > (Q3 + 1.5 * IQR))]
print(f"Valores atípicos detectados en {col} por IQR:")
print(outliers[[col]])
print(col)

# ---- Análisis Temporal y Tendencias ----
data_pressure_compensado["user_ts"] = pd.to_datetime(data_pressure_compensado["user_ts"])
data_pressure_compensado = data_pressure_compensado.sort_values(by="user_ts")
plt.figure(figsize=(10, 4))
plt.plot(data_pressure_compensado["user_ts"], data_pressure_compensado[col], label=col)
plt.title(f"Serie de tiempo de {col}")
plt.legend()
plt.show()
    

plt.figure(figsize=(10, 4))
plt.plot(data_pressure_compensado["user_ts"], data_pressure_compensado[col].rolling(window=30).mean(), label="Rolling Mean")
plt.plot(data_pressure_compensado["user_ts"], data_pressure_compensado[col].rolling(window=30).std(), label="Rolling Std")
plt.title(f"Rolling Mean & Std de {col} FinalBlowingPressureActualValue ")
plt.legend()
plt.show()







import matplotlib.pyplot as plt
#SERIES DE TIEMPO FILTRADAS 
#PRESSURE CHAMBER 
# Convertir a datetime si aún no lo está
data_pressure_compensado["user_ts"] = pd.to_datetime(data_pressure_compensado["user_ts"])
# Filtrar entre el 1 de noviembre y el 2 de enero
fecha_inicio = "2024-11-15"
fecha_fin = "2025-12-01"
data_filtrada = data_pressure_compensado[(data_pressure_compensado["user_ts"] >= fecha_inicio) & 
                                         (data_pressure_compensado["user_ts"] <= fecha_fin)]
# Ordenar por tiempo
data_filtrada = data_filtrada.sort_values(by="user_ts")

plt.figure(figsize=(10, 4))
plt.plot(data_filtrada["user_ts"], data_filtrada[col], label=col)
plt.xlabel("Fecha")
plt.ylabel("Valor de la Presión")
plt.title(f"Serie de tiempo de Presión de la cámara de compensación (15 Nov - 2 Ene)")
plt.xticks(rotation=45)
plt.legend()
plt.grid(True)
plt.show()



#PRESSURE SOPLADO 
data_pressure_soplado["user_ts"] = pd.to_datetime(data_pressure_soplado["user_ts"])
fecha_inicio = "2024-11-15"
fecha_fin = "2025-12-01"
data_filtrada = data_pressure_soplado[(data_pressure_soplado["user_ts"] >= fecha_inicio) & 
                                         (data_pressure_soplado["user_ts"] <= fecha_fin)]

data_filtrada = data_filtrada.sort_values(by="user_ts")

plt.figure(figsize=(10, 4))
plt.plot(data_filtrada["user_ts"], data_filtrada[col], label=col)
plt.xlabel("Fecha")
plt.ylabel("Valor de la Presión")
plt.title(f"Serie de tiempo de Presión de Soplado (11 Nov - 2 Ene)")
plt.xticks(rotation=45)
plt.legend()
plt.grid(True)
plt.show()



#------------HIPOTESIS TEMP VS BOT----------

'''
df_CONTIFORM_MMA_CONTIFORM_MMA1_PreformTemperatureLayer_1
df_CONTIFORM_MMA_CONTIFORM_MMA1_PreformTemperatureLayer_3
df_CONTIFORM_MMA_CONTIFORM_MMA1_PreformTemperatureLayer_5
df_CONTIFORM_MMA_CONTIFORM_MMA1_PreformTemperatureLayer_7
df_CONTIFORM_MMA_CONTIFORM_MMA1_PreformTemperatureLayer_9
df_CONTIFORM_MMA_CONTIFORM_MMA1_WS_Tot_Rej_0
'''


#Intento de ver si las botellas por día incrementaron 
import matplotlib.pyplot as plt
import pandas as pd

# Diccionario con los DataFrames y nombres de variables
dfs_a_graficar = {
    "Preform Temp Layer 1": df_CONTIFORM_MMA_CONTIFORM_MMA1_PreformTemperatureLayer_1,
    "Preform Temp Layer 3": df_CONTIFORM_MMA_CONTIFORM_MMA1_PreformTemperatureLayer_3,
    "Preform Temp Layer 5": df_CONTIFORM_MMA_CONTIFORM_MMA1_PreformTemperatureLayer_5,
    "Preform Temp Layer 7": df_CONTIFORM_MMA_CONTIFORM_MMA1_PreformTemperatureLayer_7,
    "Preform Temp Layer 9": df_CONTIFORM_MMA_CONTIFORM_MMA1_PreformTemperatureLayer_9
}



# Crear una figura para graficar todas las variables en el mismo gráfico
plt.figure(figsize=(12, 6))

# Intervalo de fechas 
fecha_inicio = pd.to_datetime("2024-11-15").tz_localize(None)
fecha_fin = pd.to_datetime("2025-12-01").tz_localize(None)

# Iterar sobre cada DataFrame y graficarlo en la misma figura
for nombre, df in dfs_a_graficar.items():
    df = df.copy()  
    df["user_ts"] = pd.to_datetime(df["user_ts"], errors="coerce")
    df["user_ts"] = df["user_ts"].dt.tz_localize(None)
    df_filtrado = df[(df["user_ts"] >= fecha_inicio) & (df["user_ts"] <= fecha_fin)].sort_values(by="user_ts")

    if not df_filtrado.empty:
        plt.plot(df_filtrado["user_ts"], df_filtrado["value"], label=nombre, alpha=0.7)


plt.xlabel("Fecha")
plt.ylabel("Valor")
plt.title("Serie de Tiempo de Temperaturas de Preforma y Total Rechazos (1 Nov - 2 Ene)")
plt.xticks(rotation=45)
plt.legend()
plt.grid(True)
plt.show()

