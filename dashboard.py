# =============================================================================
# PARTE 3: DASHBOARD INTERATIVO COM STREAMLIT (OTIMIZADO)
# =============================================================================
# Dashboard otimizado para e-commerce com KPIs e gráficos interativos.
# Inclui filtros (meses, categorias, status, estados, segmentos RFM) e visualizações otimizadas.
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
col1, col2, col3, col4, col5 = st.columns(5)  # Aumentado para 5 colunas

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

with col5:
    rfm_segments = sorted(rfm['segment'].unique().tolist())
    selected_rfm_segments = st.multiselect("Segmentos RFM", rfm_segments, default=rfm_segments)

# Filtrar dados dinamicamente
@st.cache_data
def filter_data(orders, order_items, products, customers, rfm, months, categories, statuses, states, rfm_segments):
    filtered_orders = orders[orders['order_date'].dt.strftime('%Y-%m').isin(months) & 
                           orders['status'].isin(statuses)]
    filtered_orders = filtered_orders[filtered_orders['customer_id'].isin(
        customers[customers['state'].isin(states)]['customer_id'])]
    filtered_order_items = order_items[order_items['order_id'].isin(filtered_orders['order_id'])]
    filtered_products = products[products['category'].isin(categories)]
    filtered_order_items = filtered_order_items[filtered_order_items['product_id'].isin(filtered_products['product_id'])]
    filtered_orders = filtered_orders[filtered_orders['order_id'].isin(filtered_order_items['order_id'])]
    
    # Filtrar RFM se aplicável
    if rfm_segments:
        filtered_customer_ids = rfm[rfm['segment'].isin(rfm_segments)]['customer_id'].unique()
        filtered_orders = filtered_orders[filtered_orders['customer_id'].isin(filtered_customer_ids)]
    
    return filtered_orders, filtered_order_items, filtered_products

