import streamlit as st
import pandas as pd
from datetime import datetime

# Função para criar conexão
def create_connection():
    connection = None
    try:
        connection = st.experimental_connection('main_db', type='sql')
    except Exception as e:
        print(f"Error connecting to database: {e}")
    
    return connection

# Funções para manipulação de dados
def insert_data(connection, data):
    insert_func = connection.query('INSERT INTO main_db (Log, Data, Descricao, Valor_R$, Banco, Forma_de_pagamento, Categoria) VALUES (%s, %s, %s, %s, %s, %s, %s)')
    return st.dataframe(insert_func)

def delete_data(connection, record_id):
    delete_func = connection.query('DELETE FROM main_db WHERE `Index` = %s')
    return st.dataframe(delete_func)

def read_data(connection):
    read_func =  connection.query('SELECT * FROM main_db')
    return st.dataframe(read_func)

# Função para leitura de dados com filtros
def get_filtered_data(connection, date_range=None, category=None, min_value=None, max_value=None, bank=None, payment_method=None):
    query1 = "SELECT * FROM main_db WHERE 1=1"
    # Condições dinâmicas baseadas nos filtros preenchidos
    conditions = []
    params = []

    if date_range and len(date_range) == 2:
        conditions.append("Data BETWEEN %s AND %s")
        params.extend(date_range)
    if category:
        conditions.append("Categoria = %s")
        params.append(category)
    if min_value is not None and min_value > 0:
        conditions.append("Valor_R$ >= %s")
        params.append(min_value)
    if max_value is not None and max_value > 0:
        conditions.append("Valor_R$ <= %s")
        params.append(max_value)
    if bank:
        conditions.append("Banco = %s")
        params.append(bank)
    if payment_method:
        conditions.append("Forma_de_pagamento = %s")
        params.append(payment_method)

    # Monta a query final com filtros
    if conditions:
        query1 += " AND " + " AND ".join(conditions)
    filter_func = connection.query(query1)
    return st.dataframe(filter_func)

# Função para exibir dashboard
def show_dashboard(connection):
    # Obtém as datas do primeiro dia do mês e a data atual
    today = datetime.now()
    first_day_of_month = today.replace(day=1)
    
    # Realiza a consulta para somar o valor dos gastos no intervalo
    query2 = "SELECT SUM(Valor_R$) as total_gasto FROM main_db WHERE Data BETWEEN %s AND %s"
    dashboard_func = connection.query(query2)
    
    # Retorna o total dos gastos
    return dashboard_func if dashboard_func is not None else 0

def show_total_banco(connection):
    today = datetime.now()
    first_day_of_month = today.replace(day=1)
    
    # Consulta SQL que agrupa e soma os gastos por banco
    query3 = "SELECT Banco, SUM(Valor_R$) as total_gasto FROM main_db WHERE Data BETWEEN %s AND %s GROUP BY Banco"
    banco_func = connection.query(query3)
    return st.dataframe(banco_func)

def show_total_cat(connection):
    today = datetime.now()
    first_day_of_month = today.replace(day=1)
    
    # Consulta SQL que agrupa e soma os gastos por categoria
    query4 = "SELECT Categoria, SUM(Valor_R$) as total_cat FROM main_db WHERE Data BETWEEN %s AND %s GROUP BY Categoria"
    cat_func = connection.query(query4)
    return st.dataframe(cat_func)
    


# Interface Streamlit
st.set_page_config(page_title="App Finanças Pessoais", layout="wide", initial_sidebar_state="expanded")

# Exibir a imagem de fundo como um banner no topo da página


st.logo('logo.png', size='large',icon_image='logoicon.png')
st.title("Finance Control App")
st.write("Gerencie suas finanças de forma prática e interativa.")

menu = ["Inserir Dados","Filtrar/Deletar Dados", "Consultar Dados", "Dashboards", "Sair"]

choice = st.sidebar.radio("Menu", menu)

conn = create_connection()

