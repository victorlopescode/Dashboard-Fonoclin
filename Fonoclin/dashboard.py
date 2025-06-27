import pandas as pd
import streamlit as st


uploaded_file = st.file_uploader(
    "Fonoclin\dados_fonoclin.xlsx", accept_multiple_files=False)
if uploaded_file is not None:
    file_name = uploaded_file
else:
    file_name = "Fonoclin\dados_fonoclin.xlsx"

df = pd.read_excel('Fonoclin\dados_fonoclin.xlsx')

df = df.iloc[3:].reset_index(drop=True)
df = df.drop(df.columns[0] ,axis=1)
df = df.drop(df.columns[4] ,axis=1)
col_data = df.columns[0]
df[col_data] = pd.to_datetime(df[col_data]).dt.date  # Mantém só a data, remove o horário

df.columns = ['Data', 'Horário', 'Paciente', 'Atendimento', 'Profissional', 'Especialidade', 'Token', 'Valor Empresa', 'Valor Profissional', 'Saldo Empresa']

# Ajusta a coluna 'Horário' para mostrar apenas no formato HH:MM
df['Horário'] = pd.to_datetime(df['Horário'].astype(str), errors='coerce').dt.strftime('%H:%M')

# Funções auxiliares
def filtrar_dados(df, meses, profissionais):
    df_filtrado = df.copy()
    if meses:
        df_filtrado = df_filtrado[df_filtrado['Data'].apply(lambda d: d.strftime('%B')).isin(meses)]
    if profissionais:
        df_filtrado = df_filtrado[df_filtrado['Profissional'].isin(profissionais)]
    return df_filtrado

def calcular_kpis(df):
    faturamento = df['Valor Empresa'].sum()
    despesa = df['Valor Profissional'].sum()
    lucro = df['Saldo Empresa'].sum()
    return faturamento, despesa, lucro

def atendimentos_por_profissional(df):
    return df.groupby('Profissional').size().sort_values(ascending=False)

def faltas_por_profissional(df):
    return df[df['Atendimento'].str.lower() == 'falta'].groupby('Profissional').size()

# Streamlit App
st.set_page_config(page_title="Dashboard Fonoclin", layout="wide")
st.title("Fonoclin")

# Filtros gerais
# Mapeamento dos meses em inglês para português
meses_pt = {
    'January': 'Janeiro', 'February': 'Fevereiro', 'March': 'Março', 'April': 'Abril',
    'May': 'Maio', 'June': 'Junho', 'July': 'Julho', 'August': 'Agosto',
    'September': 'Setembro', 'October': 'Outubro', 'November': 'Novembro', 'December': 'Dezembro'
}
meses_ingles = df['Data'].apply(lambda d: d.strftime('%B'))
meses_unicos = meses_ingles.unique().tolist()
meses_unicos_pt = [meses_pt[m] for m in meses_unicos]

# Seleção dos meses em português
meses_selecionados_pt = st.multiselect("Mês", meses_unicos_pt, default=meses_unicos_pt)
# Converter seleção de volta para inglês para filtrar corretamente
meses_selecionados = [k for k, v in meses_pt.items() if v in meses_selecionados_pt]

# Lista de profissionais únicos para o seletor
profissionais = df['Profissional'].dropna().unique().tolist()

# Novo seletor: Geral ou por profissional
opcao_filtro = st.radio("Visualizar dados de:", ["Fonoclin", "Profissional"])

if opcao_filtro == "Profissional":
    profissional_escolhido = st.selectbox("Selecione o Profissional", profissionais)
    df_filtrado = filtrar_dados(df, meses_selecionados, [profissional_escolhido])
else:
    profissional_escolhido = None
    df_filtrado = filtrar_dados(df, meses_selecionados, [])

# KPIs
faturamento, despesa, lucro = calcular_kpis(df_filtrado)
qtd_atendimentos = len(df_filtrado)
qtd_faltas = df_filtrado['Token'].astype(str).str.strip().str.lower().str.contains('faltou').sum()


# Mostra os números em cards
col1, col2, col3, col4 = st.columns(4)
col1.metric("Faturamento Empresa", f"R$ {faturamento:,.2f}")
col2.metric("Despesa com Profissional", f"R$ {despesa:,.2f}")
col3.metric("Lucro Empresa", f"R$ {lucro:,.2f}")
col4.metric("Qtd. Atendimentos", qtd_atendimentos)

st.metric("Quantidade de Faltas", qtd_faltas)

# Tabela detalhada dos atendimentos
st.subheader("Detalhamento dos Atendimentos")
st.dataframe(df_filtrado[['Data', 'Horário', 'Paciente', 'Atendimento', 'Especialidade', 'Valor Empresa', 'Valor Profissional', 'Saldo Empresa']])

