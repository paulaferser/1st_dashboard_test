import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Configuración
st.set_page_config(page_title="Dashboard de Ventas", layout="wide")
st.title("📊 Mi Dashboard de Ventas")

# 2. Selector de archivo (Para evitar errores de carga en GitHub)
uploaded_file = st.file_uploader("Sube tu archivo Excel o CSV para empezar", type=['csv', 'xlsx'])

if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith('.csv'):
            try:
                # El 'sep=None' detecta automáticamente si es coma, punto y coma o tabulador
                df = pd.read_csv(uploaded_file, sep=None, engine='python', encoding='utf-8')
            except UnicodeDecodeError:
                uploaded_file.seek(0)
                df = pd.read_csv(uploaded_file, sep=None, engine='python', encoding='latin1')
        else:
            # Si es Excel directo (.xlsx)
            df = pd.read_excel(uploaded_file)
            
    except Exception as e:
        st.error(f"Error técnico al abrir el archivo: {e}")
        st.info("Prueba a guardar tu Excel como 'Libro de Excel (.xlsx)' y súbelo de nuevo.")
        st.stop()

    # Limpieza básica
    df['Sum(PXC_GTV)'] = df['Sum(PXC_GTV)'].fillna(0)
    month_map = {'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6, 
                 'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12}
    if 'BK_MONTH' in df.columns:
        df['month_num'] = df['BK_MONTH'].map(month_map)

    # 3. Sidebar (Filtros)
    st.sidebar.header("Filtros")
    years = sorted(df['BK_YEAR'].unique())
    selected_years = st.sidebar.multiselect("Selecciona los Años", years, default=years[-2:])
    df_filtered = df[df['BK_YEAR'].isin(selected_years)]

    # 4. KPIs
    col1, col2, col3 = st.columns(3)
    col1.metric("Ventas Totales (GTV)", f"{df_filtered['Sum(PXC_GTV)'].sum():,.0f} €")
    col2.metric("Total Reservas", f"{df_filtered['# BK'].sum():,}")
    col3.metric("Total Pasajeros", f"{df_filtered['PAX_QTY'].sum():,}")

    # 5. Gráfico de Evolución
    st.subheader("📈 Evolución Mensual de Ventas")
    monthly_trend = df_filtered.groupby(['BK_YEAR', 'month_num', 'BK_MONTH'])['Sum(PXC_GTV)'].sum().reset_index()
    monthly_trend = monthly_trend.sort_values(['BK_YEAR', 'month_num'])
    fig_trend = px.line(monthly_trend, x='BK_MONTH', y='Sum(PXC_GTV)', color='BK_YEAR', markers=True)
    st.plotly_chart(fig_trend, use_container_width=True)

    # 6. Top Subcategorías
    st.subheader("🏆 Top Subcategorías")
    subcat_sales = df_filtered.groupby('BK_SUBCATEGORY')['Sum(PXC_GTV)'].sum().sort_values(ascending=False).head(10).reset_index()
    fig_bar = px.bar(subcat_sales, x='Sum(PXC_GTV)', y='BK_SUBCATEGORY', orientation='h', color='Sum(PXC_GTV)')
    st.plotly_chart(fig_bar, use_container_width=True)

else:
    st.info("👋 ¡Hola! Por favor, sube el archivo 'Book1.xlsx' (o su versión CSV) usando el botón de arriba para ver el análisis.")
