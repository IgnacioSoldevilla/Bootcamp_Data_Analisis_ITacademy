# %% [markdown]
# # 00.- Cargar fichero

# %%
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
import seaborn as sns
from scipy.stats import gaussian_kde
from datetime import datetime
import streamlit as st


st.set_page_config(
    page_title="Consulta temporalidad",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)



st.title("TEMPORALIDAD: RENDIMIENTO MEDIO ACUMULADO")


# %% [markdown]
# # 08.- Visualizar media beneficio acumulado

# %%
# Visualizo esta media en un plotly interactivo

def visualiza_beneficio_acum_medio(df:pd.DataFrame, name:str):
    """Genera un gráfico interactivo con Plotly que muestra el rendimiento medio acumulado
    histórico diario de una acción, calculado a partir del conjunto de entrenamiento
    (por ejemplo, 2000–2023). Para representar correctamente todos los días del año,
    incluido el 29 de febrero, se utiliza un eje temporal ficticio basado en un año
    bisiesto (año 2000).

    El gráfico incluye:
    - La curva del rendimiento medio acumulado diario expresado en porcentaje.
    - Un eje X con meses abreviados en español.
    - Un cuadro emergente (hover) que muestra fecha (día-mes) y rendimiento medio.
    - Una línea vertical roja que marca el día actual dentro del calendario.
    - Un estilo visual limpio basado en la plantilla “plotly_white”.

    Args:
        df (pd.DataFrame): DataFrame con al menos las columnas:
            - 'md': día del año en formato MM-DD.
            - 'rendimiento_medio': rendimiento medio acumulado (valor decimal).
        name (str): Nombre de la acción para mostrar en el título del gráfico.
    """
    # === Preparar datos ===
    df_plot = df.reset_index()[["md", "rendimiento_medio"]] #nuevo DF con nuevo indice y solo las columnas md y rendimiento_medio
    df_plot["fecha"] = pd.to_datetime("2000-" + df_plot["md"], format="%Y-%m-%d") # creo columna fecha real para el eje x con un año cualquiera bisiesto
    df_plot = df_plot.sort_values("fecha") # Ordena la fecha cronologicamente
    df_plot["rendimiento_medio_pct"] = df_plot["rendimiento_medio"] * 100  # convierte la media en %

    # === Crear figura ===
    fig = px.line(
        df_plot,
        x="fecha",
        y="rendimiento_medio_pct",
        title=f"{name}. Rendimiento medio acumulado histórico diario (2000 al 2023)",
        )
    
    fig.update_layout(
    title=dict(
        font=dict(size=30, color="black"),
        x=0
    )
)

    # === Ticks de meses en español para el eje X ===
    meses = pd.date_range("2000-01-01", "2000-12-01", freq="MS")
    fig.update_xaxes(
        tickmode="array",
        tickvals=meses,
        ticktext=["Ene","Feb","Mar","Abr","May","Jun",
                "Jul","Ago","Sep","Oct","Nov","Dic"]
    )

    # === Hover o cuandro emergente al pasar el ratón sin año ===
    fig.update_traces(
        hovertemplate="Fecha: %{x|%d-%m}<br>Rendimiento medio: %{y:.2f}%<extra></extra>",  # br es un salto de linea
        line=dict(color="black", width=2)
    )

    # === Día actual ===
    hoy = datetime.now()
    md_actual = hoy.strftime("%m-%d")
    fecha_actual = pd.to_datetime("2000-" + md_actual)

    # === Línea vertical roja corta (shape) ===
    fig.add_shape(
        type="line",
        x0=fecha_actual,
        x1=fecha_actual,
        y0=df_plot["rendimiento_medio_pct"].min(),     # parte baja
        y1=df_plot["rendimiento_medio_pct"].max(),  # más corta
        line=dict(color="red", width=2)
    )

    # === Etiqueta "Hoy" justo encima de la línea ===
    fig.add_annotation(
        x=fecha_actual,
        y=df_plot["rendimiento_medio_pct"].max() * 1.05,
        text="Hoy",
        showarrow=False,
        font=dict(color="red", size=14)
    )

    # === Estilo general ===
    fig.update_layout(
        xaxis_title="Mes",
        yaxis_title="Rendimiento medio (%)",
        template="plotly_white",
        showlegend=False
    )

    # fig.show();
    # st.plotly_chart(fig, use_container_width=True)
    st.plotly_chart(fig, width="stretch")




