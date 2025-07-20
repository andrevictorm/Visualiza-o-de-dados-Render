# =============================================================================
# PARTE 3: DASHBOARD INTERATIVO COM STREAMLIT
# =============================================================================
# Este dashboard exibe KPIs e gráficos interativos para o desafio técnico de e-commerce.
# Inclui KPIs (receita, ticket médio, clientes únicos/totais, pedidos, taxa de conversão),
# gráficos (receita mensal, top produtos, receita por categoria, status de pedidos, RFM, pedidos totais, receita por estado)
# e filtros (meses, categoria, status de pedido, estado).
# A Receita Total respeita os filtros de meses, categorias, status e estado, calculada diretamente de orders.csv.
# Ajusta base_path para /opt/render/project/src/ e melhora depuração.
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

# Caminho dos arquivos (testar múltiplos caminhos relativos a base_dir)
base_dir = "/opt/render/project/src/"
possible_paths = [
    os.path.join(base_dir, "Visualiza-o-de-dados-Render", "Ecommerce_Dataset"),
    os.path.join(base_dir, "Ecommerce_Dataset"),
    base_dir,
    os.path.join(base_dir, "ecommerce_dataset"),
    os.path.join(base_dir, "ECommerce_Dataset")
]
base_path = None
required_files = ['customers.csv', 'products.csv', 'orders.csv', 'order_items.csv', 'rfm_segmentation.csv']

for path in possible_paths:
    if os.path.exists(path):
        missing_files = [f for f in required_files if not os.path.exists(os.path.join(path, f))]
        if not missing_files:
            base_path = path
            break

if base_path is None:
    st.error(f"Nenhuma pasta com todos os arquivos necessários encontrada. Arquivos esperados: {', '.join(required_files)}")
    st.write("Por favor, verifique a estrutura do repositório no GitHub. A pasta 'Ecommerce_Dataset' deve estar em 'Visualiza-o-de-dados-Render/Ecommerce_Dataset/' ou na raiz. Compartilhe esta saída para análise.")
    st.stop()
else:
    st.write(f"Usando base_path: {base_path}")

# Verificar se os arquivos necessários existem
missing_files = [f for f in required_files if not os.path.join(base_path, f)]
if missing_files:
    st.error(f"Arquivos ausentes em {base_path}: {', '.join(missing_files)}")
    st.stop()

# Carregar CSVs
@st.cache_data
def load_data():
    try:
        rfm = pd.read_csv(os.path.join(base_path, 'rfm_segmentation.csv'))
        orders = pd.read_csv(os.path.join(base_path, 'orders.csv'))
        order_items = pd.read_csv(os.path.join(base_path, 'order_items.csv'))
        products = pd.read_csv(os.path.join(base_path, 'products.csv'))
        customers = pd.read_csv(os.path.join(base_path, 'customers.csv'))  # Carregar customers.csv para estado
        orders['order_date'] = pd.to_datetime(orders['order_date'])
        return rfm, orders, order_items, products, customers
    except FileNotFoundError as e:
        st.error(f"Erro ao carregar arquivos: {str(e)}")
        st.stop()

rfm, orders, order_items, products, customers = load_data()

# =============================================================================
# 1. Filtros
# =============================================================================
st.header("1. Filtros")
st.markdown("Selecione os filtros para personalizar os KPIs e gráficos.")

col1, col2, col3, col4 = st.columns(4)

with col1:
    months = sorted(orders['order_date'].dt.strftime('%Y-%m').unique().tolist())
    selected_months = st.multiselect("Selecione os meses", months, default=months)

with col2:
    categories = sorted(products['category'].unique().tolist())
    selected_categories = st.multiselect("Selecione as categorias", categories, default=categories)

with col3:
    statuses = sorted(orders['status'].unique().tolist())
    selected_statuses = st.multiselect("Selecione os status de pedido", statuses, default=['Entregue'])

with col4:
    states = sorted(customers['state'].unique().tolist())
    selected_states = st.multiselect("Selecione os estados", states, default=states)

# Filtrar dados
filtered_orders = orders[orders['order_date'].dt.strftime('%Y-%m').isin(selected_months) & 
                        orders['status'].isin(selected_statuses)]
filtered_orders = filtered_orders[filtered_orders['customer_id'].isin(customers[customers['state'].isin(selected_states)]['customer_id'])]
filtered_order_items = order_items[order_items['order_id'].isin(filtered_orders['order_id'])]
filtered_products = products[products['category'].isin(selected_categories)]
filtered_order_items = filtered_order_items[filtered_order_items['product_id'].isin(filtered_products['product_id'])]
filtered_orders = filtered_orders[filtered_orders['order_id'].isin(filtered_order_items['order_id'])]

