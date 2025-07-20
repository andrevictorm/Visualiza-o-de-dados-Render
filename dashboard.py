# =============================================================================
# PARTE 3: DASHBOARD INTERATIVO COM STREAMLIT
# =============================================================================
# Este dashboard exibe KPIs e gráficos interativos para o desafio técnico de e-commerce.
# Inclui KPIs (receita, ticket médio, clientes únicos/totais, pedidos, taxa de conversão),
# gráficos (receita mensal, top produtos, receita por categoria, status de pedidos, RFM, pedidos totais)
# e filtros (meses, categoria, status de pedido).
# Para executar: streamlit run dashboard.py
# Data: 20/07/2025

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
@st.cache_data
def load_data():
    monthly_revenue = pd.read_csv(base_path + 'monthly_revenue.csv')
    rfm = pd.read_csv(base_path + 'rfm_segmentation.csv')
    orders = pd.read_csv(base_path + 'orders.csv')
    order_items = pd.read_csv(base_path + 'order_items.csv')
    products = pd.read_csv(base_path + 'products.csv')
    orders['order_date'] = pd.to_datetime(orders['order_date'])
    return monthly_revenue, rfm, orders, order_items, products

monthly_revenue, rfm, orders, order_items, products = load_data()

# Calcular top 5 produtos por receita
top_products = order_items.merge(orders[orders['status'] == 'Entregue'], on='order_id') \
                         .merge(products, on='product_id') \
                         .groupby(['product_id', 'product_name', 'category']) \
                         .agg({'quantity': 'sum', 'unit_price': 'sum'}) \
                         .assign(total_revenue=lambda x: x['quantity'] * x['unit_price']) \
                         .reset_index()[['product_name', 'category', 'total_revenue']] \
                         .sort_values('total_revenue', ascending=False) \
                         .head(5)

# Calcular receita por categoria
revenue_by_category = order_items.merge(orders[orders['status'] == 'Entregue'], on='order_id') \
                                .merge(products, on='product_id') \
                                .groupby('category') \
                                .agg({'quantity': 'sum', 'unit_price': 'sum'}) \
                                .assign(total_revenue=lambda x: x['quantity'] * x['unit_price']) \
                                .reset_index()[['category', 'total_revenue']]

# =============================================================================
# 1. Filtros
# =============================================================================
st.header("1. Filtros")
col1, col2, col3 = st.columns(3)

with col1:
    months = monthly_revenue['order_date'].tolist()
    selected_months = st.multiselect("Selecione os meses", months, default=months)

with col2:
    categories = products['category'].unique().tolist()
    selected_categories = st.multiselect("Selecione as categorias", categories, default=categories)

with col3:
    statuses = orders['status'].unique().tolist()
    selected_statuses = st.multiselect("Selecione os status de pedido", statuses, default=['Entregue'])

# Filtrar dados
filtered_orders = orders[orders['order_date'].dt.strftime('%Y-%m').isin(selected_months) & 
                        orders['status'].isin(selected_statuses)]
filtered_order_items = order_items[order_items['order_id'].isin(filtered_orders['order_id'])]
filtered_products = products[products['category'].isin(selected_categories)]
filtered_order_items = filtered_order_items[filtered_order_items['product_id'].isin(filtered_products['product_id'])]
filtered_revenue = monthly_revenue[monthly_revenue['order_date'].isin(selected_months)]
filtered_top_products = filtered_order_items.merge(filtered_orders, on='order_id') \
                                           .merge(filtered_products, on='product_id') \
                                           .groupby(['product_name', 'category']) \
                                           .agg({'quantity': 'sum', 'unit_price': 'sum'}) \
                                           .assign(total_revenue=lambda x: x['quantity'] * x['unit_price']) \
                                           .reset_index()[['product_name', 'category', 'total_revenue']] \
                                           .sort_values('total_revenue', ascending=False) \
                                           .head(5)
filtered_revenue_by_category = filtered_order_items.merge(filtered_orders, on='order_id') \
                                                  .merge(filtered_products, on='product_id') \
                                                  .groupby('category') \
                                                  .agg({'quantity': 'sum', 'unit_price': 'sum'}) \
                                                  .assign(total_revenue=lambda x: x['quantity'] * x['unit_price']) \
                                                  .reset_index()[['category', 'total_revenue']]

# =============================================================================
# 2. KPIs
# =============================================================================
st.header("2. Indicadores-Chave de Desempenho (KPIs)")

col1, col2, col3 = st.columns(3)
col4, col5, col6 = st.columns(3)

