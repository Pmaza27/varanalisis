import pandas as pd
import streamlit as st
import numpy as np
from datetime import datetime

# --- Configuración de la Página Mejorada ---
st.set_page_config(
    page_title="Análisis de Sensores - Mi Ciudad",
    page_icon="🏙️", # Nuevo ícono más relevante
    layout="wide", # Usa todo el ancho disponible
    initial_sidebar_state="expanded" # Expande la barra lateral por defecto
)

# --- Custom CSS para Estilo Moderno ---
st.markdown("""
    <style>
    /* Fondo principal y espaciado */
    .stApp {
        background-color: #f0f2f6; /* Un color de fondo suave */
        color: #1c1f24;
    }
    /* Estilo del título principal */
    .stApp > header {
        background-color: #0e1117; 
        padding: 0.5rem 0 0.5rem 1rem;
    }
    /* Contenedor principal con sombra */
    .stMarkdown.main {
        padding: 2rem;
        border-radius: 10px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        background-color: white;
    }
    /* Estilo para st.metric (más grande y con color) */
    [data-testid="stMetricValue"] {
        font-size: 2.5rem;
        color: #26b3a0; /* Color de acento (verde azulado) */
    }
    /* Estilo para el botón de descarga */
    .stDownloadButton > button {
        background-color: #007bff; /* Azul primario */
        color: white;
        border-radius: 5px;
        padding: 0.5rem 1rem;
    }
    /* Encabezados de pestaña */
    .stTabs [data-testid="stMarkdownContainer"] {
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# --- Sidebar para Controles Principales ---
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/e/e0/Universidad_EAFIT_logo.svg", width=150)
    st.title("⚙️ Controles de Datos")
    
    # Carga de Archivo
    uploaded_file = st.file_uploader('1. Seleccione archivo CSV', type=['csv'])
    st.info("💡 Consejo: Su archivo debe contener al menos una columna de tiempo (opcional) y una columna numérica de datos de sensor.")
    
# --- Título e Información General ---
st.title('📈 Análisis Interactivo de Sensores Urbanos')
st.markdown("Bienvenido al panel de control. Utilice la barra lateral para cargar datos y las pestañas para el análisis detallado.")
st.markdown("---")

# --- Ubicación del Sensor (Mantenida por su relevancia) ---
eafit_location = pd.DataFrame({
    'lat': [6.2006],
    'lon': [-75.5783],
    'location': ['Universidad EAFIT']
})
st.subheader("📍 Ubicación de Referencia (EAFIT)")
st.map(eafit_location, zoom=15)
st.markdown("---")

# --- Bloque de Procesamiento de Datos ---
df1 = None # Inicializar df1

if uploaded_file is not None:
    try:
        df_original = pd.read_csv(uploaded_file)
        df1 = df_original.copy()
        
        # --- Controles de Columna en la Sidebar (para mantener limpio el main) ---
        with st.sidebar:
            st.subheader("2. Selección de Columnas")
            
            # 1. Seleccionar columna de tiempo
            time_col_options = ['(Sin Columna de Tiempo)'] + list(df1.columns)
            time_col = st.selectbox(
                "Columna de **Tiempo (Time)**",
                time_col_options,
                index=df1.columns.get_loc('Time') + 1 if 'Time' in df1.columns else 0
            )

            # 2. Seleccionar columna de variable de análisis
            variable_col = st.selectbox(
                "Columna de **Variable a Analizar**",
                df1.columns,
                index=1 if len(df1.columns) > 1 and df1.columns[0] == time_col else 0
            )
            
        # --- Procesamiento (El mismo robusto que antes) ---
        if time_col != '(Sin Columna de Tiempo)':
            df1[time_col] = pd.to_datetime(df1[time_col], errors='coerce')
            df1 = df1.rename(columns={time_col: 'Time'}).set_index('Time').sort_index()
            df1.dropna(subset=['Time'], inplace=True)
            
        if variable_col != 'variable':
             df1 = df1.rename(columns={variable_col: 'variable'})

        df1['variable'] = pd.to_numeric(df1['variable'], errors='coerce')
        df1.dropna(subset=['variable'], inplace=True)

        if df1.empty:
            st.error("⚠️ El DataFrame está vacío o no contiene datos numéricos válidos después del filtrado.")
            st.stop()
        
        # --- Creación de Pestañas con Emojis ---
        tab1, tab2, tab3, tab4 = st.tabs(["📊 Visualización General", "📈 Estadísticas Clave", "⚙️ Filtros y Descarga", "ℹ️ Detalles del Sitio"])

        # ==================================
        # 1. Pestaña de Visualización General
        # ==================================
        with tab1:
            st.header('Gráfico de la Variable Seleccionada')
            
            col_chart, col_raw = st.columns([3, 1])
            
            with col_raw:
                chart_type = st.radio(
                    "Tipo de Gráfico",
                    ["Línea", "Área", "Barra"],
                    index=0,
                    horizontal=True
                )
            
            with col_chart:
                if chart_type == "Línea":
                    st.line_chart(df1["variable"])
                elif chart_type == "Área":
                    st.area_chart(df1["variable"])
                else:
                    st.bar_chart(df1["variable"])
                    
            if st.checkbox('Mostrar primeras filas del DataFrame (Datos Limpios)', value=False):
                st.dataframe(df1.head(10), use_container_width=True)

        # ==================================
        # 2. Pestaña de Estadística Clave
        # ==================================
        with tab2:
            st.header('Resumen y Métricas Rápidas')
            
            stats_df = df1["variable"].describe().to_frame().round(3)
            
            # --- Diseño de Métricas en Tres Columnas ---
            
            col_mean, col_max, col_min, col_std = st.columns(4)
            
            # Aseguramos que los valores existan antes de acceder
            mean_val = stats_df.loc['mean'].iloc[0]
            max_val = stats_df.loc['max'].iloc[0]
            min_val = stats_df.loc['min'].iloc[0]
            std_val = stats_df.loc['std'].iloc[0]
            
            col_mean.metric("Promedio (Media)", f"{mean_val:,.2f}")
            col_max.metric("Máximo Absoluto", f"{max_val:,.2f}")
            col_min.metric("Mínimo Absoluto", f"{min_val:,.2f}")
            col_std.metric("Desviación Estándar", f"{std_val:,.2f}")
            
            st.markdown("---")
            st.subheader("Tabla de Resumen Estadístico")
            st.dataframe(stats_df, use_container_width=True)

        # ==================================
        # 3. Pestaña de Filtros y Descarga
        # ==================================
        with tab3:
            st.header('Filtros de Datos por Rango')
            
            min_data_value = float(df1["variable"].min())
            max_data_value = float(df1["variable"].max())
            
            if min_data_value == max_data_value:
                st.warning(f"⚠️ Todos los valores son iguales: {min_data_value:.2f}. No se puede aplicar filtro de rango.")
                st.dataframe(df1)
            else:
                col_slider, col_info = st.columns([3, 1])
                
                with col_slider:
                    # Usar un slider de rango para simplificar la interfaz
                    range_values = st.slider(
                        'Seleccione el Rango Mínimo y Máximo de Valores',
                        min_data_value,
                        max_data_value,
                        (min_data_value, max_data_value),
                        key="range_val_ui",
                        format="%.2f"
                    )
                
                min_f, max_f = range_values
                
                # Aplicar filtro
                filtrado_df = df1[(df1["variable"] >= min_f) & (df1["variable"] <= max_f)]
                
                with col_info:
                    st.metric("Registros Filtrados", f"{len(filtrado_df)}", delta=f"{len(df1) - len(filtrado_df)} excluidos")
                
                st.markdown("---")
                st.subheader("Vista Previa de Datos Filtrados")
                st.caption(f"Mostrando {len(filtrado_df)} de {len(df1)} registros en el rango **[{min_f:.2f}, {max_f:.2f}]**.")
                st.dataframe(filtrado_df, use_container_width=True)
                
                # Botón de Descarga
                csv = filtrado_df.to_csv().encode('utf-8')
                st.download_button(
                    label="💾 Descargar Datos Filtrados (CSV)",
                    data=csv,
                    file_name=f'datos_filtrados_{variable_col}_{datetime.now().strftime("%Y%m%d")}.csv',
                    mime='text/csv',
                    key='download_btn_ui'
                )
        
        # ==================================
        # 4. Pestaña de Información
        # ==================================
        with tab4:
            st.header("Información del Sitio de Medición")
            
            col_site, col_details = st.columns(2)
            
            with col_site:
                st.subheader("Ubicación")
                st.markdown(f"""
                - **Sitio:** Universidad EAFIT
                - **Latitud:** `{eafit_location['lat'].iloc[0]}`
                - **Longitud:** `{eafit_location['lon'].iloc[0]}`
                - **Altitud:** ~1,495 metros sobre el nivel del mar
                """)
            
            with col_details:
                st.subheader("Detalles del Sensor y Datos")
                st.markdown(f"""
                - **Tipo de Sensor:** ESP32 (Referencial)
                - **Variable Analizada:** **{variable_col}**
                - **Registros Totales:** `{len(df1)}`
                - **Rango de Tiempo:** De **{df1.index.min().strftime('%Y-%m-%d %H:%M')}** a **{df1.index.max().strftime('%Y-%m-%d %H:%M')}**
                """)


    except Exception as e:
        st.error(f'❌ Error crítico al procesar el archivo: {str(e)}')
        st.info('Asegúrese de que el archivo CSV esté bien formado y que haya seleccionado las columnas correctas en el panel lateral.')
else:
    st.info('👆 Por favor, cargue un archivo CSV desde la barra lateral izquierda para comenzar el análisis.')
    
# --- Footer ---
st.markdown("---")
st.markdown("""
    <div style='text-align: center; font-size: small; color: gray;'>
        Aplicación de Análisis de Sensores Urbanos | Desarrollado para EAFIT
    </div>
""", unsafe_allow_html=True)
