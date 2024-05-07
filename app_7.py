import timeit
import pandas            as pd
import streamlit         as st
import seaborn           as sns
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from PIL                 import Image
from io                  import BytesIO

# Set no tema do seaborn para melhorar o visual dos plots
custom_params = {"axes.spines.right": False, "axes.spines.top": False}
sns.set_theme(style="ticks", rc=custom_params)

# Função para ler os dados - ex2
@st.cache_data
def load_data(file_data):
    try:
        return pd.read_csv(file_data, sep=';')
    except:
        return pd.read_excel(file_data)
    
# Função para filtrar baseado na multiseleção de categorias
@st.cache_data
def multiselect_filter(relatorio, col, selecionados):
    if 'all' in selecionados:
        return relatorio
    else:
        return relatorio[relatorio[col].isin(selecionados)].reset_index(drop=True)
    
# Configuração para evitar que o Streamlit ajuste automaticamente o tamanho dos gráficos
st.set_option('deprecation.showPyplotGlobalUse', False)

# Função para converter o df para csv -ex2
@st.cache
def convert_df(df):
    return df.to_csv(index=False).encode('utf-8')

# Função para converter o df para excel -ex2
def to_excel(df, file_name):
    file_path = file_name + '.xlsx'
    writer = pd.ExcelWriter(file_path, engine='xlsxwriter')
    df.to_excel(writer, index=False, sheet_name='Sheet1')
    writer.close()  # Close the ExcelWriter to save the file
    return file_path


