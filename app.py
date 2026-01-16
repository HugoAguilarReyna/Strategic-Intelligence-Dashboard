import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
from datetime import datetime

# --- 1. CONFIGURACIÓN Y ESTILO UNIFICADO (PhD STYLE) ---
st.set_page_config(page_title="Strategic Intelligence | PhD Suite", layout="wide", page_icon="⚖️")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700&family=JetBrains+Mono:wght@500;800&display=swap');
    
    .main { background-color: #0d1117; }
    
/* Títulos de sección estilo terminal científica - VERSION AGRANDADA */
    .section-header {
        color: #58a6ff;
        font-family: 'JetBrains Mono', monospace;
        font-size: 1.5rem; /* Antes era 0.85rem */
        font-weight: 800;  /* Negrita extrema */
        letter-spacing: 2px;
        text-transform: uppercase;
        margin: 45px 0 25px 0;
        border-left: 6px solid #58a6ff; /* Borde más grueso para el título más grande */
        padding-left: 15px;
    }

    /* CONTENEDOR UNIFICADO (Basado en tu Imagen 4) */
    .stat-container {
        margin-bottom: 30px;
        padding: 10px 0;
    }
    .stat-label {
        color: #ffffff;
        font-family: 'Inter', sans-serif;
        font-size: 0.95rem;
        font-weight: 400;
        margin-bottom: 8px;
    }
    .stat-value {
        font-family: 'Inter', sans-serif;
        font-size: 2.5rem; 
        font-weight: 700;
        line-height: 1;
    }
    .stat-delta {
        color: #39d353;
        font-family: 'Inter', sans-serif;
        font-size: 0.85rem;
        margin-top: 6px;
        display: flex;
        align-items: center;
        gap: 5px;
        font-weight: 500;
    }

    /* Ajustes de tablas */
    .stDataFrame { border: 1px solid #30363d; border-radius: 4px; }
    
    hr { border-top: 1px solid #30363d; margin: 2rem 0; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. MOTOR DE CARGA Y FILTROS ---
@st.cache_data
def load_data():
    # Usamos Path.cwd() para asegurar que partimos de la raíz del proyecto en Render
    base_path = Path.cwd() / "Data"  # Corregido a "Data" con D mayúscula para match con GitHub
    archivo_path = base_path / "data_gold_main.csv"
    
    if not archivo_path.exists():
        # Mensaje de error más técnico para debuguear en Render
        st.error(f"❌ Error Crítico: No se encontró {archivo_path.name} en {base_path}")
        st.info("Asegúrate de que la carpeta 'Data' esté en la raíz de tu repositorio.")
        st.stop()
        
    df = pd.read_csv(archivo_path)
    
    # --- Limpieza PhD Suite ---
    df.columns = [col.lower().strip() for col in df.columns]
    df['total'] = pd.to_numeric(df['total'], errors='coerce').fillna(0)
    df['fecha_timbrado'] = pd.to_datetime(df['fecha_timbrado'], errors='coerce')
    df['nombre'] = df['nombre'].fillna("N/A")
    df['tipo'] = df['tipo'].fillna("I").str.upper()
    df['estatus'] = df['estatus'].fillna("vigente")
    df['metodo_pago'] = df['metodo_pago'].fillna("PUE")
    
    return df.dropna(subset=['fecha_timbrado'])

df_raw = load_data()

with st.sidebar:
    st.title("🎛️ Control Panel")
    min_d, max_d = df_raw['fecha_timbrado'].min().date(), df_raw['fecha_timbrado'].max().date()
    rango = st.date_input("Rango Temporal", [min_d, max_d])
    start_date, end_date = (rango[0], rango[1]) if len(rango) == 2 else (rango[0], rango[0])
    
    clientes = st.multiselect("Entidades", sorted(df_raw['nombre'].unique()))
    estatus_list = st.multiselect("Estatus", df_raw['estatus'].unique(), default=df_raw['estatus'].unique())

# Aplicación de filtros
mask = (df_raw['fecha_timbrado'].dt.date >= start_date) & \
       (df_raw['fecha_timbrado'].dt.date <= end_date) & \
       (df_raw['estatus'].isin(estatus_list))

df_f = df_raw.loc[mask].copy()
if clientes:
    df_f = df_f[df_f['nombre'].isin(clientes)]

# --- 3. LÓGICA DE RENDERIZADO UNIFICADA ---
def render_stat_element(label, value, delta, color="#ffffff"):
    st.markdown(f"""
        <div class="stat-container">
            <div class="stat-label">{label}</div>
            <div class="stat-value" style="color: {color};">{value}</div>
            <div class="stat-delta">↑ {delta}</div>
        </div>
    """, unsafe_allow_html=True)

# --- HEADER PRINCIPAL ---
st.markdown("<h1 style='text-align: center;'>Strategic Intelligence Dashboard</h1>", unsafe_allow_html=True)
st.markdown(f"""
    <div style='text-align: center; margin-bottom: 40px;'>
        <code style='color:#8b949e; font-size: 1.1rem;'>
            ANÁLISIS FORENSE: {start_date} AL {end_date}
        </code>
    </div>
""", unsafe_allow_html=True)
# --- SECCIÓN 1: VOLUMETRÍA Y SECCIÓN 2: ESTADÍSTICA (MISMO NIVEL VISUAL) ---
st.markdown("<div class='section-header'>Volumetría y Control Operativo</div>", unsafe_allow_html=True)

ing = df_f[df_f['tipo'] == 'I']['total'].sum()
egr = df_f[df_f['tipo'] == 'E']['total'].sum()
vol = len(df_f)
avg = df_f['total'].mean() if vol > 0 else 0

v1, v2, v3, v4 = st.columns(4)
with v1: render_stat_element("Volumen CFDI", f"{vol:,}", "Total Transacciones", "#58a6ff")
with v2: render_stat_element("Ingresos", f"${ing:,.2f}", "Net Inflow", "#39d353")
with v3: render_stat_element("Egresos", f"${egr:,.2f}", "Net Outflow", "#f85149")
with v4: render_stat_element("Balance", f"${ing - egr:,.2f}", "Net Liquidity", "#ffffff")

# LÍNEA DIVISORIA
st.markdown("<hr class='custom-hr'>", unsafe_allow_html=True)

st.markdown("<div class='section-header'>Inteligencia Estadística y Distribución</div>", unsafe_allow_html=True)

s1, s2, s3, s4 = st.columns(4)
with s1: render_stat_element("Monto Máximo", f"${df_f['total'].max():,.2f}", "Peak Value")
with s2: render_stat_element("Desviación Est.", f"${df_f['total'].std():,.2f}", "Sigma Variance")
with s3: render_stat_element("Rango Operativo", f"${df_f['total'].max() - df_f['total'].min():,.2f}", "Full Spread")
with s4: render_stat_element("Promedio", f"${avg:,.2f}", "Mean Density")

# LÍNEA DIVISORIA
st.markdown("<hr class='custom-hr'>", unsafe_allow_html=True)

# --- SECCIÓN: ANÁLISIS DE SEGMENTACIÓN POR QUINTILES (VERSIÓN ULTRA-IMPACT) ---
st.markdown("<div class='section-header'>Segmentación y Concentración de Capital</div>", unsafe_allow_html=True)

with st.container():
    if not df_f.empty:
        # 1. Cálculo de Quintiles
        q_vals = df_f['total'].quantile([0.2, 0.4, 0.6, 0.8]).values
        
        # 2. CSS personalizado para títulos y valores gigantes
        st.markdown("""
            <style>
            .q-container {
                display: flex;
                justify-content: space-between;
                gap: 15px;
                margin-bottom: 25px;
            }
            .q-card {
                flex: 1;
                background: rgba(88, 166, 255, 0.05);
                border: 1px solid #30363d;
                border-radius: 12px;
                padding: 25px 10px;
                text-align: center;
                transition: transform 0.3s;
            }
            .q-card:hover {
                border-color: #58a6ff;
                background: rgba(88, 166, 255, 0.1);
            }
            .q-header {
                color: #58a6ff; /* Cambiado a azul para resaltar más */
                font-family: 'Inter', sans-serif;
                font-size: 1.1rem; /* Título más grande */
                font-weight: 800;  /* Negrita extrema */
                text-transform: uppercase;
                margin-bottom: 12px;
                letter-spacing: 1px;
            }
            .q-value {
                color: #ffffff;
                font-family: 'JetBrains Mono', monospace; /* Fuente técnica */
                font-size: 2.2rem; /* Valor mucho más grande */
                font-weight: 800;  /* Negrita extrema */
                line-height: 1;
            }
            </style>
        """, unsafe_allow_html=True)

        # Renderizado de Tarjetas
        st.markdown(f"""
            <div class="q-container">
                <div class="q-card">
                    <div class="q-header">Q1 (Umbral 20%)</div>
                    <div class="q-value">${q_vals[0]:,.2f}</div>
                </div>
                <div class="q-card">
                    <div class="q-header">Q2 (Umbral 40%)</div>
                    <div class="q-value">${q_vals[1]:,.2f}</div>
                </div>
                <div class="q-card">
                    <div class="q-header">Q3 (Umbral 60%)</div>
                    <div class="q-value">${q_vals[2]:,.2f}</div>
                </div>
                <div class="q-card">
                    <div class="q-header">Q4 (Umbral 80%)</div>
                    <div class="q-value">${q_vals[3]:,.2f}</div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        # 3. Gráfico de Concentración
        df_f['quintil'] = pd.qcut(df_f['total'], 5, labels=['Q1 (Bajo)', 'Q2', 'Q3', 'Q4', 'Q5 (Alto)'])
        q_dist = df_f.groupby('quintil', observed=False)['total'].agg(['sum']).reset_index()
        q_dist['porcentaje'] = (q_dist['sum'] / q_dist['sum'].sum()) * 100

        fig_q = px.bar(
            q_dist, x='quintil', y='sum',
            text=q_dist['porcentaje'].apply(lambda x: f'{x:.1f}%'),
            color='sum', template="plotly_dark",
            color_continuous_scale='Blues'
        )
        fig_q.update_layout(
            height=400, 
            showlegend=False, 
            coloraxis_showscale=False,
            title="Distribución de Masa Monetaria por Quintil",
            margin=dict(l=0, r=0, t=50, b=0), 
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig_q, use_container_width=True)
        
    else:
        st.info("Sin datos suficientes para segmentación.")
        
# --- 4. GRÁFICAS (UNA DEBAJO DE LA OTRA) ---
st.divider()

# --- Gráfico 1: Dinámica Temporal OPTIMIZADO (¡Impactante!) ---
st.markdown("<div class='section-header'>Volumetría y Control Operativo</div>", unsafe_allow_html=True)

# Preparamos los datos semanalmente
df_w = df_f.set_index('fecha_timbrado').resample('W')['total'].sum().reset_index()

# Creamos la gráfica de área con mejoras visuales
fig_area = px.area(
    df_w, 
    x='fecha_timbrado', 
    y='total', 
    template="plotly_dark",
    title="Análisis Semanal del Capital Operado",
    labels={'fecha_timbrado': 'Periodo Semanal', 'total': 'Monto Total ($)'}
)

# Refinamiento visual avanzado
fig_area.update_traces(
    mode='lines+markers+text',  # Líneas, marcadores y TEXTO en cada punto
    line_color='#58a6ff',      # Color de la línea (azul de la marca PhD)
    fillcolor='rgba(88, 166, 255, 0.15)', # Relleno con más opacidad
    marker=dict(size=8, color='#58a6ff', line=dict(width=2, color='#ffffff')), # Marcadores claros
    text=df_w['total'].apply(lambda x: f'${x:,.0f}'), # Texto con formato monetario sin decimales
    textposition="top center", # Posición del texto encima de los puntos
    textfont=dict(size=12, color='#ffffff') # Estilo del texto
)

fig_area.update_layout(
    height=550, # Aumentamos un poco más la altura para mayor impacto
    margin=dict(l=0, r=0, t=50, b=0), # Ajustamos márgenes
    hovermode="x unified", # Hover que unifica información en el eje X
    xaxis_title=None, # Quitamos título del eje X, ya está en el subtítulo
    yaxis_title=None, # Quitamos título del eje Y, ya está en el subtítulo
    xaxis=dict(
        showgrid=False, # Eliminamos cuadrícula para un look más limpio
        tickfont=dict(size=10, color='#8b949e'),
        rangeslider_visible=False # Puedes activar esto si quieres un rango de tiempo interactivo
    ),
    yaxis=dict(
        showgrid=True, 
        gridcolor='#30363d', # Color de la cuadrícula más tenue
        tickfont=dict(size=10, color='#8b949e')
    ),
    plot_bgcolor='rgba(0,0,0,0)', # Fondo transparente
    paper_bgcolor='rgba(0,0,0,0)', # Fondo transparente del papel
    title=dict(
        font=dict(size=24, color='#ffffff', family='Inter, sans-serif'), # Título más grande
        x=0.01 # Posición del título
    )
)

st.plotly_chart(fig_area, use_container_width=True)


# LÍNEA DIVISORIA
st.markdown("<hr class='custom-hr'>", unsafe_allow_html=True)

# --- Gráfico 2: Concentración Top 5 OPTIMIZADO ---
st.markdown("<div class='section-header'>RANKING ESTRATÉGICO: TOP 5 ENTIDADES</div>", unsafe_allow_html=True)

# 1. Obtener los 5 más grandes
top5 = df_f.groupby('nombre')['total'].sum().nlargest(5).reset_index()

top5 = top5.sort_values('total', ascending=False) 

# Creación de la gráfica
fig_top5 = px.bar(
    top5, 
    x='total', 
    y='nombre', 
    orientation='h',
    color='total',
    template="plotly_dark",
    color_continuous_scale="Blues",
    text=top5['total'].apply(lambda x: f' ${x:,.2f} ')
)

# Estilo PhD Premium
fig_top5.update_traces(
    textposition='inside', 
    textfont=dict(size=14, family='JetBrains Mono', color='white'),
    marker=dict(line=dict(width=0)),
    hovertemplate='<b>%{y}</b><br>Total Operado: %{text}<extra></extra>'
)

fig_top5.update_layout(
    height=450,
    showlegend=False,
    coloraxis_showscale=False,
    xaxis_visible=False, # Mantiene el look limpio sin ejes
    yaxis_title=None,
    margin=dict(l=0, r=10, t=30, b=0),
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    yaxis=dict(
        tickfont=dict(size=14, family='Inter', color='#ffffff'),
        # Al estar el dataframe de menor a mayor, 'reversed' pone el último (el mayor) arriba
        autorange="reversed" 
    )
)

st.plotly_chart(fig_top5, use_container_width=True)

# --- Gráfico 1: Sunburst OPTIMIZADO CON LEYENDA (COLORBAR) A LA DERECHA ---
st.markdown("<div class='section-header'>Análisis de Riesgo Estructural</div>", unsafe_allow_html=True)


fig_sun = px.sunburst(
    df_f, 
    path=['metodo_pago', 'estatus'], 
    values='total',
    color='total',
    color_continuous_scale='Reds', 
    template="plotly_dark",
    title="Jerarquía de Riesgo: Método de Pago vs. Estatus"
)

fig_sun.update_traces(
    textinfo="label+percent entry", 
    textfont_size=18, # Texto dentro del gráfico más legible
    hovertemplate='<b>%{label}</b><br>Monto: $%{value:,.2f}<br>Propio: %{percentParent:.2f}%'
)

fig_sun.update_layout(
    font=dict(weight="bold"), # Aplica peso a las fuentes del layout
    height=650, # Un poco más de altura para lucir la jerarquía
    margin=dict(t=50, l=0, r=150, b=50), # Margen derecho amplio para la leyenda
    
    # Configuración de la Barra de Color (Leyenda de Riesgo)
    coloraxis_showscale=True,
    coloraxis_colorbar=dict(
        title="Monto Riesgo",
        title_font_size=16,
        thicknessmode="pixels", thickness=20,
        lenmode="fraction", len=0.8,
        yanchor="middle", y=0.5,
        xanchor="left", x=1.1, # Posición a la derecha
        tickfont=dict(size=14, family="JetBrains Mono", color="white"),
        tickformat="$,.0f" # Formato moneda en los ticks
    )
)

st.plotly_chart(fig_sun, use_container_width=True)

# LÍNEA DIVISORIA
st.markdown("<hr class='custom-hr'>", unsafe_allow_html=True)

# --- Gráfico 2: Pie (Donut) OPTIMIZADO CON TEXTOS GRANDES ---
st.markdown("<div class='section-header'>Composición de Cartera por Tipo</div>", unsafe_allow_html=True)

# Mapeo de nombres para mayor claridad
df_f['tipo_label'] = df_f['tipo'].map({
    'I': 'Ingresos (I)', 
    'E': 'Egresos (E)', 
    'T': 'Traslados (T)'
}).fillna(df_f['tipo'])

fig_pie = px.pie(
    df_f, 
    names='tipo_label', 
    values='total', 
    hole=0.6, 
    template="plotly_dark",
    color_discrete_sequence=px.colors.qualitative.Pastel,
    title="Distribución Operativa de CFDI"
)

fig_pie.update_traces(
    textposition='outside', 
    # Aumentamos el tamaño de la fuente de las etiquetas en el gráfico
    textfont_size=16,
    textinfo='percent+label',
    marker=dict(line=dict(color='#0d1117', width=2)),
    pull=[0.05, 0, 0]
)

fig_pie.update_layout(
    height=550, # Aumentamos un poco el alto para dar espacio a los textos grandes
    showlegend=True,
    # --- LEYENDA A LA DERECHA CON TEXTOS GRANDES ---
    legend=dict(
        orientation="v",
        yanchor="middle",
        y=0.5,
        xanchor="left",
        x=1.1,
        font=dict(
            family="Inter, sans-serif",
            size=18, # Texto de la leyenda más grande
            color="white"
        ),
        bgcolor="rgba(0,0,0,0)", # Fondo transparente
    ),
    # Aumentamos el margen derecho para que el texto grande no se corte
    margin=dict(t=80, l=0, r=150, b=0) 
)

st.plotly_chart(fig_pie, use_container_width=True)

# LÍNEA DIVISORIA
st.markdown("<hr class='custom-hr'>", unsafe_allow_html=True)

# Gráfico 3: Bar (Top 10)
st.markdown("<div class='section-header'>Análisis de Concentración: Top 10 Clientes</div>", unsafe_allow_html=True)



# Preparamos los datos
top10 = df_f.groupby('nombre')['total'].sum().nlargest(10).reset_index()
top10 = top10.sort_values('total', ascending=True) # Para que el más alto quede arriba en la gráfica horizontal

# Creamos la gráfica con esteroides visuales
fig_top10 = px.bar(
    top10, 
    x='total', 
    y='nombre', 
    orientation='h',
    color='total',
    text_auto=',.2f', # Añade los montos automáticamente sobre las barras
    title="Top 10 Clientes por Volumen Monetario",
    template="plotly_dark",
    color_continuous_scale='GnBu' # Escala de color profesional (Verde-Azul)
)

# Refinamiento estético profundo
fig_top10.update_traces(
    textfont_size=12, 
    textangle=0, 
    textposition="outside", 
    cliponaxis=False
)

fig_top10.update_layout(
    height=500,
    showlegend=False,
    coloraxis_showscale=False, # Ocultamos la barra de escala para máxima limpieza
    yaxis_title=None,
    xaxis_title="Monto Total Operado",
    margin=dict(l=0, r=50, t=40, b=0), # Margen derecho extra para las etiquetas
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    xaxis=dict(showgrid=False, zeroline=False) # Eliminamos el ruido del fondo
)

st.plotly_chart(fig_top10, use_container_width=True)

# --- 6. OUTLIERS Y AUDITORÍA ---
st.divider()

st.markdown("<div class='section-header'>Detección Visual de Outliers</div>", unsafe_allow_html=True)

st.plotly_chart(px.scatter(df_f, x="fecha_timbrado", y="total", color="total", size="total", 
                           hover_name="nombre", template="plotly_dark", color_continuous_scale="Reds"), use_container_width=True)

# --- 7. EXPLORADOR DE DATOS Y EXPORTACIÓN ---
st.divider()
df_f['fecha_simple'] = df_f['fecha_timbrado'].dt.date
dups = df_f[df_f.duplicated(subset=['nombre', 'total', 'fecha_simple'], keep=False)]

col_aud, col_btn = st.columns([7, 3])
with col_aud:
    if not dups.empty: st.warning(f"⚠️ Se detectaron {len(dups)} registros duplicados en el set actual.")
    else: st.success("✅ No se detectaron duplicados obvios.")

with col_btn:
    csv_data = df_f.to_csv(index=False).encode('utf-8')
    st.download_button("📥 DESCARGAR REPORTE FULL (CSV)", csv_data, 
                       f"Reporte_{datetime.now().strftime('%Y%m%d')}.csv", "text/csv")


st.markdown("<div class='section-header'>Explorador Detallado</div>", unsafe_allow_html=True)

cols_view = [c for c in ['uuid', 'folio', 'fecha_timbrado', 'nombre', 'total', 'metodo_pago', 'estatus'] if c in df_f.columns]

st.dataframe(df_f[cols_view].sort_values(by='total', ascending=False), use_container_width=True)
