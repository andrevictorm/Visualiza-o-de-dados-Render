# =============================================================================
# PARTE 3: DASHBOARD INTERATIVO COM STREAMLIT
# =============================================================================
# Este dashboard exibe KPIs e gráficos interativos para o desafio técnico de e-commerce.
# Usa os CSVs e gráficos gerados na Parte 2.
# Para executar: streamlit run dashboard.py
# Data: 18/07/2025

import streamlit as st
import pandas as pd
import plotly.express as px
import os

# Configuração da página
st.set_page_config(page_title="Dashboard E-commerce", layout="wide")

# Título do dashboard
st.title("📊 Dashboard Interativo de E-commerce")
st.markdown("Análise de vendas, clientes e produtos para 2024")

# Caminho dos arquivos (ajuste para o ambiente local ou servidor)
base_path = "./Ecommerce_Dataset/"  # Substitua pelo caminho correto no seu ambiente

# Carregar CSVs
monthly_revenue = pd.read_csv(base_path + 'monthly_revenue.csv')
rfm = pd.read_csv(base_path + 'rfm_segmentation.csv')

# =============================================================================
# 1. KPIs
# =============================================================================
st.header("1. Indicadores-Chave de Desempenho (KPIs)")

col1, col2, col3 = st.columns(3)
total_revenue = monthly_revenue['total_amount'].sum()
avg_ticket = total_revenue / len(rfm)
unique_customers = len(rfm)

col1.metric("Receita Total (2024)", f"R$ {total_revenue:,.2f}")
col2.metric("Ticket Médio", f"R$ {avg_ticket:,.2f}")
col3.metric("Clientes Únicos", f"{unique_customers:,}")

# =============================================================================
# 2. Filtros
# =============================================================================
st.header("2. Filtros")
months = monthly_revenue['order_date'].tolist()
selected_months = st.multiselect("Selecione os meses", months, default=months)

# Filtrar dados por meses selecionados
filtered_revenue = monthly_revenue[monthly_revenue['order_date'].isin(selected_months)]

# =============================================================================
# 3. Gráficos
# =============================================================================
st.header("3. Visualizações")

# 3.1. Tendência de Receita Mensal
st.subheader("Tendência de Receita Mensal")
fig_revenue = px.line(filtered_revenue, x='order_date', y='total_amount',
                      title="Receita Mensal (2024)", markers=True)
fig_revenue.update_layout(xaxis_title="Mês", yaxis_title="Receita (R$)")
st.plotly_chart(fig_revenue, use_container_width=True)

# 3.2. Distribuição de Segmentos RFM
st.subheader("Distribuição de Segmentos de Clientes (RFM)")
fig_rfm = px.histogram(rfm, x='segment', category_orders={"segment": ["VIP", "Regular", "Ocasional", "Inativo"]},
                       title="Segmentação de Clientes")
fig_rfm.update_layout(xaxis_title="Segmento", yaxis_title="Contagem de Clientes")
st.plotly_chart(fig_rfm, use_container_width=True)

# 3.3. Imagens geradas na Parte 2
st.subheader("Outras Visualizações")
st.image(base_path + 'price_distribution_by_category.png', caption="Distribuição de Preços por Categoria")
st.image(base_path + 'monthly_unique_customers.png', caption="Clientes Únicos por Mês")