# Função principal da aplicação
def main():
    st.set_page_config(page_title = 'Telemarketing Analysis', \
        page_icon = '../img/telmarketing_icon.png',
        #layout="wide",
        initial_sidebar_state='expanded'
    )

    # Estilo da página
    st.markdown("""
<style>
    h1 {
        color: #26547C;
        text-align: left;
    }
    h2 {
        color: #407FB7;
        border-bottom: 1px solid #407FB7;
    }
    h3 {
        color: #4A90E2;
        text-align: center;    
    }
    p {
        color: #333333;
    }
</style>
""", unsafe_allow_html=True)

    # Título principal da aplicação
    st.write('# Telemarketing Data Analysis')
    st.markdown("---")

    # Apresenta a imagem na barra lateral da aplicação
    image = Image.open("../img/side-image.png")
    st.sidebar.image(image)

    # Botão para carregar arquivo na aplicação -ex2
    st.sidebar.write("## Upload File")
    data_file_1 = st.sidebar.file_uploader("Bank marketing data", type = ['csv','xlsx'])

    # Verifica se há conteúdo carregado na aplicação
    if (data_file_1 is not None):
        bank_raw = load_data(data_file_1)
        bank = bank_raw.copy()

        #Exibindo a tabela original sem filtros
        st.write('## Before filters')
        st.write(bank_raw.head())

        with st.sidebar.form(key='my_form'):
        
            # SELECIONA O TIPO DE GRÁFICO
            graph_type = st.radio('Plot Type:', ('Bar', 'Pie'))

            # IDADES
            max_age = int(bank.age.max())
            min_age = int(bank.age.min())
            idades = st.slider(label='Age', 
                                min_value = min_age,
                                max_value = max_age, 
                                value = (min_age, max_age),
                                step = 1)
        
            # PROFISSÕES
            jobs_list = bank.job.unique().tolist()
            jobs_list.append('all')
            jobs_selected =  st.multiselect("Job", jobs_list, ['all'])

            # ESTADO CIVIL
            marital_list = bank.marital.unique().tolist()
            marital_list.append('all')
            marital_selected =  st.multiselect("Marital status", marital_list, ['all'])

            # DEFAULT?
            default_list = bank.default.unique().tolist()
            default_list.append('all')
            default_selected =  st.multiselect("Default", default_list, ['all'])

            
            # TEM FINANCIAMENTO IMOBILIÁRIO?
            housing_list = bank.housing.unique().tolist()
            housing_list.append('all')
            housing_selected =  st.multiselect("Housing?", housing_list, ['all'])

            
            # TEM EMPRÉSTIMO?
            loan_list = bank.loan.unique().tolist()
            loan_list.append('all')
            loan_selected =  st.multiselect("Loan?", loan_list, ['all'])

            
            # MEIO DE CONTATO?
            contact_list = bank.contact.unique().tolist()
            contact_list.append('all')
            contact_selected =  st.multiselect("Contact", contact_list, ['all'])

            
            # MÊS DO CONTATO
            month_list = bank.month.unique().tolist()
            month_list.append('all')
            month_selected =  st.multiselect("Month", month_list, ['all'])

            
            # DIA DA SEMANA
            day_of_week_list = bank.day_of_week.unique().tolist()
            day_of_week_list.append('all')
            day_of_week_selected =  st.multiselect("Day of week", day_of_week_list, ['all'])

            # encadeamento de métodos para filtrar a seleção
            bank = (bank.query("age >= @idades[0] and age <= @idades[1]")
                        .pipe(multiselect_filter, 'job', jobs_selected)
                        .pipe(multiselect_filter, 'marital', marital_selected)
                        .pipe(multiselect_filter, 'default', default_selected)
                        .pipe(multiselect_filter, 'housing', housing_selected)
                        .pipe(multiselect_filter, 'loan', loan_selected)
                        .pipe(multiselect_filter, 'contact', contact_selected)
                        .pipe(multiselect_filter, 'month', month_selected)
                        .pipe(multiselect_filter, 'day_of_week', day_of_week_selected)
            )
                
            submit_button = st.form_submit_button(label='Apply')

    
    # Botões de download dos dados filtrados -ex2
    st.write('## After Filters')
    st.write(bank.head())

    st.cache_data    
    file_name = 'bank_filtered'
    excel_file_path = to_excel(bank, file_name)
    st.download_button(label='📥 Download filtered data in EXCEL', 
                       data=open(excel_file_path, 'rb'), 
                       file_name=file_name + '.xlsx')
    st.markdown("---")

    st.write('## Acceptance Proportion')
    # PLOTS   
    
    fig, ax = plt.subplots(1, 2, figsize = (10,6))
    color_map= ListedColormap(['lightblue', 'lightsalmon'])
    custom_palette = ['lightblue', 'lightsalmon']

    bank_raw_target_perc = bank_raw.y.value_counts(normalize = True).to_frame()*100
    bank_raw_target_perc = bank_raw_target_perc.sort_index()

    try:
        bank_target_perc = bank.y.value_counts(normalize = True).to_frame()*100
        bank_target_perc = bank_target_perc.sort_index()
    except:
        st.error('Erro no filtro')

    # Botões de download dos dados dos gráficos
    col1, col2 = st.columns(2)

    st.cache_data
    # Save 'bank_raw_target_perc' to Excel and create download button
    file_path_raw = to_excel(bank_raw_target_perc, 'bank_raw_y')
    st.download_button(label='📥 Download Original', data=open(file_path_raw, 'rb'), file_name='bank_raw_y.xlsx')

    # Save 'bank_target_perc' to Excel and create download button
    file_path_filtered = to_excel(bank_target_perc, 'bank_y')
    st.download_button(label='📥 Download Filtered', data=open(file_path_filtered, 'rb'), file_name='bank_y.xlsx')
    st.markdown("---")    

    if graph_type == 'Barras':
        sns.barplot(x = bank_raw_target_perc.index, 
                    y = 'proportion',
                    data = bank_raw_target_perc, 
                    ax = ax[0],
                    palette=custom_palette)
        ax[0].bar_label(ax[0].containers[0])
        ax[0].set_title('Original Data',
                        fontweight ="bold")
            
        sns.barplot(x = bank_target_perc.index, 
                    y = 'proportion', 
                    data = bank_target_perc, 
                    ax = ax[1],
                    palette=custom_palette)
        ax[1].bar_label(ax[1].containers[0])
        ax[1].set_title('Filtered Data',
                        fontweight ="bold")
    else:
        
        bank_raw_target_perc.plot(kind='pie', autopct='%.2f', y='proportion', ax = ax[0], colormap=color_map)
        ax[0].set_title('Original Data',
                        fontweight ="bold")
            
        bank_target_perc.plot(kind='pie', autopct='%.2f', y='proportion', ax = ax[1], colormap=color_map)
        ax[1].set_title('Filtered Data',
                        fontweight ="bold")

    st.pyplot(plt)

    
        


if __name__ == '__main__':
	main()