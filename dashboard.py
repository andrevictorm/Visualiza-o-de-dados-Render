# =============================================================================
# PARTE 3: DASHBOARD INTERATIVO COM STREAMLIT (OTIMIZADO)
# =============================================================================
# Dashboard otimizado para e-commerce com KPIs e gráficos interativos.
# Inclui filtros (meses, categorias, status, estados) e visualizações otimizadas.
# Focado em reduzir tempo de carregamento e deploy no Render.
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

# Caminho dos arquivos
base_dir = "/opt/render/project/src/"
base_path = os.path.join(base_dir, "Ecommerce_Dataset")  # Ajustado com base no sucesso anterior
required_files = ['customers.csv', 'products.csv', 'orders.csv', 'order_items.csv', 'rfm_segmentation.csv']

if not all(os.path.exists(os.path.join(base_path, f)) for f in required_files):
    st.error(f"Arquivos ausentes em {base_path}: {', '.join(required_files)}. Verifique a estrutura.")
    st.stop()

# Carregar dados com cache
@st.cache_data
def load_data():
    rfm = pd.read_csv(os.path.join(base_path, 'rfm_segmentation.csv'))
    orders = pd.read_csv(os.path.join(base_path, 'orders.csv'))
    order_items = pd.read_csv(os.path.join(base_path, 'order_items.csv'))
    products = pd.read_csv(os.path.join(base_path, 'products.csv'))
    customers = pd.read_csv(os.path.join(base_path, 'customers.csv'))
    orders['order_date'] = pd.to_datetime(orders['order_date'])
    return rfm, orders, order_items, products, customers

rfm, orders, order_items, products, customers = load_data()

# Filtros
st.header("1. Filtros")
col1, col2, col3, col4 = st.columns(4)

with col1:
    months = sorted(orders['order_date'].dt.strftime('%Y-%m').unique().tolist())
    selected_months = st.multiselect("Meses", months, default=months)

with col2:
    categories = sorted(products['category'].unique().tolist())
    selected_categories = st.multiselect("Categorias", categories, default=categories)

with col3:
    statuses = sorted(orders['status'].unique().tolist())
    selected_statuses = st.multiselect("Status", statuses, default=['Entregue'])

with col4:
    states = sorted(customers['state'].unique().tolist())
    selected_states = st.multiselect("Estados", states, default=states)

# Filtrar dados dinamicamente
@st.cache_data
def filter_data(orders, order_items, products, customers, months, categories, statuses, states):
    filtered_orders = orders[orders['order_date'].dt.strftime('%Y-%m').isin(months) & 
                           orders['status'].isin(statuses)]
    filtered_orders = filtered_orders[filtered_orders['customer_id'].isin(
        customers[customers['state'].isin(states)]['customer_id'])]
    filtered_order_items = order_items[order_items['order_id'].isin(filtered_orders['order_id'])]
    filtered_products = products[products['category'].isin(categories)]
    filtered_order_items = filtered_order_items[filtered_order_items['product_id'].isin(filtered_products['product_id'])]
    filtered_orders = filtered_orders[filtered_orders['order_id'].isin(filtered_order_items['order_id'])]
    return filtered_orders, filtered_order_items, filtered_products

filtered_orders, filtered_order_items, filtered_products = filter_data(
    orders, order_items, products, customers, selected_months, selected_categories, selected_statuses, selected_states
)

# KPIs otimizados
st.header("2. KPIs")
@st.cache_data
def calculate_kpis(filtered_orders, filtered_order_items, filtered_products):
    revenue_df = filtered_order_items.merge(filtered_orders, on='order_id') \
                                    .merge(filtered_products, on='product_id') \
                                    .assign(item_revenue=lambda x: x['quantity'] * x['unit_price'])
    total_revenue = revenue_df['item_revenue'].sum()
    unique_customers = filtered_orders['customer_id'].nunique()
    total_orders = len(filtered_orders)
    avg_ticket = total_revenue / total_orders if total_orders > 0 else 0
    avg_orders_per_customer = total_orders / unique_customers if unique_customers > 0 else 0
    conversion_rate = (len(filtered_orders[filtered_orders['status'] == 'Entregue']) / len(orders)) * 100 if len(orders) > 0 else 0
    return total_revenue, unique_customers, total_orders, avg_ticket, avg_orders_per_customer, conversion_rate