# Calcular receita mensal com base nos filtros
filtered_revenue = filtered_orders.merge(filtered_order_items, on='order_id') \
                                 .merge(filtered_products, on='product_id') \
                                 .assign(item_revenue=lambda x: x['quantity'] * x['unit_price']) \
                                 .groupby(filtered_orders['order_date'].dt.strftime('%Y-%m')) \
                                 .agg({'item_revenue': 'sum'}) \
                                 .reset_index() \
                                 .rename(columns={'item_revenue': 'total_amount', 'order_date': 'order_date'})

# Calcular receita por estado
filtered_revenue_by_state = filtered_orders.merge(filtered_order_items, on='order_id') \
                                          .merge(filtered_products, on='product_id') \
                                          .merge(customers, on='customer_id') \
                                          .assign(item_revenue=lambda x: x['quantity'] * x['unit_price']) \
                                          .groupby('state') \
                                          .agg({'item_revenue': 'sum'}) \
                                          .reset_index() \
                                          .rename(columns={'item_revenue': 'total_revenue'})

# Calcular top 5 produtos por receita (usando todos os produtos sem restrição inicial de categoria)
filtered_top_products = order_items.merge(orders, on='order_id') \
                                  .merge(products, on='product_id') \
                                  .assign(item_revenue=lambda x: x['quantity'] * x['unit_price']) \
                                  .groupby(['product_name', 'category']) \
                                  .agg({'item_revenue': 'sum'}) \
                                  .reset_index() \
                                  .rename(columns={'item_revenue': 'total_revenue'}) \
                                  .sort_values('total_revenue', ascending=False) \
                                  .head(5)

# Calcular receita por categoria
filtered_revenue_by_category = filtered_order_items.merge(filtered_orders, on='order_id') \
                                                  .merge(filtered_products, on='product_id') \
                                                  .assign(item_revenue=lambda x: x['quantity'] * x['unit_price']) \
                                                  .groupby('category') \
                                                  .agg({'item_revenue': 'sum'}) \
                                                  .reset_index() \
                                                  .rename(columns={'item_revenue': 'total_revenue'})

# =============================================================================
# 2. KPIs
# =============================================================================
st.header("2. Indicadores-Chave de Desempenho (KPIs)")
st.markdown("Resumo das métricas principais com base nos filtros selecionados.")

col1, col2, col3 = st.columns(3)
col4, col5, col6 = st.columns(3)

# Calcular Receita Total com base nos filtros
revenue_df = filtered_order_items.merge(filtered_orders, on='order_id') \
                                .merge(filtered_products, on='product_id') \
                                .assign(item_revenue=lambda x: x['quantity'] * x['unit_price'])
total_revenue = revenue_df['item_revenue'].sum()
unique_customers = filtered_orders['customer_id'].nunique()
total_orders = len(filtered_orders)
avg_ticket = total_revenue / total_orders if total_orders > 0 else 0
avg_orders_per_customer = total_orders / unique_customers if unique_customers > 0 else 0
conversion_rate = (len(filtered_orders[filtered_orders['status'] == 'Entregue']) / len(orders)) * 100 if len(orders) > 0 else 0

col1.metric("Receita Total (2024)", f"R$ {total_revenue:,.2f}")
col2.metric("Ticket Médio", f"R$ {avg_ticket:,.2f}")
col3.metric("Clientes Únicos", f"{unique_customers:,}")
col4.metric("Média de Pedidos por Cliente", f"{avg_orders_per_customer:.2f}")
col5.metric("Total de Pedidos", f"{total_orders:,}")
col6.metric("Taxa de Conversão (Entregues)", f"{conversion_rate:.2f}%")

# =============================================================================
# 3. Visualizações
# =============================================================================
st.header("3. Visualizações")
st.markdown("Gráficos interativos que refletem os filtros aplicados.")

# 3.1. Tendência de Receita Mensal
st.subheader("Tendência de Receita Mensal")
st.markdown("Mostra a evolução da receita mensal com base nos filtros de meses, categorias e status.")
if not filtered_revenue.empty:
    fig_revenue = px.line(filtered_revenue, x='order_date', y='total_amount',
                          title="Receita Mensal (2024)", markers=True)
    fig_revenue.update_layout(xaxis_title="Mês", yaxis_title="Receita (R$)")
    st.plotly_chart(fig_revenue, use_container_width=True)
else:
    st.warning("Nenhum dado disponível para os filtros selecionados.")

# 3.2. Top 5 Produtos por Receita
st.subheader("Top 5 Produtos por Receita")
st.markdown("Exibe os 5 produtos com maior receita, considerando os filtros aplicados.")
if not filtered_top_products.empty:
    fig_top_products = px.bar(filtered_top_products, x='product_name', y='total_revenue', color='category',
                              title="Top 5 Produtos por Receita")
    fig_top_products.update_layout(xaxis_title="Produto", yaxis_title="Receita (R$)", xaxis_tickangle=45)
    st.plotly_chart(fig_top_products, use_container_width=True)