# %% [markdown]
# # 09.- Pedir y validar fechas de operación

# %%
# === Función para pedir ===
def pedir_fecha(mensaje:str)->datetime:
    """Solicita al usuario una fecha en formato 'dd-mm' y la convierte en un objeto
    datetime utilizando un año fijo (2000), que permite incluir correctamente el
    29 de febrero en caso de ser necesario. Si el usuario introduce un formato
    incorrecto, se muestra un mensaje de advertencia.

    La función está pensada para introducir días del año sin importar el año real,
    por lo que se antepone '2000-' a la fecha introducida antes de convertirla.

    Args:
        mensaje (str): Texto que se mostrará al usuario al solicitar la fecha.

    Returns:
        datetime | None: Objeto datetime correspondiente al día y mes introducidos.
                        Devuelve None si la fecha no tiene el formato válido 'dd-mm'.
    """
    
    texto = st.text_input(mensaje, value="01-01")

    try:
        fecha = datetime.strptime("2000-" + texto, "%Y-%d-%m")
        return fecha
    except ValueError:
        st.write("⚠️ Fecha inválida. Usa el formato dd-mm (por ejemplo 20-02).")

# %% [markdown]
# # 10.- Validar fechas de operación

# %%

# === Función para pedir y validar una fecha ===
def pedir_validar_fecha()->tuple:
    """Solicita al usuario dos fechas en formato 'dd-mm', las convierte en objetos datetime
    usando un año fijo (2000) y valida que el intervalo esté en el orden correcto.
    Si la fecha final introducida es anterior a la inicial, las intercambia y avisa
    al usuario del ajuste.

    Las fechas se devuelven finalmente como cadenas en formato 'YYYY-MM-DD', manteniendo
    el año ficticio 2000, lo que permite trabajar con rangos de días del año sin
    depender del año real.

    Returns:
        tuple: f_inicio_str (str): Fecha inicial en formato 'YYYY-MM-DD'.
                f_fin_str (str): Fecha final en formato 'YYYY-MM-DD'.
                Si el usuario introduce fechas inválidas, la validación se gestiona en
                la función `pedir_fecha`, que devuelve None y muestra un aviso.
    """
    
    # === Pedir fecha inicial ===
    f_inicio = pedir_fecha("Entra fecha inicio (dd-mm): ")

    # === Pedir fecha final ===
    f_fin = pedir_fecha("Entra fecha final (dd-mm): ")
    
    if f_fin <= f_inicio:
        f_temp = f_inicio
        f_inicio = f_fin
        f_fin = f_temp
        st.write(f"Has introducido las fechas en orden equivocado, las considero inicio {f_inicio.day}-{f_inicio.month} y fin {f_fin.day}-{f_fin.month}")
        
        # raise ValueError(
        #     f"⚠️ Fecha inválida: {f_fin.date()} no es posterior a {f_inicio.date()}."
        # )


    # === Convertir a formato YYYY-MM-DD ===
    f_inicio_str = f_inicio.strftime("%Y-%m-%d")
    f_fin_str = f_fin.strftime("%Y-%m-%d")



    # print("Fecha inicio:", f_inicio_str)
    # print("Fecha final:", f_fin_str)
    
    return f_inicio_str, f_fin_str


# %% [markdown]
# # 11.- Probabilidad variación

