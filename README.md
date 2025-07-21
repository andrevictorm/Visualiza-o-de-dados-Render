# 📊 Dashboard Interativo de E-commerce

## Visão Geral do Projeto

Este projeto consiste em uma análise completa de dados de vendas de um e-commerce, culminando no desenvolvimento de um dashboard interativo. [cite_start]Foi elaborado como parte de um desafio técnico com o objetivo de demonstrar habilidades em manipulação de dados com SQL, análise de dados com Python e visualização interativa. [cite: 41]

[cite_start]O desafio propôs a atuação como Cientista de Dados para uma empresa de e-commerce de produtos eletrônicos, buscando compreender melhor o comportamento de vendas, a performance dos produtos e os padrões dos clientes. [cite: 42, 43]

## Estrutura do Repositório

[cite_start]O repositório `Visualiza-o-de-dados-Render` contém os seguintes arquivos e pastas essenciais: [cite: 31]

* [cite_start]`Ecommerce_Dataset/`: Pasta contendo os arquivos CSV (`customers.csv`, `products.csv`, `orders.csv`, `order_items.csv`) essenciais para o funcionamento do dashboard. [cite: 32]
* [cite_start]`dashboard.py`: O código-fonte principal do dashboard interativo, desenvolvido em Streamlit. [cite: 33]
* [cite_start]`requirements.txt`: Lista todas as dependências Python necessárias para a execução do aplicativo. [cite: 34]
* [cite_start]`Gerador_de_dados.ipynb`: Notebook Jupyter (Google Colab) utilizado para implementar o script de geração de dados sintéticos. [cite: 9]
* [cite_start]`Queries_SQLite.ipynb`: Notebook Jupyter (Google Colab) utilizado para criar a base de dados SQLite e executar as queries SQL. [cite: 13]
* [cite_start]`Análise_de_Dados.ipynb`: Notebook Jupyter (Google Colab) contendo a análise exploratória, temporal e de segmentação de clientes. [cite: 19]
* [cite_start]`create_tables.sql`: Script SQL para a criação das tabelas no banco de dados. [cite: 11]
* [cite_start]`queries.sql`: Arquivo contendo as consultas SQL realizadas para extração de insights. [cite: 16]

## Linha de Raciocínio no Desenvolvimento

O projeto foi estruturado em quatro partes principais:

### [cite_start]Parte 1: Geração de Dados Sintéticos [cite: 8]
[cite_start]Nesta fase, um gerador de dados sintéticos fornecido foi implementado e executado no Google Colab, utilizando o arquivo `Gerador_de_dados.ipynb`. [cite: 9] [cite_start]Foram gerados dados realistas para 10.000 clientes, 500 produtos, 50.000 pedidos e 101.382 itens de pedidos, que foram salvos em formato CSV no Google Drive, na pasta `Ecommerce_Dataset`, juntamente com o script SQL de criação de tabelas. [cite: 10, 11]

### [cite_start]Parte 2: Manipulação de Dados com SQL [cite: 12]
[cite_start]Aproveitando o ambiente Colab, foi criada uma base de dados relacional em SQLite (`ecommerce_test.db`)[cite: 13]. As tabelas `customers`, `products`, `orders` e `order_items` foram definidas com chaves estrangeiras para garantir a integridade dos dados. Os CSVs gerados na Parte 1 foram importados para essas tabelas. [cite_start]Diversas consultas SQL foram executadas para responder a questões analíticas essenciais, como receita total por mês, top produtos por receita, receita por categoria, número de clientes únicos por mês, ticket médio e top 10 clientes por valor total de compras. [cite: 14, 15, 48]

### [cite_start]Parte 3: Análise de Dados com Python [cite: 18]
[cite_start]Com os dados carregados via pandas no notebook `Análise_de_Dados.ipynb`, a análise se dividiu em três frentes: [cite: 19, 20, 21]
* [cite_start]**Análise Exploratória de Dados (EDA)**: Geração de estatísticas descritivas, identificação de padrões e valores extremos (outliers) utilizando o método IQR (Interquartile Range). [cite: 22, 49]
* [cite_start]**Análise Temporal**: Utilização da coluna de data dos pedidos para agrupar a receita e o número de clientes únicos por mês, identificando tendências de vendas ao longo do tempo, sazonalidade e crescimento mês a mês. [cite: 23, 50]
* [cite_start]**Segmentação de Clientes (RFM)**: Aplicação da técnica RFM (Recência, Frequência, Monetário) para classificar clientes em segmentos (VIP, Regular, Ocasional, Inativo) com base em seus scores, fornecendo perfis básicos dos segmentos. [cite: 25, 26, 27, 50]