total_revenue, unique_customers, total_orders, avg_ticket, avg_orders_per_customer, conversion_rate = calculate_kpis(
    filtered_orders, filtered_order_items, filtered_products
)

col1, col2, col3 = st.columns(3)
col4, col5, col6 = st.columns(3)
col1.metric("Receita Total", f"R$ {total_revenue:,.2f}")
col2.metric("Ticket Médio", f"R$ {avg_ticket:,.2f}")
col3.metric("Clientes Únicos", f"{unique_customers:,}")
col4.metric("Pedidos por Cliente", f"{avg_orders_per_customer:.2f}")
col5.metric("Total Pedidos", f"{total_orders:,}")
col6.metric("Taxa Conversão", f"{conversion_rate:.2f}%")

# Visualizações otimizadas
st.header("3. Visualizações")
@st.cache_data
def get_visualizations(filtered_orders, filtered_order_items, filtered_products, rfm):
    # Top 5 Produtos (sem restrição inicial de categoria)
    top_products = order_items.merge(orders, on='order_id') \
                             .merge(products, on='product_id') \
                             .assign(item_revenue=lambda x: x['quantity'] * x['unit_price']) \
                             .groupby(['product_name', 'category']) \
                             .agg({'item_revenue': 'sum'}) \
                             .reset_index() \
                             .rename(columns={'item_revenue': 'total_revenue'}) \
                             .sort_values('total_revenue', ascending=False) \
                             .head(5)

    # Receita por Categoria
    revenue_by_category = filtered_order_items.merge(filtered_orders, on='order_id') \
                                             .merge(filtered_products, on='product_id') \
                                             .assign(item_revenue=lambda x: x['quantity'] * x['unit_price']) \
                                             .groupby('category') \
                                             .agg({'item_revenue': 'sum'}) \
                                             .reset_index() \
                                             .rename(columns={'item_revenue': 'total_revenue'})

    # Receita por Estado
    revenue_by_state = filtered_orders.merge(filtered_order_items, on='order_id') \
                                     .merge(filtered_products, on='product_id') \
                                     .merge(customers, on='customer_id') \
                                     .assign(item_revenue=lambda x: x['quantity'] * x['unit_price']) \
                                     .groupby('state') \
                                     .agg({'item_revenue': 'sum'}) \
                                     .reset_index() \
                                     .rename(columns={'item_revenue': 'total_revenue'})

    # Receita Mensal
    revenue_monthly = filtered_orders.merge(filtered_order_items, on='order_id') \
                                    .merge(filtered_products, on='product_id') \
                                    .assign(item_revenue=lambda x: x['quantity'] * x['unit_price']) \
                                    .groupby(filtered_orders['order_date'].dt.strftime('%Y-%m')) \
                                    .agg({'item_revenue': 'sum'}) \
                                    .reset_index() \
                                    .rename(columns={'item_revenue': 'total_amount', 'order_date': 'order_date'})

    # Status de Pedidos
    status_counts = filtered_orders['status'].value_counts().reset_index()
    status_counts.columns = ['status', 'count']

    # Clientes Únicos por Mês
    monthly_customers = filtered_orders.groupby(filtered_orders['order_date'].dt.strftime('%Y-%m'))['customer_id'] \
                                      .nunique().reset_index(name='unique_customers')

    # Pedidos Totais por Mês
    total_orders_by_month = filtered_orders.groupby(filtered_orders['order_date'].dt.strftime('%Y-%m')) \
                                          .size().reset_index(name='total_orders')

    return top_products, revenue_by_category, revenue_by_state, revenue_monthly, status_counts, monthly_customers, total_orders_by_month

top_products, revenue_by_category, revenue_by_state, revenue_monthly, status_counts, monthly_customers, total_orders_by_month = get_visualizations(
    filtered_orders, filtered_order_items, filtered_products, rfm
)