# %%
def years_ha_subido(df_train:pd.DataFrame, md_inicio:str, md_fin:str)->tuple:
    """Calcula, para cada año del conjunto de entrenamiento, el rendimiento obtenido entre
    dos fechas específicas del calendario (md_inicio y md_fin, en formato 'MM-DD').
    Determina cuántos años han sido positivos y cuántos negativos en ese intervalo,
    y devuelve un DataFrame con el beneficio porcentual por año.

    El cálculo del rendimiento entre dos días del año se realiza como:

        rendimiento = ((1 + rend_fin) / (1 + rend_inicio) - 1) * 100

    donde `rend_inicio` y `rend_fin` son los rendimientos acumulados del año en las
    fechas md_inicio y md_fin respectivamente.

    Args:
        df_train (pd.DataFrame): DataFrame pivotado donde:
                                - El índice son días del año en formato 'MM-DD'.
                                - Cada columna representa un año.
                                - La última columna suele ser 'rendimiento_medio' y se ignora en el cálculo.
        md_inicio (str): Día inicial en formato 'MM-DD'.
        md_fin (str): Día final en formato 'MM-DD'.

    Returns:
        tuple: df_beneficio_year (pd.DataFrame): Tabla con columnas ['year', 'beneficio'],
                donde 'beneficio' es el rendimiento porcentual entre md_inicio y md_fin.
            anno_negativo (int): Número de años con rendimiento negativo.
            anno_positivo (int): Número de años con rendimiento positivo.
    """
    
    # Contar rendimiento de cada año
    anno_positivo = 0
    anno_negativo =0
    df_beneficio_year = pd.DataFrame(columns=["year", "beneficio"])

    for y in df_train.columns[:-1]:
        rend_acum_inicio = df_train.loc[md_inicio, y]
        rend_acum_fin = df_train.loc[md_fin, y]

        rend_inicio_a_fin = ((((1 + rend_acum_fin) / (1 + rend_acum_inicio)) -1) * 100).round(2)

        if pd.notna(rend_inicio_a_fin): 
            df_beneficio_year.loc[len(df_beneficio_year)] = [y, rend_inicio_a_fin]
            if rend_inicio_a_fin >= 0: 
                anno_positivo += 1 
            else: 
                anno_negativo += 1

    return df_beneficio_year, anno_negativo, anno_positivo

# %% [markdown]
# # 12.- Visualizar variacion años entre fechas

# %%
def visualiza_variacion_years(df_beneficio_year:pd.DataFrame):
    """Genera un gráfico interactivo de barras horizontales que muestra el beneficio
    porcentual obtenido en cada año dentro de un intervalo específico del calendario.
    Cada barra se colorea según si el rendimiento del año fue positivo o negativo,
    facilitando la comparación visual entre años.

    El gráfico incluye:
    - Una barra horizontal por año, ordenada según el DataFrame original.
    - Colores diferenciados: verde para años con beneficio positivo y rojo para años negativos.
    - Eje X representando el beneficio porcentual.
    - Eje Y con los años correspondientes.
    - Estilo interactivo basado en Plotly.

    Args:
        df_beneficio_year (pd.DataFrame): DataFrame con al menos las columnas:
            - 'year': año correspondiente.
            - 'beneficio': rendimiento porcentual entre dos fechas del año.
            La función añade internamente una columna 'color' para la codificación visual.
    """

    # Crear columna de color según signo del beneficio
    df_beneficio_year["color"] = df_beneficio_year["beneficio"].apply(
        lambda x: "positivo" if x >= 0 else "negativo"
    )

    # Mapa de colores
    colores = {
        "positivo": "green",
        "negativo": "red"
    }

    # Gráfico de barras horizontales
    fig = px.bar(
        df_beneficio_year,
        x="beneficio",
        y="year",
        orientation="h",
        color="color",
        color_discrete_map=colores,
        title=f"Beneficio Año a Año - {name}"
    )
    
    fig.update_layout(
    title=dict(
        font=dict(size=30, color="black"),
        x=0
    )
)

    altura = len(df_beneficio_year) * 20  # Ajuste dinámico

    fig.update_layout(
        xaxis_title="Beneficio (%)", 
        yaxis_title="Año",
        margin=dict(t=60, b=40),
        height=altura
        )

    # Mostrar todos los años y en el orden del DataFrame 
    fig.update_yaxes( type='category', 
                    categoryorder="array", 
                    categoryarray=df_beneficio_year["year"] )

    fig.update_layout(showlegend=False)  # Oculta la leyenda si no la necesitas
    # fig.show()
    # st.plotly_chart(fig, use_container_width=True)
    st.plotly_chart(fig, width="stretch")



# %% [markdown]
# # 13.- Calculo volatilidad y sharpe ratio