if choice == "Inserir Dados":
    st.header("Inserir Dados")
    #with st.expander("Formulário de Inserção"):
    log = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Data e hora atual
    st.text_input("Log", log, disabled=True)  # Campo não editável
    data = st.date_input("Data")  # Usando o seletor de data do Streamlit
    descricao = st.text_input("Descrição")
    valor = st.number_input("Valor R$", min_value=0.0, format="%.2f")
    banco = st.selectbox("Banco", ["Nubank", "Next - R", "C6", "Next - L", "Itau - R", "Itau - L"])
    forma_pagamento = st.selectbox("Forma de Pagamento", ["Débito", "Pix", "Crédito"])
    categoria = st.selectbox("Categoria", ["Casa", "Supermercado", "Restaurante", "Ifood", "Saúde", "Carro", "Pessoal", "Educação", "Lazer", "Viagem", "Assinaturas"])

    if st.button("Inserir"):
        insert_data(conn, (log, data, descricao, valor, banco, forma_pagamento, categoria))
        st.success("Dados inseridos com sucesso!")

elif choice == "Filtrar/Deletar Dados":
    st.header("Filtrar Dados")
    #with st.expander("Filtrar Dados"):
    date_range = st.date_input("Selecione o intervalo de datas", [])
    category = st.selectbox("Categoria", ["","Casa", "Supermercado", "Restaurante", "Ifood", "Saúde", "Carro", "Pessoal", "Educação", "Lazer", "Viagem", "Assinaturas"])
    min_value = st.number_input("Valor mínimo", min_value=0.0, format="%.2f")
    max_value = st.number_input("Valor máximo", min_value=0.0, format="%.2f")
    bank = st.selectbox("Banco", ["","Nubank", "Next - R", "C6", "Next - L", "Itau - R", "Itau - L"])
    payment_method = st.selectbox("Forma de Pagamento", ["","Débito", "Pix", "Crédito"])
           
    if st.button("Filtrar"):
        data = get_filtered_data(
            conn,
            date_range=date_range if len(date_range) == 2 else None,
            category=category if category else None,
            min_value=min_value if min_value > 0 else None,
            max_value=max_value if max_value > 0 else None,
            bank=bank if bank else None,
            payment_method=payment_method if payment_method else None
    )
        st.write("Registros Filtrados:")
        st.dataframe(data)
        
    st.divider()
        
    
    with st.expander("Formulário de Deleção"):
        st.write("Deletar Dados")
        record_id = st.number_input("ID do Registro", min_value=1, step=1)
        if st.button("Deletar"):
            delete_data(conn, record_id)
            st.success("Dados deletados com sucesso!")
        

elif choice == "Deletar Dados":
    st.header("Deletar Dados")
    #with st.expander("Formulário de Deleção"):
    

elif choice == "Consultar Dados":
    st.header("Consultar Dados")
    #with st.expander("Tabela de Dados"):
    data = read_data(conn)
    df = pd.DataFrame(data, columns=["Index", "Log", "Data", "Descrição", "Valor R$", "Banco", "Forma de Pagamento", "Categoria"])
    st.dataframe(df)

elif choice == "Dashboards":
    st.header("Dashboards")
    show_dashboard(conn)
    total_gasto = show_dashboard(conn)
    st.metric(label="Gasto Total (Mês Atual)", value=f"R$ {total_gasto:.2f}")
    
    expenses_by_cat = show_total_cat(conn)
    if not expenses_by_cat.empty:
        today = datetime.now()
        first_day_of_month = today.replace(day=1)
        today_formatted = today.strftime("%d/%m")
        first_day_of_month_formatted = first_day_of_month.strftime("%d/%m")
        # Cria o gráfico de barras
        # Bar chart 1: Valor_R$ by Categoria
        st.bar_chart(expenses_by_cat.set_index('Categoria'))


    else:
        st.write("Nenhum gasto encontrado para o mês atual.")
    
    expenses_by_bank = show_total_banco(conn)
    if not expenses_by_bank.empty:
        today = datetime.now()
        first_day_of_month = today.replace(day=1)
        today_formatted = today.strftime("%d/%m")
        first_day_of_month_formatted = first_day_of_month.strftime("%d/%m")
        # Cria o gráfico de barras
        # Bar chart 2: Valor_R$ by Banco
        st.bar_chart(expenses_by_bank.set_index('Banco'))
      
    else:
        st.write("Nenhum gasto encontrado para o mês atual.")
        
elif choice == "Sair":
    if st.button('Sair'):
        if conn is not None and conn.is_connected():
            conn.close()
            st.text("Conexão encerrada.")