filtered_orders, filtered_order_items, filtered_products = filter_data(
    orders, order_items, products, customers, rfm, selected_months, selected_categories, selected_statuses, selected_states, selected_rfm_segments
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
def get_visualizations(orders, order_items, products, filtered_orders, filtered_order_items, filtered_products, customers, rfm):
    # Top 5 Produtos (usando dados brutos para todas as categorias)
    top_products = order_items.merge(orders, on='order_id') \
                             .merge(products, on='product_id') \
                             .assign(item_revenue=lambda x: x['quantity'] * x['unit_price']) \
                             .groupby(['product_name', 'category']) \
                             .agg({'item_revenue': 'sum'}) \
                             .reset_index() \
                             .rename(columns={'item_revenue': 'total_revenue'}) \
                             .sort_values('total_revenue', ascending=False) \
                             .head(5)

    # Receita por Categoria (com filtros)
    revenue_by_category = filtered_order_items.merge(filtered_orders, on='order_id') \
                                             .merge(filtered_products, on='product_id') \
                                             .assign(item_revenue=lambda x: x['quantity'] * x['unit_price']) \
                                             .groupby('category') \
                                             .agg({'item_revenue': 'sum'}) \
                                             .reset_index() \
                                             .rename(columns={'item_revenue': 'total_revenue'})

    # Receita por Estado (com filtros)
    revenue_by_state = filtered_orders.merge(filtered_order_items, on='order_id') \
                                     .merge(filtered_products, on='product_id') \
                                     .merge(customers, on='customer_id') \
                                     .assign(item_revenue=lambda x: x['quantity'] * x['unit_price']) \
                                     .groupby('state') \
                                     .agg({'item_revenue': 'sum'}) \
                                     .reset_index() \
                                     .rename(columns={'item_revenue': 'total_revenue'})

    # Receita Mensal (com filtros)
    revenue_monthly = filtered_orders.merge(filtered_order_items, on='order_id') \
                                    .merge(filtered_products, on='product_id') \
                                    .assign(item_revenue=lambda x: x['quantity'] * x['unit_price']) \
                                    .groupby(filtered_orders['order_date'].dt.strftime('%Y-%m')) \
                                    .agg({'item_revenue': 'sum'}) \
                                    .reset_index() \
                                    .rename(columns={'item_revenue': 'total_amount', 'order_date': 'order_date'})

    # Status de Pedidos (com filtros)
    status_counts = filtered_orders['status'].value_counts().reset_index()
    status_counts.columns = ['status', 'count']

    # Clientes Únicos por Mês (com filtros)
    monthly_customers = filtered_orders.groupby(filtered_orders['order_date'].dt.strftime('%Y-%m'))['customer_id'] \
                                      .nunique().reset_index(name='unique_customers')

    # Pedidos Totais por Mês (com filtros)
    total_orders_by_month = filtered_orders.groupby(filtered_orders['order_date'].dt.strftime('%Y-%m')) \
                                          .size().reset_index(name='total_orders')

    return top_products, revenue_by_category, revenue_by_state, revenue_monthly, status_counts, monthly_customers, total_orders_by_month

top_products, revenue_by_category, revenue_by_state, revenue_monthly, status_counts, monthly_customers, total_orders_by_month = get_visualizations(
    orders, order_items, products, filtered_orders, filtered_order_items, filtered_products, customers, rfm
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

# Relatório Resumo
st.header("Resumo dos Resultados")
st.markdown("""
### Análise Exploratória:
- **Estatísticas descritivas**: Fornecem uma visão geral dos dados:
  - `customers`: 10.000 clientes, com 8.864 nomes únicos e 2.973 cidades.
  - `products`: 500 produtos, com preços variando de 15,53 a 2.971,16 reais (média de R$485,32).
  - `orders`: 50.000 pedidos, com `total_amount` de 12,75 a 14.617,32 reais (média de R$1.211,58).
  - `order_items`: 101.382 itens, com quantidades de 1 a 3 e preços unitários de 12,43 a 3.118,45 reais.
- **Outliers**: 3.481 pedidos com valores extremos em `total_amount`, indicando compras de alto valor (ex.: R$10.873,03).
- **Gráficos**: Boxplot de preços por categoria e histograma de valores de pedidos mostram a distribuição dos dados.

### Análise Temporal:
- **Receita mensal**: Confirma o padrão sazonal, com picos em novembro (6,4M) e dezembro (5,8M).
- **Crescimento mês a mês**: Variações significativas, como +30,02% em novembro e -9,50% em dezembro.
- **Clientes únicos**: Pico em novembro (4.593 clientes), consistente com a sazonalidade.

### Segmentação RFM:
- Clientes segmentados em VIP, Regular, Ocasional e Inativo com base em recência, frequência e monetário.
- Exemplo: João Guilherme da Cruz (RFM_score=10, VIP) comprou recentemente (16 dias), 5 vezes, gastando R$7.031,01.
""")

# Visualização da tabela rfm_segmentation.csv com filtros
st.header("Tabela de Segmentação RFM")
# Filtros para recency, frequency e monetary
min_recency = int(rfm['recency'].min())
max_recency = int(rfm['recency'].max())
min_frequency = int(rfm['frequency'].min())
max_frequency = int(rfm['frequency'].max())
min_monetary = int(rfm['monetary'].min())
max_monetary = int(rfm['monetary'].max())

recency_range = st.slider("Recency (dias)", min_recency, max_recency, (min_recency, max_recency))
frequency_range = st.slider("Frequency (pedidos)", min_frequency, max_frequency, (min_frequency, max_frequency))
monetary_range = st.slider("Monetary (R$)", min_monetary, max_monetary, (min_monetary, max_monetary))

# Filtrar a tabela com base nos sliders
filtered_rfm = rfm[
    (rfm['recency'] >= recency_range[0]) & (rfm['recency'] <= recency_range[1]) &
    (rfm['frequency'] >= frequency_range[0]) & (rfm['frequency'] <= frequency_range[1]) &
    (rfm['monetary'] >= monetary_range[0]) & (rfm['monetary'] <= monetary_range[1])
]

# Exibir a tabela
st.dataframe(filtered_rfm)

st.markdown("---")
st.markdown("Dashboard otimizado, 20/07/2025")
