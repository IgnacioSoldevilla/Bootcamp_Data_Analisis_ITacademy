

# %%
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import seaborn as sns
from datetime import datetime
from sklearn.cluster import KMeans
import calendar
import streamlit as st



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

opciones = sorted([f"{k} → {v}" for k, v in sp500_top25.items()])

eleccion = st.sidebar.radio("Selecciona:", opciones)

clave = eleccion.split(" → ")[0]

name = clave
ticker = sp500_top25[clave]

input_folder = "SP500_Top25_resultados"

st.set_page_config(
    page_title="Dashboard Estacional Resultados",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ***************************************************************************************************************
# Inyectamos el título en la barra superior fija de Streamlit
st.markdown(f"""
<style>
[data-testid="stToolbar"] {{
    display: none;
}}

[data-testid="stHeader"]::after {{
    content: "📊 {name}: RESULTADOS ESTADISTICOS";
    font-size: 1.4rem;
    font-weight: 700;
    color: #1f77b4;
    position: absolute;
    top: 12px;
    left: 370px;
}}

[data-testid="stHeader"] {{
    border-bottom: 4px solid #006bb3;
}}
</style>
""", unsafe_allow_html=True)






# *******************************************************************************************************************

# Titulo
# st.title(f"{name}: RESULTADOS ESTADISTICOS")

# Indice
with st.sidebar:
    st.markdown("""
    ## Índice
    - [Resumen Global](#resumen)
    - [Introducción visual](#introduccion)
    - [Robustez](#robustez)
    - [Resultados monetarios](#monetarios)
    - [Análisis avanzado](#avanzado)
    - [Conclusiones](#conclusiones)
    """, unsafe_allow_html=True)



df_final = pd.read_parquet(f"{input_folder}/{name}_{ticker}_final.parquet")

df_total_backtest_ordenado = pd.read_parquet(f"{input_folder}/total_backtest_ordenado.parquet")





# %% [markdown]
# # 1.- Introducción visual: Heatmap + ranking.


st.header(":blue[Introducción visual]", anchor="introduccion")

st.markdown("""
<style>
h2 {
    border-bottom: 3px solid #1f77b4;
    padding-bottom: 4px;
}
</style>
""", unsafe_allow_html=True)




# %%
# Ventanas operadas por año
resumen_anual = df_total_backtest_ordenado[df_total_backtest_ordenado["name"] == name]
# display(resumen_anual)

ax = resumen_anual["ventanas_operadas"].plot(kind="bar", figsize=(8,4), color="#cccccc")

ax.set_xticks(range(len(resumen_anual)))
ax.set_xticklabels(resumen_anual["periodo"], rotation=0)

plt.title(f"Número de ventanas operadas por año — {name}")
plt.ylabel("Ventanas")
plt.xlabel("")

# Añadir el valor encima de cada barra 
for i, v in enumerate(resumen_anual["ventanas_operadas"]): 
    ax.text( 
            i, 
            v + (v * 0.001), # un pequeño margen por encima de la barra 
            f"{v:.0f}", 
            ha='center', 
            va='bottom', 
            fontsize=9 
            )

# plt.show()
st.pyplot(plt)
# plt.clf()   # ← limpia la figura


# %%
# 1. Preparar el DataFrame para el heatmap
df_plot = df_final.copy()
df_plot = df_plot.rename(columns={"rend_inicio_a_fin": "rend_historico"})
df_plot = df_plot.sort_values("md_inicio")

# 2. Identificar columnas de rendimiento (todas las que empiezan por "rend_")
cols_rend = [c for c in df_plot.columns if c.startswith("rend_")]

# 3. Crear índice tipo "MM-DD → MM-DD"
df_plot.index = df_plot["md_inicio"] + " → " + df_plot["md_fin"]

# 4. Dibujar el heatmap
# plt.figure(figsize=(10, 6))
plt.figure(figsize=(8, 4))
sns.heatmap(df_plot[cols_rend], annot=False, cmap="RdYlGn", center=0, vmin=df_plot[cols_rend].min().min(), vmax=df_plot[cols_rend].max().max())
plt.title(f"Rendimientos por año (validación) — {name}")
plt.xlabel("Años de validación")
plt.ylabel("Ventanas estacionales")
# plt.show()
st.pyplot(plt)
plt.clf()   # ← limpia la figura


# %%


# Copia para no modificar df_final original
df_plot = df_final.copy()
df_plot = df_plot.rename(columns={"rend_inicio_a_fin": "rend_historico"})

# Identificar columnas de validación
cols_rend = [c for c in df_plot.columns if c.startswith("rend_")]

# Preparar DataFrame largo (melt)
df_melt = df_plot.melt(
    id_vars=["md_inicio", "md_fin", "rend_historico"],
    value_vars=cols_rend,
    var_name="año",
    value_name="rendimiento"
)

# Crear etiqueta de ventana
df_melt["ventana"] = df_melt["md_inicio"] + " → " + df_melt["md_fin"]

# Extraer mes para detectar cambios
df_melt["mes"] = df_melt["md_inicio"].str.slice(0, 2).astype(int)

# Ordenar por fecha para que las líneas verticales tengan sentido
df_melt = df_melt.sort_values(["mes", "md_inicio"])

# Detectar posiciones donde cambia el mes
line_positions = []
ventanas_ordenadas = df_melt["ventana"].unique()

meses = df_melt.drop_duplicates("ventana")["mes"].tolist()
for i in range(1, len(meses)):
    if meses[i] != meses[i-1]:
        line_positions.append(i)

# Crear figura
fig = go.Figure()

# --- Línea del rendimiento histórico ---
df_hist = df_melt.drop_duplicates("ventana")

fig.add_trace(
    go.Scatter(
        x=df_hist["ventana"],
        y=df_hist["rend_historico"],
        mode="lines",
        name="Histórico",
        line=dict(color="black", width=3)
    )
)

# --- Puntos de cada año de validación ---
colores = {
    "rend_historico": "black",
    "rend_2024": "#9467bd",
    "rend_2025": "#2ca02c"
}


for año in df_melt["año"].unique():
    df_year = df_melt[df_melt["año"] == año]
    fig.add_trace(
        go.Scatter(
            x=df_year["ventana"],
            y=df_year["rendimiento"],
            mode="markers",
            name=año,
            marker=dict(size=9, color=colores[año], opacity=0.7)
        )
    )

# --- Líneas verticales por meses ---
for pos in line_positions:
    fig.add_vline(
        x=pos,
        line_width=1,
        line_dash="dash",
        line_color="blue"
    )

# Layout
fig.update_layout(
    title=dict(
        text=f"Comparativa: Rendimiento histórico vs. validación — {name}",
        font=dict(size=30, color="black"),
        x=0
        ),
    xaxis_title="Ventana estacional",
    yaxis_title="Rendimiento (%)",
    height=700,
    width=800,
)

fig.update_xaxes(tickangle=90)

# fig.show()
st.plotly_chart(fig, width="stretch")


# %% [markdown]


# %%

# --- Preparar datos ---

# Orden 1: ranking puro (mejor → peor)
df_rank = df_final.sort_values("media_validacion", ascending=False)

# Orden 2: orden estacional por fecha de inicio
df_fecha = df_final.sort_values("md_inicio")

# Etiquetas tipo "MM-DD → MM-DD"
df_rank["ventana"] = df_rank["md_inicio"] + " → " + df_rank["md_fin"]
df_fecha["ventana"] = df_fecha["md_inicio"] + " → " + df_fecha["md_fin"]

# --- Detectar cambios de mes para líneas verticales ---
# Extraer mes como número
df_fecha["mes"] = df_fecha["md_inicio"].str.slice(0, 2).astype(int)

# Posiciones donde cambia el mes
line_positions = []
for i in range(1, len(df_fecha)):
    if df_fecha["mes"].iloc[i] != df_fecha["mes"].iloc[i-1]:
        line_positions.append(i)

# --- Crear figura con 2 subplots ---
fig = make_subplots(
    rows=2, cols=1,
    shared_xaxes=False,
    vertical_spacing=0.15,
    subplot_titles=(
        "Ranking por media de validación (mejor → peor)",
        "Ranking por fecha de inicio (orden estacional)"
    )
)

# --- Subplot 1: Ranking puro ---
colors_rank = ["green" if v > 0 else "red" for v in df_rank["media_validacion"]]

fig.add_trace(
    go.Bar(
        x=df_rank["ventana"],
        y=df_rank["media_validacion"],
        marker_color=colors_rank,
        name="Ranking puro"
    ),
    row=1, col=1
)

# --- Subplot 2: Orden por fecha ---
colors_fecha = ["green" if v > 0 else "red" for v in df_fecha["media_validacion"]]

fig.add_trace(
    go.Bar(
        x=df_fecha["ventana"],
        y=df_fecha["media_validacion"],
        marker_color=colors_fecha,
        name="Orden estacional"
    ),
    row=2, col=1
)

# --- Añadir líneas verticales por meses en el subplot 2 ---
for pos in line_positions:
    fig.add_vline(
        x=pos,
        line_width=1,
        line_dash="dash",
        line_color="blue",
        row=2, col=1
    )

# --- Layout ---
fig.update_layout(
    height=900,
    width=800,
    title=dict(
        text=f"Comparativa de Rankings de Ventanas Estacionales — {name}",
        font=dict(size=30, color="black"),
        x=0
        ),
    showlegend=False
)

fig.update_xaxes(tickangle=90)

# fig.show()
st.plotly_chart(fig, width="stretch")


# %% [markdown]
# # 2.- Robustez: Boxplot + porcentaje de acierto + scatter media vs volatilidad.

st.header(":blue[Robustez]", anchor="robustez")


# %%
# Transformar de formato ancho a largo
df_plot = df_final.copy()
df_plot = df_plot.rename(columns={"rend_inicio_a_fin": "rend_historico"})
df_plot = df_plot.sort_values("md_inicio")

df_box = df_plot[cols_rend].melt(
    var_name="Año",
    value_name="Rendimiento"
)

# Crear boxplot interactivo
fig = px.box(
    df_box,
    x="Año",
    y="Rendimiento",
    title=f"Distribución de rendimientos por año — {name}",
    points="all",  # muestra todos los puntos individuales
    template="plotly_white",
    color="Año"
)

fig.update_layout(
    title=dict(
        text=f"Distribución de rendimientos por año — {name}",
        font=dict(size=30, color="black"),
        x=0.0
    )
)


fig.update_traces(marker=dict(size=4, opacity=0.6))

# Quitar etiqueta del eje X
fig.update_xaxes(title_text=None)
# Quitar leyenda
fig.update_layout(showlegend=False)

# fig.show()
st.plotly_chart(fig, width="stretch")



# %%
# --- Preparar datos ---

df_pct = df_final.sort_values("md_inicio").copy()

# Etiqueta de ventana
df_pct["ventana"] = df_pct["md_inicio"] + " → " + df_pct["md_fin"]

# Extraer mes para detectar cambios
df_pct["mes"] = df_pct["md_inicio"].str.slice(0, 2).astype(int)

# Detectar posiciones donde cambia el mes
line_positions = []
meses = df_pct["mes"].tolist()
for i in range(1, len(meses)):
    if meses[i] != meses[i-1]:
        line_positions.append(i)

# --- Colorear por cuartiles ---
q1, q2, q3 = np.percentile(df_pct["pct_acierto"], [25, 50, 75])

def asignar_cuartil(valor):
    if valor <= q1:
        return "Q1 (bajo)"
    elif valor <= q2:
        return "Q2"
    elif valor <= q3:
        return "Q3"
    else:
        return "Q4 (alto)"

df_pct["cuartil"] = df_pct["pct_acierto"].apply(asignar_cuartil)

# Paleta de colores por cuartil
colores = {
    "Q1 (bajo)": "#003f5c",
    "Q2": "#59defc",
    "Q3": "#91bfdb",
    "Q4 (alto)": "#76ff03"
}

# --- Crear figura ---
fig = go.Figure()

fig.add_trace(
    go.Bar(
        x=df_pct["ventana"],
        y=df_pct["pct_acierto"],
        marker_color=[colores[c] for c in df_pct["cuartil"]],
        text=df_pct["cuartil"],
        hovertemplate="<b>%{x}</b><br>% acierto: %{y:.1f}%<br>Cuartil: %{text}<extra></extra>"
    )
)

# --- Líneas verticales por meses ---
for pos in line_positions:
    fig.add_vline(
        x=pos - 0.5,
        line_width=1,
        line_dash="dash",
        line_color="gray"
    )

# --- Línea horizontal de referencia ---
fig.add_hline(
    y=50,
    line_width=2,
    line_dash="dot",
    line_color="black",
    annotation_text="50% referencia",
    annotation_position="top left",
    annotation_font=dict(color="red", size=16)
)

# --- Layout ---
fig.update_layout(
    title=dict(
        text=f"Porcentaje aciertos por ventana — {name}",
        font=dict(size=30, color="black"),
        x=0  # 0 = izquierda, 0.5 = centrado
    ),
    xaxis_title="Ventana estacional",
    yaxis_title="% acierto",
    height=700,
    width=800,
    # height=600,
    # width=1400,
    xaxis_tickangle=90,
    showlegend=False
)

# fig.show();
st.plotly_chart(fig, width="stretch")



# %%
# Media vs. Volatilidad de ventanas estacionales

# Calcular el máximo ranking
max_rank = int(df_final["ranking"].max())

fig = px.scatter(
    df_final,
    x="media_validacion",
    y="std_validacion",
    title=f"Rendimiento medio vs. Volatilidad de ventanas estacionales - {name}",
    labels={
        "media_validacion": "Rendimiento medion (%)",
        "std_validacion": "Volatilidad (std)"
    },
    hover_data=["md_inicio", "md_fin", "ranking"],
    color="ranking",
    color_continuous_scale="viridis",
    range_color=[1, max_rank]
)

fig.update_layout(
    title=dict(
        text=f"Rendimiento medio vs. Volatilidad de ventanas estacionales - {name}",
        font=dict(size=30, color="black"),
        x=0  # 0 = izquierda, 0.5 = centrado
    )
)


fig.update_traces(marker=dict(size=10, opacity=0.8))

fig.update_layout(
    height=700,
    width=800,
    # height=600,
    # width=900,
    xaxis=dict(showgrid=True),
    yaxis=dict(showgrid=True),
    coloraxis_colorbar=dict(
        title=dict(
            text="Ranking ventanas",
            side="right"
        ),
        tickvals=[1, max_rank],
        ticktext=[f"1 (mejor)", f"{max_rank} (peor)"],
        x=1.15,      # mueve la barra hacia la derecha
        xpad=30      # añade espacio entre barra y título
    )
)
fig.update_traces(marker=dict(size=10, opacity=0.6))


# fig.show()
st.plotly_chart(fig, width="stretch")


# %%

# --- Detectar columna de volatilidad automáticamente ---
col_std = [c for c in df_final.columns if "std" in c.lower()][0]

# --- Copia del DF ---
df_scatter = df_final.copy()

# --- LIMPIEZA CRÍTICA: eliminar inf, -inf y NaN ---
df_scatter = df_scatter.replace([np.inf, -np.inf], np.nan)
df_scatter = df_scatter.dropna(subset=["media_validacion", col_std])

# --- Resetear índice para evitar desalineaciones ---
df_scatter = df_scatter.reset_index(drop=True)

# --- Preparar datos para clustering ---
df_cluster = df_scatter[["media_validacion", col_std]]

# Si hay menos de 3 puntos válidos, no se puede hacer clustering
if len(df_cluster) >= 3:
    kmeans = KMeans(n_clusters=3, random_state=0)
    clusters = kmeans.fit_predict(df_cluster)
    df_scatter["cluster"] = clusters
else:
    df_scatter["cluster"] = 0  # un solo cluster si no hay suficientes puntos

# Paleta de colores para clusters
palette = px.colors.qualitative.Set2

# --- Crear figura ---
fig = go.Figure()

fig.add_trace(
    go.Scatter(
        x=df_scatter["media_validacion"],
        y=df_scatter[col_std],
        mode="markers",
        marker=dict(
            size=12,
            opacity=0.8,
            color=[palette[int(c)] for c in df_scatter["cluster"]],
            line=dict(width=1, color="black")
        ),
        text=df_scatter["md_inicio"] + " → " + df_scatter["md_fin"],
        hovertemplate="<b>%{text}</b><br>Media: %{x:.2f}%<br>Volatilidad: %{y:.2f}<extra></extra>"
    )
)

# --- Líneas de referencia ---
fig.add_hline(
    y=df_scatter[col_std].median(),
    line_dash="dot",
    line_color="gray",
    annotation_text="Mediana volatilidad",
    annotation_position="top right",
    annotation_yshift=5
)

fig.add_vline(
    x=df_scatter["media_validacion"].median(),
    line_dash="dot",
    line_color="gray",
    annotation_text="Mediana rend. medio",
    # annotation_text="Mediana media",
    annotation_position="top left",
    annotation_yshift=20,
    annotation_xshift=60
)

# --- Anotaciones ---
best_idx = df_scatter["media_validacion"].idxmax()
fig.add_annotation(
    x=df_scatter.loc[best_idx, "media_validacion"],
    y=df_scatter.loc[best_idx, col_std],
    text="⭐ Mejor Rendimiento",
    showarrow=True,
    arrowhead=2,
    font=dict(color="red", size=16),
    arrowcolor="red"
)

stable_idx = df_scatter[col_std].idxmin()
fig.add_annotation(
    x=df_scatter.loc[stable_idx, "media_validacion"],
    y=df_scatter.loc[stable_idx, col_std],
    text="🔒 Más estable",
    showarrow=True,
    arrowhead=2,
    font=dict(color="red", size=16),
    arrowcolor="red"
)

# --- Layout ---
fig.update_layout(
    title=dict(
        text=f"Rend. medio vs. Volatilidad de ventanas estacionales (3 clusters) — {name}",
        font=dict(size=30, color="black"),
        x=0  # 0 = izquierda, 0.5 = centrado
    ),
    xaxis_title="Rendimiento medio (%)",
    yaxis_title="Volatilidad (std)",
    height=700,
    width=800,
    xaxis=dict(showgrid=True),
    yaxis=dict(showgrid=True),
)

# fig.show()
st.plotly_chart(fig, width="stretch")

# %% [markdown]

# %% [markdown]
# # 3.- Resultados monetarios: Beneficio anual + mejor/peor operación + capital final.


st.header(":blue[Resultados monetarios]", anchor="monetarios")

# %%

df_filtrado = df_total_backtest_ordenado[df_total_backtest_ordenado["name"] == name][["capital_inicial", 
                                                                                    "capital_final",
                                                                                    "beneficio_total",
                                                                                    "retorno_%",
                                                                                    "ventanas_operadas",
                                                                                    "drawdown_max",
                                                                                    "mejor_operacion",
                                                                                    "periodo"
                                                                                    ]]

df2 = (
    df_filtrado.set_index("periodo")          # periodo pasa a ser índice
    # .T                              # transponemos filas ↔ columnas
)

st.write(df2)


# %%
# Beneficio total por año
resumen_anual = df2

ax = resumen_anual["beneficio_total"].plot(kind="bar", figsize=(8,4), color="steelblue")
plt.title(f"Beneficio anual — {name}")
plt.ylabel("€")
plt.xlabel("Periodo")

# Poner etiquetas del eje X en horizontal
plt.xticks(rotation=0)

# Añadir el valor encima de cada barra 
for i, v in enumerate(resumen_anual["beneficio_total"]): 
    ax.text( 
            i, 
            v + (v * 0.001), # un pequeño margen por encima de la barra 
            f"{v:.2f}€", 
            ha='center', 
            va='bottom', 
            fontsize=7 
            )

# plt.show()
st.pyplot(plt)
plt.clf()   # ← limpia la figura


# %%
# Retorno anual (%)
ax = resumen_anual["retorno_%"].plot(kind="bar", figsize=(8,4), color="steelblue")
plt.title(f"Retorno anual (%) — {name}")
plt.ylabel("%")
plt.xlabel("Periodo")

# Poner etiquetas del eje X en horizontal
plt.xticks(rotation=0)

# Añadir el valor encima de cada barra 
for i, v in enumerate(resumen_anual["retorno_%"]): 
    ax.text( 
            i, 
            v + (v * 0.001), # un pequeño margen por encima de la barra 
            f"{v:.2f}%", 
            ha='center', 
            va='bottom', 
            fontsize=7 
            )

# plt.show()
st.pyplot(plt)
plt.clf()   # ← limpia la figura



# %%
# Gráfico combinado: mejor vs peor operación

ax = resumen_anual[["mejor_operacion", "drawdown_max"]].plot(
    kind="bar",
    figsize=(8,4),
    color=["green", "red"]
)

plt.legend(fontsize=6, loc="upper right")

plt.title(f"Mejor y peor operación por año — {name}")
plt.ylabel("€")
plt.xlabel("Periodo")
plt.grid(axis="y", alpha=0.3)

# Poner etiquetas del eje X en horizontal
plt.xticks(rotation=0)

# Añadir etiquetas a cada barra
for container in ax.containers:
    ax.bar_label(
        container,
        fmt="%.2f€",
        padding=3,
        fontsize=7
    )

# plt.show()
st.pyplot(plt)
plt.clf()   # ← limpia la figura


# %% [markdown]
# # 4.- Análisis avanzado: Histograma + correlación + curva de equity.


st.header(":blue[Análisis avanzado]", anchor="avanzado")

# %%
# HISTOGRAMA

rendimientos = pd.concat([
    df_final["rend_2024"],
    df_final["rend_2025"]
], axis=0)

fig = px.histogram(
    rendimientos,
    nbins=40,
    marginal="box",
    opacity=0.75,
    title=f"Histograma de rendimientos por ventana — {name}",
    labels={"value": "Rendimiento (%)"},
    template="plotly_white"
)

fig.update_layout(
    title=dict(
        text=f"Histograma de rendimientos por ventana — {name}",
        font=dict(size=30, color="black"),
        x=0  # 0 = izquierda, 0.5 = centrado
    )
)

fig.update_traces(marker_color="steelblue")

# Quitar la leyenda "variable"
fig.update_layout(showlegend=False)
# fig.show()
st.plotly_chart(fig, width="stretch")


# %%
# Crear un DataFrame largo con etiqueta de año
rendimientos = pd.DataFrame({
    "valor": pd.concat([df_final["rend_2024"], df_final["rend_2025"]], axis=0),
    "año":   ["2024"] * len(df_final) + ["2025"] * len(df_final)
})

fig = px.histogram(
    rendimientos,
    x="valor",
    color="año",              # colores distintos por año
    nbins=40,
    marginal="box",
    opacity=0.55,             # permite ver la superposición
    barmode="overlay",        # superponer histogramas
    title=f"Histograma de rendimientos por ventana y año — {name}",
    labels={"valor": "Rendimiento (%)"},
    template="plotly_white",
    color_discrete_map={
        "2024": "steelblue",
        "2025": "indianred"
    }
)

fig.update_layout(
    title=dict(
        text=f"Histograma de rendimientos por ventana y año — {name}",
        font=dict(size=30, color="black"),
        x=0  # 0 = izquierda, 0.5 = centrado
    )
)

# fig.show()
st.plotly_chart(fig, width="stretch")



# %%
# CURVA EQUITY

# Convertir md_inicio (MM-DD) en fecha artificial
df_final["fecha_md"] = pd.to_datetime("2000-" + df_final["md_inicio"], format="%Y-%m-%d")

# Extraer nombre de mes (para mostrar en el eje X)
df_final["mes_nombre"] = df_final["fecha_md"].dt.strftime("%B")



capital_inicial = 10000
capital_por_ventana = 1000
anios = [2024, 2025]

fig = go.Figure()

for year in anios:
    # Filtrar solo ventanas con datos para ese año
    df_year = df_final[df_final[f"rend_{year}"].notna()].copy()

    # Beneficio por ventana
    df_year["benef"] = (df_year[f"rend_{year}"] / 100) * capital_por_ventana

    # Equity acumulado
    df_year["equity"] = capital_inicial + df_year["benef"].cumsum()

    # Ordenar por fecha MM-DD
    df_year = df_year.sort_values("fecha_md")

    color_map = {
        2024: "#1f77b4",   # azul
        2025: "#DAA520"    # naranja
    }

    fig.add_trace(go.Scatter(
        x=df_year["fecha_md"],       # eje X con mes y día
        y=df_year["equity"],
        mode="lines+markers",
        name=f"Equity {year}",
        line=dict(width=3, color=color_map[year]),
        marker=dict(size=6, color=color_map[year]),
        fill="tozeroy",
        opacity=0.25
    ))

# Línea horizontal del capital inicial
fig.add_hline(
    y=capital_inicial,
    line=dict(color="gray", width=2, dash="dash"),
    annotation_text="Capital inicial",
    annotation_position="top left",
    annotation_yshift=-25
)

fig.update_layout(
    title=f"Curva de equity anual — {name}",
    xaxis_title="Mes",
    yaxis_title="Capital (€)",
    template="plotly_white",
    hovermode="x unified",
    xaxis=dict(
        tickformat="%b",  # Mostrar solo el mes (Jan, Feb, Mar…)
        dtick="M1"        # Un tick por mes
    )
)

fig.update_layout(
    title=dict(
        text=f"Curva de equity anual — {name}",
        font=dict(size=30, color="black"),
        x=0  # 0 = izquierda, 0.5 = centrado
    )
)

# fig.show()
st.plotly_chart(fig, width="stretch")



# %% [markdown]
# # 5.- Conclusiones: Ventanas más sólidas, riesgos, oportunidades.

# %%
st.header(":blue[Conclusiones]", anchor="conclusiones")

df = df_scatter.copy()

# Umbrales dinámicos
med_media = df["media_validacion"].median()
med_std   = df["std_validacion"].median()
med_sharpe = df["sharpe"].median()
med_sortino = df["sortino"].median()

# Clasificación
def clasificar(fila):
    media = fila["media_validacion"]
    std   = fila["std_validacion"]
    r24   = fila["rend_2024"]
    r25   = fila["rend_2025"]
    prob  = fila["probabilidad_positivo"]
    sharpe = fila["sharpe"]
    sortino = fila["sortino"]

    # Ventanas sólidas
    if media >= med_media and std <= med_std and prob >= 0.70 and sharpe >= med_sharpe:
        return "solida"

    # Ventanas estables
    if std <= med_std and media >= 0:
        return "estable"

    # Ventanas agresivas
    if media >= med_media and std > med_std:
        return "agresiva"

    # Ventanas débiles
    if media < med_media and std > med_std:
        return "debil"

    return "neutral"

df["categoria"] = df.apply(clasificar, axis=1)

# Identificar mejor y más estable
mejor = df.loc[df["media_validacion"].idxmax()]
mas_estable = df.loc[df["std_validacion"].idxmin()]

df_counts = df.groupby(["categoria"])[["categoria"]].count().rename(columns={"categoria": "Cantidad"})



# %%


orden_categorias = ["solida", "estable", "agresiva", "debil", "neutral"]

# Contar ventanas por categoría
df_counts = (
    df.groupby("categoria")[["categoria"]]
      .count()
      .rename(columns={"categoria": "Cantidad"})
      .reset_index()
      .sort_values("Cantidad", ascending=True)
)

# Orden dinámico según la cantidad (ya ordenado)
orden_categorias_asc = df_counts["categoria"].tolist()

fig = px.pie(
    df_counts,
    names="categoria",
    values="Cantidad",
    hole=0.4,
    title=f"Distribución ventanas por categoría - {name}",
    category_orders={"categoria": orden_categorias_asc},
    color="categoria",
    color_discrete_map={
    "solida": "#55A868",     # verde elegante
    "estable": "#4C72B0",    # azul suave
    "agresiva": "#E25822",   # rojo anaranjado clásico
    "debil": "#7D420E",      # naranja marronado
    "neutral": "#808080"     # Gris medio neutro
    },
    hover_data=["Cantidad"]   
)

fig.update_layout(
    title=dict(
        text=f"Distribución ventanas por categoría - {name}",
        font=dict(size=30, color="black"),
        x=0  # 0 = izquierda, 0.5 = centrado
    )
)

fig.update_traces(rotation=0)

# fig.show()
st.plotly_chart(fig, width="stretch")

# *************************************************************************************************


# ---------------------------------------------------------
# 1) CLASIFICACIÓN NUEVA
# ---------------------------------------------------------

df = df_scatter.copy()

med_media = df["media_validacion"].median()
med_std   = df["std_validacion"].median()
med_sharpe = df["sharpe"].median()
med_sortino = df["sortino"].median()

def clasificar(fila):
    media = fila["media_validacion"]
    std   = fila["std_validacion"]
    prob  = fila["probabilidad_positivo"]
    sharpe = fila["sharpe"]

    if media >= med_media and std <= med_std and prob >= 0.70 and sharpe >= med_sharpe:
        return "solida"

    if std <= med_std and media >= 0:
        return "estable"

    if media >= med_media and std > med_std:
        return "agresiva"

    if media < med_media and std > med_std:
        return "debil"

    return "neutral"

df["categoria"] = df.apply(clasificar, axis=1)

# ---------------------------------------------------------
# 2) FUNCIONES DE FECHA (sin cambios)
# ---------------------------------------------------------

def convertir_fecha_segura(md):
    mes, dia = map(int, md.split("-"))
    ultimo_dia = calendar.monthrange(2000, mes)[1]
    dia = min(dia, ultimo_dia)
    return datetime(2000, mes, dia)

def punto_medio(md_inicio, md_fin):
    f1 = convertir_fecha_segura(md_inicio)
    f2 = convertir_fecha_segura(md_fin)
    return f1 + (f2 - f1) / 2

# ---------------------------------------------------------
# 3) PREPARAR DATOS PARA EL GRÁFICO
# ---------------------------------------------------------

df["fecha_inicio"] = df["md_inicio"].apply(convertir_fecha_segura)
df["fecha_fin"] = df["md_fin"].apply(convertir_fecha_segura)
df["fecha_medio"] = df.apply(lambda r: punto_medio(r["md_inicio"], r["md_fin"]), axis=1)

# Colores modernos
colores_modernos = {
    "solida": "#55A868",     # verde elegante
    "estable": "#4C72B0",    # azul suave
    "agresiva": "#E25822",   # rojo anaranjado clásico
    "debil": "#7D420E",      # naranja marronado
    "neutral": "#808080"     # Gris medio neutro
}

# ---------------------------------------------------------
# 4) GRÁFICO ESTACIONAL EN PLOTLY (idéntico al original)
# ---------------------------------------------------------

def grafico_estacional_plotly(df):
    fig = go.Figure()

    # Añadir puntos por categoría (como Matplotlib)
    for categoria, color in colores_modernos.items():
        df_cat = df[df["categoria"] == categoria]

        fig.add_trace(go.Scatter(
            x=df_cat["fecha_medio"],
            y=df_cat["rend_inicio_a_fin"],
            mode="markers",
            name=categoria,
            marker=dict(
                size=10,
                color=color,
                line=dict(width=1, color="black")
            ),
            hovertemplate=(
                "<b>%{text}</b><br>" +
                "Rendimiento: %{y:.2f}%<br>" +
                "Inicio: %{customdata[0]}<br>" +
                "Fin: %{customdata[1]}<br>" +
                "<extra></extra>"
            ),
            text=df_cat["categoria"],
            customdata=np.stack((df_cat["md_inicio"], df_cat["md_fin"]), axis=-1)
        ))

    # Eje X con meses en español
    meses_es = ["Ene", "Feb", "Mar", "Abr", "May", "Jun",
                "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]

    fig.update_layout(
        # title=f"Estacionalidad ventanas por Categoría - {name}",
        title=dict(
            text=f"Estacionalidad ventanas por Categoría - {name}",
            font=dict(size=30, color="black"),
            x=0  # 0 = izquierda, 0.5 = centrado
        ),
        xaxis=dict(
            tickmode="array",
            tickvals=[datetime(2000, m, 1) for m in range(1, 13)],
            ticktext=meses_es
        ),
        yaxis_title="Rendimiento (%)",
        xaxis_title="Mes",
        template="simple_white",
        legend_title="Categoría",
        height=500
    )



    # fig.show()
    st.plotly_chart(fig, width="stretch")

# ---------------------------------------------------------
# 5) LLAMADA AL GRÁFICO
# ---------------------------------------------------------

grafico_estacional_plotly(df)


# **************************************************************************************************





st.header(":blue[Resumen Global]", anchor="resumen")


# %% [markdown]
# # 6.- Resumen global

# %%
df_global = df_total_backtest_ordenado[df_total_backtest_ordenado["periodo"] == "completo"]
df_global.sort_values(by=["retorno_%"],ascending=False)

# %%
df_global = df_global.sort_values("retorno_%")

df_global["color"] = df_global["retorno_%"].apply(
    lambda x: "positivo" if x >= 0 else "negativo"
)


fig = px.bar(
    df_global,
    y="name",
    x="retorno_%",
    orientation="h",
    color="color",
    color_discrete_map={
        "positivo": "green",
        "negativo": "red"
    },
    text="retorno_%",
    title="Rendimiento en los años de test",
    height=700,
    width=800
    # height=700,
    # width=1000
)

fig.update_layout(
    title=dict(
        text=f"Rendimiento todas las acciones en los años de test",
        font=dict(size=30, color="black"),
        x=0  # 0 = izquierda, 0.5 = centrado
    )
)


fig.update_traces(textposition="outside")
fig.update_yaxes(title_text=None)
fig.update_layout(showlegend=False)

# fig.show();
st.plotly_chart(fig, width="stretch")


# %%

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


input_folder = "SP500_Top25_tratados"
df_todas_rend_medio = pd.DataFrame()   # ← inicialización correcta

for name, ticker in sp500_top25.items():

    df_train = pd.read_parquet(f"{input_folder}/{name}_{ticker}_train.parquet")
    df_una_rend_medio = df_train[["rendimiento_medio"]].rename(
        columns={"rendimiento_medio": name}
    )

    if df_todas_rend_medio.empty:
        df_todas_rend_medio = df_una_rend_medio
    else:
        df_todas_rend_medio = df_todas_rend_medio.join(df_una_rend_medio, how="outer")

# display(df_todas_rend_medio)



# Matriz de correlación completa
corr = df_todas_rend_medio.corr(method="pearson")

# ORDENAR filas y columnas alfabéticamente
corr = corr.sort_index(axis=0).sort_index(axis=1)

# Crear máscara para dejar solo la triangular inferior
mask = np.triu(np.ones_like(corr, dtype=bool), k=1)

# Aplicar máscara (parte superior → NaN)
corr_lower = corr.mask(mask)

fig = px.imshow(
    corr_lower,
    text_auto=True,
    zmin=-1,
    zmax=1,
    color_continuous_scale=[
        [0.0, "yellow"],     # -1
        [0.5, "white"],    #  0
        [1.0, "blue"]       # +1
    ],
    title="Matriz de correlación (pearson)"
)

fig.update_layout(width=1200, 
                height=900,
                xaxis_title="",
                yaxis_title=""
                )

fig.update_layout(
    title=dict(
        text=f"Matriz de correlación rendimiento medio de todas las acciones",
        font=dict(size=30, color="black"),
        x=0  # 0 = izquierda, 0.5 = centrado
    )
)
# fig.show()
st.plotly_chart(fig, width="stretch")







