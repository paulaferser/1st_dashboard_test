import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Configuración de la página
st.set_page_config(page_title="Dashboard de Ventas", layout="wide")
st.title("📊 Análisis de Ventas 2019 - 2026")

# 2. Cargar los datos (El archivo que subiste)
@st.cache_data
def load_data():
   df = pd.read_csv('Book1.xlsx - Sheet1 (1).csv')
    df['Sum(PXC_GTV)'] = df['Sum(PXC_GTV)'].fillna(0)
    # Ordenar meses cronológicamente
    month_map = {'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6, 
                 'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12}
    df['month_num'] = df['BK_MONTH'].map(month_map)
    return df

df = load_data()

# 3. Sidebar (Filtros)
st.sidebar.header("Filtros")
years = sorted(df['BK_YEAR'].unique())
selected_years = st.sidebar.multiselect("Selecciona los Años", years, default=years[-2:])

# Filtrar datos
mask = df['BK_YEAR'].isin(selected_years)
df_filtered = df[mask]

# 4. KPIs Principales
col1, col2, col3 = st.columns(3)
total_gtv = df_filtered['Sum(PXC_GTV)'].sum()
total_bk = df_filtered['# BK'].sum()
total_pax = df_filtered['PAX_QTY'].sum()

col1.metric("Ventas Totales (GTV)", f"{total_gtv:,.0f} €")
col2.metric("Total Reservas", f"{total_bk:,}")
col3.metric("Total Pasajeros", f"{total_pax:,}")

# 5. Gráfico de Evolución Temporal
st.subheader("📈 Evolución Mensual de Ventas")
monthly_trend = df_filtered.groupby(['BK_YEAR', 'month_num', 'BK_MONTH'])['Sum(PXC_GTV)'].sum().reset_index()
monthly_trend = monthly_trend.sort_values(['BK_YEAR', 'month_num'])

fig_trend = px.line(monthly_trend, x='BK_MONTH', y='Sum(PXC_GTV)', color='BK_YEAR',
                  labels={'Sum(PXC_GTV)': 'Ventas', 'BK_MONTH': 'Mes'},
                  markers=True, template="plotly_white")
st.plotly_chart(fig_trend, use_container_width=True)

# 6. Gráfico de Subcategorías (Pareto)
st.subheader("🏆 Top Subcategorías por Ventas")
subcat_sales = df_filtered.groupby('BK_SUBCATEGORY')['Sum(PXC_GTV)'].sum().sort_values(ascending=False).head(10).reset_index()

fig_bar = px.bar(subcat_sales, x='Sum(PXC_GTV)', y='BK_SUBCATEGORY', orientation='h',
                 color='Sum(PXC_GTV)', color_continuous_scale='Viridis',
                 labels={'Sum(PXC_GTV)': 'Ventas', 'BK_SUBCATEGORY': 'Categoría'})
st.plotly_chart(fig_bar, use_container_width=True)