# %%
def calculo_volatilidad_sharpe(df_train:pd.DataFrame, md_inicio:str, md_fin:str, rend_inicio_a_fin:float)->tuple:
    """Calcula la volatilidad, el ratio Sharpe y el ratio Sortino para un intervalo
    específico del calendario definido por dos días del año (md_inicio y md_fin).
    Los cálculos se basan en los rendimientos acumulados por año contenidos en
    el DataFrame de entrenamiento.

    Para cada año:
    - Se obtiene el rendimiento acumulado en md_inicio y md_fin.
    - Se calcula el rendimiento del periodo mediante:
          r_periodo = (1 + r_fin) / (1 + r_ini) - 1
    - Se almacena el rendimiento anual del intervalo.

    A partir de todos los rendimientos anuales:
    - La volatilidad se calcula como la desviación típica muestral.
    - El Sharpe ratio se obtiene dividiendo el rendimiento medio del periodo
      (rend_inicio_a_fin, expresado en %) entre la volatilidad.
    - El Sortino ratio se calcula igual que el Sharpe, pero usando solo la
      desviación típica de los rendimientos negativos. Si no hay rendimientos
      negativos, el Sortino se considera infinito.

    Args:
        df_train (pd.DataFrame): DataFrame pivotado donde:
            - El índice son días del año en formato 'MM-DD'.
            - Cada columna representa un año.
            - La columna 'rendimiento_medio' se excluye del cálculo.
        md_inicio (str): Día inicial del intervalo en formato 'MM-DD'.
        md_fin (str): Día final del intervalo en formato 'MM-DD'.
        rend_inicio_a_fin (float): Rendimiento total del periodo expresado en porcentaje.

    Returns:
        tuple: volatilidad (float): Desviación típica de los rendimientos del periodo.
                sharpe (float): Ratio Sharpe del intervalo.
                sortino (float): Ratio Sortino del intervalo.
    """
    
    # Calculo desviación tipica que es igual que la volatilidad entre md_inicio y md_fin
    cols_anios = [c for c in df_train.columns if c != "rendimiento_medio"]

    rendimientos_periodo = []

    for año in cols_anios:
        r_ini = df_train.loc[md_inicio, año]
        r_fin = df_train.loc[md_fin, año]

        # Fórmula correcta para rendimientos del periodo a partir de los acumulados de inicio y fin
        r_periodo = (1 + r_fin) / (1 + r_ini) - 1

        rendimientos_periodo.append(r_periodo)

    # Calculo desviación típica
    variacion_tipica = np.std(rendimientos_periodo, ddof=1).round(4)
    volatilidad = variacion_tipica

    # Sharpe ratio es una medida del retorno ajustado al riesgo. Valores mayores a 1 son generalmente considerados buenos.
    sharpe = ((rend_inicio_a_fin /100) / volatilidad).round(4)

    # === Sortino ratio === 
    # # Filtrar solo rendimientos negativos 
    downside = [r for r in rendimientos_periodo if r < 0] 
    
    if len(downside) == 0: 
        # Si nunca ha caído, el riesgo negativo es cero → Sortino infinito 
        sortino = np.inf 
    else: 
        downside_std = np.std(downside, ddof=1) 
        sortino = ((rend_inicio_a_fin / 100) / downside_std).round(4)

    
    return volatilidad, sharpe, sortino

# %% [markdown]
# # 14.- Interpretar Volatilidad

# %%
def interpretar_volatilidad(vol:float)->str:
    """Interpreta el nivel de volatilidad de un patrón estacional a partir de un valor
    decimal (por ejemplo, 0.1139 = 11.39%) y devuelve una descripción cualitativa
    del grado de estabilidad del comportamiento histórico.

    La clasificación se basa en el porcentaje equivalente:
        - < 1%     → Muy estable, patrón fuerte.
        - 1%–3%    → Moderadamente estable.
        - 3%–5%    → Volatilidad notable, requiere precaución.
        - > 5%     → Muy volátil, patrón débil.

    Args:
        vol (float): Volatilidad en formato decimal (ejemplo: 0.025 = 2.5%).

    Returns:
        str: Descripción cualitativa del nivel de volatilidad.
    """
    
    vol_pct = vol * 100  # convertir a porcentaje

    if vol_pct < 1:
        return "Muy estable, patrón fuerte"
    elif 1 <= vol_pct < 3:
        return "Moderadamente estable"
    elif 3 <= vol_pct < 5:
        return "Volatilidad notable, cuidado"
    else:
        return "Muy volátil, patrón débil"


# %% [markdown]
# # 15.- Interpretar Sharpe