# Gráficos
# 3.1. Top 5 Produtos
st.subheader("Top 5 Produtos por Receita")
if not top_products.empty:
    fig_top = px.bar(top_products, x='product_name', y='total_revenue', color='category',
                     title="Top 5 Produtos por Receita")
    fig_top.update_layout(xaxis_title="Produto", yaxis_title="Receita (R$)", xaxis_tickangle=45)
    st.plotly_chart(fig_top, use_container_width=True)
else:
    st.warning("Nenhum dado disponível.")

# 3.2. Receita por Categoria
st.subheader("Receita por Categoria")
if not revenue_by_category.empty:
    fig_cat = px.bar(revenue_by_category, x='category', y='total_revenue',
                     title="Receita por Categoria")
    fig_cat.update_layout(xaxis_title="Categoria", yaxis_title="Receita (R$)")
    st.plotly_chart(fig_cat, use_container_width=True)
else:
    st.warning("Nenhum dado disponível.")

# 3.3. Receita por Estado
st.subheader("Receita por Estado")
if not revenue_by_state.empty:
    fig_state = px.bar(revenue_by_state, x='state', y='total_revenue',
                       title="Receita por Estado")
    fig_state.update_layout(xaxis_title="Estado", yaxis_title="Receita (R$)", xaxis_tickangle=45)
    st.plotly_chart(fig_state, use_container_width=True)
else:
    st.warning("Nenhum dado disponível.")

# 3.4. Tendência de Receita Mensal
st.subheader("Tendência de Receita Mensal")
if not revenue_monthly.empty:
    fig_month = px.line(revenue_monthly, x='order_date', y='total_amount',
                        title="Receita Mensal (2024)", markers=True)
    fig_month.update_layout(xaxis_title="Mês", yaxis_title="Receita (R$)")
    st.plotly_chart(fig_month, use_container_width=True)
else:
    st.warning("Nenhum dado disponível.")

# 3.5. Distribuição de Status
st.subheader("Distribuição de Status de Pedidos")
if not status_counts.empty:
    fig_status = px.pie(status_counts, names='status', values='count',
                        title="Distribuição de Status")
    st.plotly_chart(fig_status, use_container_width=True)
else:
    st.warning("Nenhum dado disponível.")

# 3.6. Clientes Únicos por Mês
st.subheader("Clientes Únicos por Mês")
if not monthly_customers.empty:
    fig_cust = px.line(monthly_customers, x='order_date', y='unique_customers',
                       title="Clientes Únicos por Mês", markers=True)
    fig_cust.update_layout(xaxis_title="Mês", yaxis_title="Clientes Únicos")
    st.plotly_chart(fig_cust, use_container_width=True)
else:
    st.warning("Nenhum dado disponível.")

# 3.7. Pedidos Totais por Mês
st.subheader("Pedidos Totais por Mês")
if not total_orders_by_month.empty:
    fig_orders = px.line(total_orders_by_month, x='order_date', y='total_orders',
                         title="Pedidos Totais por Mês", markers=True)
    fig_orders.update_layout(xaxis_title="Mês", yaxis_title="Total Pedidos")
    st.plotly_chart(fig_orders, use_container_width=True)
else:
    st.warning("Nenhum dado disponível.")

# 3.8. Segmentos RFM
st.subheader("Distribuição de Segmentos RFM")
if not rfm.empty:
    fig_rfm = px.histogram(rfm, x='segment', category_orders={"segment": ["VIP", "Regular", "Ocasional", "Inativo"]},
                           title="Segmentação de Clientes")
    fig_rfm.update_layout(xaxis_title="Segmento", yaxis_title="Contagem")
    st.plotly_chart(fig_rfm, use_container_width=True)
else:
    st.warning("Nenhum dado disponível.")

# 3.9. Imagens estáticas
st.subheader("Visualizações Estáticas")
try:
    st.image(os.path.join(base_path, 'price_distribution_by_category.png'), caption="Preços por Categoria")
    st.image(os.path.join(base_path, 'rfm_segment_distribution.png'), caption="Segmentos RFM")
except FileNotFoundError:
    st.warning(f"Imagens não encontradas em {base_path}")

st.markdown("---")
st.markdown("Dashboard otimizado, 20/07/2025")
