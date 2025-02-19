import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

# Leitura dos arquivos CSV
df_volei = pd.read_csv('multiTimeline_Vôlei.csv', skiprows=1)
df_superliga = pd.read_csv('multiTimeline_Superliga de Vôlei.csv', skiprows=1)
df_olimpiadas = pd.read_csv('multiTimeline_Olimpíadas.csv', skiprows=1)
df_liga = pd.read_csv('multiTimeline_Liga das Nações.csv', skiprows=1)

# Ajustando as colunas e datas
df_volei.columns = ['Semana', 'Volei']
df_superliga.columns = ['Semana', 'Superliga']
df_olimpiadas.columns = ['Semana', 'Olimpiadas']
df_liga.columns = ['Semana', 'Liga_Nacoes']

df_volei['Semana'] = pd.to_datetime(df_volei['Semana'])
df_superliga['Semana'] = pd.to_datetime(df_superliga['Semana'])
df_olimpiadas['Semana'] = pd.to_datetime(df_olimpiadas['Semana'])
df_liga['Semana'] = pd.to_datetime(df_liga['Semana'])

# Tratamento de dados
df_olimpiadas.replace('<1', 0, inplace=True)
df_liga.replace('<1', 0, inplace=True)
df_olimpiadas['Olimpiadas'] = df_olimpiadas['Olimpiadas'].astype(int)
df_liga['Liga_Nacoes'] = df_liga['Liga_Nacoes'].astype(int)

# Filtragem de dados
df_volei_filtrado = df_volei[df_volei['Semana'] >= '2022-01-01']
df_superliga_filtrado = df_superliga[df_superliga['Semana'] >= '2022-01-01']
df_olimpiadas_filtrado = df_olimpiadas[df_olimpiadas['Semana'] >= '2022-01-01']
df_liga_filtrado = df_liga[df_liga['Semana'] >= '2022-01-01']

# Combinação de todos os DataFrames
df_final = df_volei_filtrado.merge(df_superliga_filtrado, on='Semana', how='outer')\
                   .merge(df_olimpiadas_filtrado, on='Semana', how='outer')\
                   .merge(df_liga_filtrado, on='Semana', how='outer')

# Preenchendo valores faltantes
df_final.fillna(0, inplace=True)

# Convertendo as colunas para int
df_final.iloc[:, 1:] = df_final.iloc[:, 1:].astype(int)

# Criando a coluna de Ano
df_final['Ano'] = df_final['Semana'].dt.year

# Streamlit Dashboard
st.title('Análise da Popularidade do Vôlei')
st.markdown('Este dashboard explora a popularidade do Vôlei ao longo do tempo usando dados do Google Trends.')

# Filtragem
anos = sorted(df_final['Semana'].dt.year.unique())
ano_selecionado = st.sidebar.selectbox('Selecione o Ano', anos)

# Removendo a coluna "Ano" da lista de eventos
eventos = df_final.columns[1:-1]

# Se o ano selecionado for 2023 ou 2025, remove "Olimpíadas" da seleção por falta de dados
if ano_selecionado in [2023, 2025]:
    eventos = [evento for evento in eventos if evento != 'Olimpiadas']

eventos_selecionados = st.sidebar.multiselect('Selecione Eventos', eventos, default=eventos)

# Filtrar dados para o ano selecionado mantendo a coluna "Semana"
df_ano = df_final[df_final['Semana'].dt.year == ano_selecionado].copy()

# Se não houver dados para o ano selecionado, mostrar aviso
if df_ano.empty:
    st.write(f"⚠️ Não há dados disponíveis para o ano {ano_selecionado}. Selecione outro ano.")
else:
    df_ano = df_ano[['Semana'] + eventos_selecionados]

    # Correlação com Matplotlib
    st.subheader(f'Correlação dos Eventos em {ano_selecionado}')
    correlacao = df_ano.drop(columns=['Semana']).corr()

    if (correlacao.sum() != 0).all():
        plt.figure(figsize=(10, 6))
        sns.heatmap(correlacao, annot=True, cmap='coolwarm')
        plt.title(f'Correlação em {ano_selecionado}')
        st.pyplot(plt.gcf())
    else:
        st.write('Não há dados suficientes para calcular a correlação neste ano.')

    # Análise de Popularidade ao Longo do Tempo
    st.subheader(f'Popularidade ao Longo do Tempo em {ano_selecionado}')

    # Melhorando o gráfico
    plt.figure(figsize=(14, 7))
    for evento in eventos_selecionados:
        plt.plot(df_ano['Semana'], df_ano[evento], label=evento, marker='o', linestyle='-', markersize=4)

    plt.xlabel('Semana', fontsize=12)
    plt.ylabel('Popularidade', fontsize=12)
    plt.title(f'Evolução da Popularidade dos Eventos Selecionados em {ano_selecionado}', fontsize=16)
    plt.xticks(rotation=45, ha='right')  
    plt.legend(title='Eventos', fontsize=10)
    plt.grid(True)

    # Exibir o gráfico
    st.pyplot(plt.gcf())