total_revenue = filtered_revenue['total_amount'].sum()
unique_customers = filtered_orders['customer_id'].nunique()
total_orders = len(filtered_orders)
avg_ticket = total_revenue / total_orders if total_orders > 0 else 0
total_customers = len(filtered_orders)  # Contagem de pedidos (clientes totais)
conversion_rate = (len(filtered_orders[filtered_orders['status'] == 'Entregue']) / len(orders)) * 100 if len(orders) > 0 else 0

col1.metric("Receita Total (2024)", f"R$ {total_revenue:,.2f}")
col2.metric("Ticket Médio", f"R$ {avg_ticket:,.2f}")
col3.metric("Clientes Únicos", f"{unique_customers:,}")
col4.metric("Clientes Totais (Pedidos)", f"{total_customers:,}")
col5.metric("Total de Pedidos", f"{total_orders:,}")
col6.metric("Taxa de Conversão (Entregues)", f"{conversion_rate:.2f}%")

# =============================================================================
# 3. Visualizações
# =============================================================================
st.header("3. Visualizações")

# 3.1. Tendência de Receita Mensal
st.subheader("Tendência de Receita Mensal")
fig_revenue = px.line(filtered_revenue, x='order_date', y='total_amount',
                      title="Receita Mensal (2024)", markers=True)
fig_revenue.update_layout(xaxis_title="Mês", yaxis_title="Receita (R$)")
st.plotly_chart(fig_revenue, use_container_width=True)

# 3.2. Top 5 Produtos por Receita
st.subheader("Top 5 Produtos por Receita")
fig_top_products = px.bar(filtered_top_products, x='product_name', y='total_revenue', color='category',
                          title="Top 5 Produtos por Receita")
fig_top_products.update_layout(xaxis_title="Produto", yaxis_title="Receita (R$)", xaxis_tickangle=45)
st.plotly_chart(fig_top_products, use_container_width=True)

# 3.3. Receita por Categoria
st.subheader("Receita por Categoria")
fig_category = px.bar(filtered_revenue_by_category, x='category', y='total_revenue',
                      title="Receita por Categoria")
fig_category.update_layout(xaxis_title="Categoria", yaxis_title="Receita (R$)")
st.plotly_chart(fig_category, use_container_width=True)

# 3.4. Distribuição de Status de Pedidos
st.subheader("Distribuição de Status de Pedidos")
status_counts = filtered_orders['status'].value_counts().reset_index()
status_counts.columns = ['status', 'count']
fig_status = px.pie(status_counts, names='status', values='count',
                    title="Distribuição de Status de Pedidos")
st.plotly_chart(fig_status, use_container_width=True)

# 3.5. Clientes Únicos por Mês
st.subheader("Clientes Únicos por Mês")
monthly_customers = filtered_orders.groupby(filtered_orders['order_date'].dt.strftime('%Y-%m'))['customer_id'] \
                                   .nunique().reset_index(name='unique_customers')
fig_customers = px.line(monthly_customers, x='order_date', y='unique_customers',
                        title="Clientes Únicos por Mês (2024)", markers=True)
fig_customers.update_layout(xaxis_title="Mês", yaxis_title="Clientes Únicos")
st.plotly_chart(fig_customers, use_container_width=True)

# 3.6. Pedidos Totais por Mês
st.subheader("Pedidos Totais por Mês")
total_orders_by_month = filtered_orders.groupby(filtered_orders['order_date'].dt.strftime('%Y-%m')) \
                                      .size().reset_index(name='total_orders')
fig_total_orders = px.line(total_orders_by_month, x='order_date', y='total_orders',
                           title="Pedidos Totais por Mês (2024)", markers=True)
fig_total_orders.update_layout(xaxis_title="Mês", yaxis_title="Total de Pedidos")
st.plotly_chart(fig_total_orders, use_container_width=True)

# 3.7. Distribuição de Segmentos RFM
st.subheader("Distribuição de Segmentos de Clientes (RFM)")
fig_rfm = px.histogram(rfm, x='segment', category_orders={"segment": ["VIP", "Regular", "Ocasional", "Inativo"]},
                       title="Segmentação de Clientes")
fig_rfm.update_layout(xaxis_title="Segmento", yaxis_title="Contagem de Clientes")
st.plotly_chart(fig_rfm, use_container_width=True)

# 3.8. Imagens geradas na Parte 2
st.subheader("Outras Visualizações (Parte 2)")
st.image(base_path + 'price_distribution_by_category.png', caption="Distribuição de Preços por Categoria")
st.image(base_path + 'rfm_segment_distribution.png', caption="Distribuição de Segmentos RFM")