# %%
def interpretar_sharpe(sharpe:float)->str:
    """Proporciona una interpretación cualitativa del Sharpe ratio según su valor.
    El Sharpe ratio mide la eficiencia del rendimiento ajustado al riesgo: valores
    más altos indican que la estrategia compensa mejor el riesgo asumido.

    La clasificación utilizada es:
        - > 2.0     → Excelente: riesgo muy bien compensado.
        - 1.0–2.0   → Bueno: relación rendimiento/riesgo sólida.
        - 0.5–1.0   → Aceptable: compensación adecuada pero sin destacar.
        - 0.0–0.5   → Débil: demasiado riesgo para la recompensa obtenida.
        - < 0.0     → Malo: rinde peor que un activo sin riesgo.

    Args:
        sharpe (float): Valor del Sharpe ratio.

    Returns:
        str: Descripción cualitativa del nivel de eficiencia riesgo/rendimiento.
    """

    if sharpe > 2:
        return "Excelente. Riesgo muy bien compensado; estrategia altamente eficiente."
    elif 1 <= sharpe <= 2:
        return "Bueno. Buena relación rendimiento/riesgo, comportamiento sólido."
    elif 0.5 <= sharpe < 1:
        return "Aceptable. El riesgo se compensa, pero sin destacar."
    elif 0 <= sharpe < 0.5:
        return "Débil. Mucho riesgo para poca recompensa."
    else:
        return "Malo. Rinde peor que un activo sin riesgo; el riesgo no compensa."


# %% [markdown]
# # 16.- Interpretar Sortino

# %%
def interpretar_sortino(sortino:float)->str:
    """Proporciona una interpretación cualitativa del Sortino ratio según su valor.
    El Sortino ratio mide el rendimiento ajustado únicamente al riesgo negativo,
    es decir, penaliza solo las caídas y no la volatilidad total como el Sharpe.

    La clasificación utilizada es:
        - > 3.0     → Excelente: caídas muy controladas y rendimiento sobresaliente.
        - 2.0–3.0   → Muy bueno: pocas caídas y rendimiento sólido.
        - 1.0–2.0   → Bueno: el rendimiento compensa claramente las caídas ocasionales.
        - 0.0–1.0   → Débil: demasiadas caídas o demasiado profundas para el rendimiento obtenido.
        - < 0.0     → Malo: el riesgo negativo domina y el rendimiento es insuficiente.

    Args:
        sortino (float): Valor del Sortino ratio.

    Returns:
        str: Descripción cualitativa del nivel de riesgo negativo frente al rendimiento.
    """

    if sortino > 3:
        return "Excelente. Caídas muy controladas; el rendimiento compensa sobradamente el riesgo negativo."
    elif 2 <= sortino <= 3:
        return "Muy bueno. El periodo rara vez cae y ofrece un rendimiento sólido."
    elif 1 <= sortino < 2:
        return "Bueno. El rendimiento supera claramente las caídas ocasionales."
    elif 0 <= sortino < 1:
        return "Débil. Las caídas son demasiado frecuentes o profundas para el rendimiento obtenido."
    else:
        return "Malo. El rendimiento está por debajo del mínimo aceptable; el riesgo negativo domina."


# %% [markdown]
# # 400.- PRINCIPAL 4: Comprobar fechas concretas

# %%

st.set_page_config(layout="wide")


sp500_top25 = {
    "Apple": "AAPL",
    "Microsoft": "MSFT",
    "Nvidia": "NVDA",
    "Amazon": "AMZN",
    "Meta": "META",
    "Alphabet Class A": "GOOGL",
    "Alphabet Class C": "GOOG",
    "Berkshire Hathaway": "BRK-B",
    "Eli Lilly": "LLY",
    "Broadcom": "AVGO",
    "Tesla": "TSLA",
    "JPMorgan": "JPM",
    "UnitedHealth": "UNH",
    "Visa": "V",
    "Exxon Mobil": "XOM",
    "Mastercard": "MA",
    "Johnson & Johnson": "JNJ",
    "Procter & Gamble": "PG",
    "Home Depot": "HD",
    "Costco": "COST",
    "Merck": "MRK",
    "Chevron": "CVX",
    "AbbVie": "ABBV",
    "PepsiCo": "PEP",
    "Walmart": "WMT"
}

# opciones = [f"{k} → {v}" for k, v in sp500_top25.items()]
# eleccion = st.selectbox("Elige una opción:", opciones)
# clave = eleccion.split(" → ")[0]
# name = clave
# ticker = sp500_top25[clave]

opciones = sorted([f"{k} → {v}" for k, v in sp500_top25.items()])

eleccion = st.sidebar.radio("Selecciona:", opciones)

clave = eleccion.split(" → ")[0]
# st.write("Clave:", clave)
# st.write("Valor:", sp500_top25[clave][clave])
name = clave
ticker = sp500_top25[clave]



# importar los ficheros con los datos ya tratados
input_folder = "SP500_Top25_tratados"
# name = "Amazon"
# ticker = "AMZN"