else:
    st.warning("Nenhum dado disponível para os filtros selecionados.")

# 3.3. Receita por Categoria
st.subheader("Receita por Categoria")
st.markdown("Mostra a receita total por categoria de produto, com base nos filtros.")
if not filtered_revenue_by_category.empty:
    fig_category = px.bar(filtered_revenue_by_category, x='category', y='total_revenue',
                          title="Receita por Categoria")
    fig_category.update_layout(xaxis_title="Categoria", yaxis_title="Receita (R$)")
    st.plotly_chart(fig_category, use_container_width=True)
else:
    st.warning("Nenhum dado disponível para os filtros selecionados.")

# 3.4. Distribuição de Status de Pedidos
st.subheader("Distribuição de Status de Pedidos")
st.markdown("Proporção de pedidos por status (ex.: Entregue, Pendente, Cancelado).")
status_counts = filtered_orders['status'].value_counts().reset_index()
status_counts.columns = ['status', 'count']
if not status_counts.empty:
    fig_status = px.pie(status_counts, names='status', values='count',
                        title="Distribuição de Status de Pedidos")
    st.plotly_chart(fig_status, use_container_width=True)
else:
    st.warning("Nenhum dado disponível para os filtros selecionados.")

# 3.5. Clientes Únicos por Mês
st.subheader("Clientes Únicos por Mês")
st.markdown("Evolução do número de clientes únicos por mês, com base nos filtros.")
monthly_customers = filtered_orders.groupby(filtered_orders['order_date'].dt.strftime('%Y-%m'))['customer_id'] \
                                   .nunique().reset_index(name='unique_customers')
if not monthly_customers.empty:
    fig_customers = px.line(monthly_customers, x='order_date', y='unique_customers',
                            title="Clientes Únicos por Mês (2024)", markers=True)
    fig_customers.update_layout(xaxis_title="Mês", yaxis_title="Clientes Únicos")
    st.plotly_chart(fig_customers, use_container_width=True)
else:
    st.warning("Nenhum dado disponível para os filtros selecionados.")

# 3.6. Pedidos Totais por Mês
st.subheader("Pedidos Totais por Mês")
st.markdown("Evolução do número total de pedidos por mês, com base nos filtros.")
total_orders_by_month = filtered_orders.groupby(filtered_orders['order_date'].dt.strftime('%Y-%m')) \
                                      .size().reset_index(name='total_orders')
if not total_orders_by_month.empty:
    fig_total_orders = px.line(total_orders_by_month, x='order_date', y='total_orders',
                               title="Pedidos Totais por Mês (2024)", markers=True)
    fig_total_orders.update_layout(xaxis_title="Mês", yaxis_title="Total de Pedidos")
    st.plotly_chart(fig_total_orders, use_container_width=True)
else:
    st.warning("Nenhum dado disponível para os filtros selecionados.")

# 3.7. Distribuição de Segmentos RFM
st.subheader("Distribuição de Segmentos de Clientes (RFM)")
st.markdown("Distribuição de clientes por segmento (VIP, Regular, Ocasional, Inativo).")
if not rfm.empty:
    fig_rfm = px.histogram(rfm, x='segment', category_orders={"segment": ["VIP", "Regular", "Ocasional", "Inativo"]},
                           title="Segmentação de Clientes")
    fig_rfm.update_layout(xaxis_title="Segmento", yaxis_title="Contagem de Clientes")
    st.plotly_chart(fig_rfm, use_container_width=True)
else:
    st.warning("Nenhum dado disponível para os filtros selecionados.")

# 3.8. Receita por Estado
st.subheader("Receita por Estado")
st.markdown("Mostra a receita total por estado, com base nos filtros aplicados.")
if not filtered_revenue_by_state.empty:
    fig_state = px.bar(filtered_revenue_by_state, x='state', y='total_revenue',
                       title="Receita por Estado")
    fig_state.update_layout(xaxis_title="Estado", yaxis_title="Receita (R$)", xaxis_tickangle=45)
    st.plotly_chart(fig_state, use_container_width=True)
else:
    st.warning("Nenhum dado disponível para os filtros selecionados.")

# 3.9. Imagens geradas na Parte 2
st.subheader("Outras Visualizações (Parte 2)")
st.markdown("Gráficos estáticos gerados na análise exploratória.")
try:
    st.image(os.path.join(base_path, 'price_distribution_by_category.png'), caption="Distribuição de Preços por Categoria")
    st.image(os.path.join(base_path, 'rfm_segment_distribution.png'), caption="Distribuição de Segmentos RFM")
except FileNotFoundError:
    st.warning(f"Imagens da Parte 2 não encontradas. Verifique se estão em {base_path}")

st.markdown("---")
st.markdown("Dashboard criado para o desafio técnico de e-commerce, 20/07/2025.")