### [cite_start]Parte 4: Versionamento e Deployment do Dashboard [cite: 29]
[cite_start]Após a conclusão das etapas de análise, o projeto foi organizado e preparado para disponibilização como um dashboard interativo. [cite: 30]
* [cite_start]**Repositório GitHub**: Foi criado o repositório `Visualiza-o-de-dados-Render` para controle de versão. [cite: 31]
* [cite_start]**Hospedagem com Render**: Para acesso remoto, foi configurado um serviço web na plataforma Render, nomeado `ecommerce-dashboard`, que automatiza o build e deployment do Streamlit app. [cite: 35, 36]

## Funcionalidades do Dashboard

[cite_start]O dashboard interativo oferece as seguintes funcionalidades principais: [cite: 51]

* [cite_start]**Filtros Dinâmicos**: Permite filtrar dados por Mês, Categoria de Produto, Status do Pedido, Estado do Cliente e Segmento RFM. [cite: 52]
* **KPIs Essenciais**: Exibe métricas chave como Receita Total, Ticket Médio, Clientes Únicos, Pedidos por Cliente, Total de Pedidos e Taxa de Conversão.
* **Gráficos Interativos**:
    * Tendência de Receita Mensal.
    * Variação Percentual da Receita Mês a Mês.
    * Receita por Categoria de Produto.
    * Top 5 Produtos por Receita.
    * Total de Pedidos por Mês.
    * Clientes Únicos por Mês.
    * Novos Clientes por Mês.
    * Distribuição de Clientes por Região (Estado).
    * Clientes por Categoria.
    * Receita por Estado.
    * Distribuição de Status de Pedidos.
    * Distribuição de Segmentos RFM (Histograma).
* **Visualização de Tabela RFM**: Tabela detalhada dos clientes segmentados, com filtros adicionais por Recência, Frequência e Monetário.

## Como Executar o Projeto Localmente

Para rodar o dashboard em sua máquina local, siga os passos abaixo:

1.  **Clone o repositório**:
    ```bash
    git clone [https://github.com/andrevictorm/Visualiza-o-de-dados-Render.git](https://github.com/andrevictorm/Visualiza-o-de-dados-Render.git)
    cd Visualiza-o-de-dados-Render
    ```
2.  **Crie e ative um ambiente virtual (recomendado)**:
    ```bash
    python -m venv venv
    # No Windows
    .\venv\Scripts\activate
    # No macOS/Linux
    source venv/bin/activate
    ```
3.  **Instale as dependências**:
    ```bash
    [cite_start]pip install -r requirements.txt [cite: 34]
    ```
4.  **Garanta os dados**: Certifique-se de que a pasta `Ecommerce_Dataset` com os arquivos CSV (`customers.csv`, `products.csv`, `orders.csv`, `order_items.csv`, `rfm_segmentation.csv`) esteja na raiz do repositório clonado. Se não tiver os dados, os notebooks `Gerador_de_dados.ipynb` e `Análise_de_Dados.ipynb` explicam como gerá-los e prepará-los.

5.  **Execute o Dashboard Streamlit**:
    ```bash
    [cite_start]streamlit run dashboard.py [cite: 33]
    ```
    Isso abrirá o dashboard em seu navegador padrão.

## Dashboard Online (Live Demo)

[cite_start]Você pode acessar a versão hospedada do dashboard interativo através do Render: [https://ecommerce-dashboard-zwqm.onrender.com](https://ecommerce-dashboard-zwqm.onrender.com) [cite: 5, 37]

## Principais Insights e Análises

O projeto revelou insights importantes sobre o e-commerce:

* **Sazonalidade de Vendas**: A receita mensal mostra um padrão sazonal claro, com picos notáveis em novembro e dezembro, indicando a influência de períodos de vendas sazonais.
* **Distribuição Geográfica**: A receita é significativamente liderada por um estado específico, mostrando a importância de análises regionais para campanhas direcionadas.
* **Segmentação de Clientes**: A segmentação RFM permite identificar e focar em diferentes perfis de clientes (VIP, Regular, Ocasional, Inativo), possibilitando estratégias de marketing e retenção mais eficazes.
* **Performance de Produtos e Categorias**: Identificação dos top 5 produtos e das categorias de maior receita, auxiliando em decisões de estoque e promoções.

## Autor

* **André Victor**
    * [cite_start]Email: andre_victor_m@hotmail.com [cite: 4]
    * [cite_start]Telefone: (21) 976557279 [cite: 4]
    * [cite_start]Repositório Git: [https://github.com/andrevictorm/Visualiza-o-de-dados-Render](https://github.com/andrevictorm/Visualiza-o-de-dados-Render) [cite: 6]

## Agradecimentos

[cite_start]Este projeto foi desenvolvido como um teste técnico proposto por @Sidinei Andrade. [cite: 39] [cite_start]A estrutura do desafio e os dados de exemplo fornecidos foram cruciais para a execução e o aprendizado contínuo. [cite: 41, 54]