df_train = pd.read_parquet(f"{input_folder}/{name}_{ticker}_train.parquet")

# 9.- Visualiza media por dia del beneficio acumulado de todos los años
visualiza_beneficio_acum_medio(df_train, name)




# 1.- Entrada de fechas de inici y fin en formato dd-mm
f_inicio_str, f_fin_str = pedir_validar_fecha()
md_inicio = f_inicio_str[5:]
md_fin = f_fin_str[5:]

# 2.- Calcular el retorno medio y la duracion en dias de este periodo
rend_acum_inicio = df_train.loc[md_inicio, "rendimiento_medio"]
rend_acum_fin = df_train.loc[md_fin, "rendimiento_medio"]

rend_inicio_a_fin = ((((1 + rend_acum_fin) / (1 + rend_acum_inicio)) -1) * 100).round(2)

diferencia = (datetime.strptime(f_fin_str, "%Y-%m-%d") - datetime.strptime(f_inicio_str, "%Y-%m-%d")).days

# Contar rendimiento de cada año para la probabilidad de subida
df_beneficio_year, anno_negativo, anno_positivo = years_ha_subido(df_train, md_inicio, md_fin)


# 4.- Calculo desviación tipica que es igual que la volatilidad, el ratio sharpe y el ratio sortino
volatilidad, sharpe, sortino = calculo_volatilidad_sharpe(df_train, md_inicio, md_fin, rend_inicio_a_fin)



# Construcción del resumen anual completo
probabilidad = (anno_positivo / (anno_negativo + anno_positivo)) * 100

comentario_probabilidad = (
    "Probabilidad mayor del 60%" 
    if probabilidad > 60 
    else "Probabilidad menor del 60%"
)

mm, dd = md_inicio.split("-")
md_inicio_convertido = f"{dd}-{mm}"
mm, dd = md_fin.split("-")
md_fin_convertido = f"{dd}-{mm}"


resumen = pd.DataFrame({
    "Dia-Mes inicio pauta:": md_inicio_convertido,
    "Dia-Mes final pauta:": md_fin_convertido,
    "Días duración:": diferencia,
    "Total Años:": anno_negativo + anno_positivo,
    "Años en negativo (#):": anno_negativo,
    "Años en negativo (%):": (anno_negativo/(anno_negativo+anno_positivo))*100,
    "Años en positivo (#):": anno_positivo,
    "Años en positivo (%):": (anno_positivo/(anno_negativo+anno_positivo))*100,
    "Sharpe:": sharpe,
    "Sortino:": sortino,
    "Rendimiento medio en la pauta (%):": rend_inicio_a_fin,
    "Volatilidad (%):": volatilidad*100
}, index=[0]).T



resumen.columns = [""]

# Formateo manual de decimales 
resumen.loc["Volatilidad (%):", ""] = f"{volatilidad*100:.2f}" 
resumen.loc["Sharpe:", ""] = f"{sharpe:.4f}" 
resumen.loc["Sortino:", ""] = f"{sortino:.4f}" 
resumen.loc["Rendimiento medio en la pauta (%):", ""] = f"{rend_inicio_a_fin:.2f}"
resumen.loc["Años en negativo (%):", ""] = f"{(anno_negativo/(anno_negativo+anno_positivo))*100:.2f}"
resumen.loc["Años en positivo (%):", ""] = f"{(anno_positivo/(anno_negativo+anno_positivo))*100:.2f}" 

# Comentarios
resumen["Comentario"] = ""
resumen.loc["Volatilidad (%):", "Comentario"] = interpretar_volatilidad(volatilidad)
resumen.loc["Sharpe:", "Comentario"] = interpretar_sharpe(sharpe)
resumen.loc["Sortino:", "Comentario"] = interpretar_sortino(sortino)
resumen.loc["Años en positivo (%):", "Comentario"] = comentario_probabilidad

pd.set_option("display.max_colwidth", None)

# Mostrar con alineación izquierda SOLO en Comentario
# display(resumen.style.set_properties(subset=["Comentario"], **{"text-align": "left"}))
html = resumen.style.set_properties(
    subset=["Comentario"],
    **{"text-align": "left"}
).to_html()

st.markdown(html, unsafe_allow_html=True)






# 6.- Visualiza la variacion en todos los años entre las fechas (mm-dd) introducidas
visualiza_variacion_years(df_beneficio_year)




