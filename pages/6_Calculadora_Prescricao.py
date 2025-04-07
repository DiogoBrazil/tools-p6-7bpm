import streamlit as st
import datetime
from dateutil.relativedelta import relativedelta
import pandas as pd

# --- Configuração da Página ---
st.set_page_config(
    page_title="Calculadora Prescrição - 7ºBPM/P-6",
    page_icon="⏳",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- Estilos CSS ---
st.write("""
<style>
    /* Esconde Sidebar */
    [data-testid="stSidebar"] { display: none !important; }
    /* Ajusta container principal */
    .block-container {
        max-width: 800px; /* Largura um pouco menor para formulário */
        padding-top: 1.5rem;
        padding-bottom: 2rem;
    }

    /* Estilos do Botão Voltar (copiado de outra página) */
    div.element-container:nth-child(1) { margin-top: 1rem !important; margin-bottom: 1.5rem !important; }
    div.element-container:nth-child(1) > .stButton > button {
        background-color: #f0f2f6 !important; color: #333 !important; border: 1px solid #d1d1d1 !important;
        font-weight: normal !important; box-shadow: none !important; width: auto !important;
        padding: 0.4rem 0.8rem !important; display: inline-block !important;
    }
    div.element-container:nth-child(1) > .stButton > button:hover {
        background-color: #e0e2e6 !important; color: #111 !important; border-color: #c1c1c1 !important;
        box-shadow: none !important;
    }
     div.element-container:nth-child(1) > .stButton > button:focus {
        box-shadow: 0 0 0 0.2rem rgba(211, 211, 211, 0.5) !important; outline: none;
    }

    /* Título e Descrição */
    h1 { text-align: center; margin-bottom: 0.5rem; font-size: 1.8rem; color: #333;}
    .stApp > .main .block-container > div:nth-child(1) > div > div > div > p.stCaption {
        text-align: center; margin-bottom: 2rem; color: #555; line-height: 1.5;
    }

    /* Campos de Data */
    div[data-testid="stDateInput"] {
        margin-bottom: 0.5rem; /* Espaço entre inputs */
    }

    /* Seção de Suspensão */
    .suspension-section {
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 1rem 1.5rem;
        margin-top: 1.5rem;
        background-color: #f8f9fa;
    }
    .suspension-section h3 {
        margin-top: 0;
        margin-bottom: 1rem;
        font-size: 1.1rem;
        color: #495057;
        border-bottom: 1px solid #dee2e6;
        padding-bottom: 0.5rem;
    }

    /* Botão Calcular */
    div.stButton button[kind="primary"] { /* Botão Calcular principal */
        margin-top: 1.5rem;
        background-color: #28a745; /* Verde */
        border-color: #28a745;
        font-size: 1.1rem;
        padding: 0.6rem 1.5rem;
    }
    div.stButton button[kind="primary"]:hover {
        background-color: #218838;
        border-color: #1e7e34;
    }

    /* Resultados */
    .result-container {
        margin-top: 2rem;
        padding: 1.5rem;
        border-radius: 8px;
        text-align: center;
        font-size: 1.1rem;
        font-weight: 500;
    }
    .result-success { /* Fundo Verde */
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
    }
    .result-error { /* Fundo Vermelho */
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
    }

</style>
""", unsafe_allow_html=True)

if st.button("← Voltar à página inicial", key="back_button_prescricao", type='primary'):
    st.switch_page("Home.py")

# --- Título e Descrição ---
st.title("⏳ Calculadora de Prescrição Disciplinar")
st.caption("Calcule a data limite para a prescrição de infrações disciplinares conforme as regras do RDPM. Preencha os campos abaixo.")

# --- Dicionários e Constantes ---
NATUREZA_PRAZOS = {
    "Leve": relativedelta(years=1),
    "Média": relativedelta(years=2),
    "Grave": relativedelta(years=5)
}
NATUREZA_OPTIONS = list(NATUREZA_PRAZOS.keys())
TODAY = datetime.date.today()

# --- Inputs Principais ---
col1, col2 = st.columns([2, 3]) # Coluna para natureza e data conhecimento

with col1:
    natureza = st.selectbox(
        "Natureza da Infração:",
        options=NATUREZA_OPTIONS,
        index=None, # Nenhum selecionado por padrão
        placeholder="Selecione a natureza..."
    )

with col2:
    data_conhecimento = st.date_input(
        "Data de Conhecimento do Fato:",
        value=None, # Começa vazio
        max_value=TODAY, # Não pode ser no futuro
        format="DD/MM/YYYY"
    )

data_instauracao = st.date_input(
    "Data de Instauração (Sindicância/Processo Disciplinar):",
    value=None,
    max_value=TODAY,
    format="DD/MM/YYYY",
    help="Data de abertura da Sindicância Regular ou instauração do Processo Disciplinar. Interrompe e reinicia a contagem."
)

# --- Seção de Suspensão ---
st.markdown("---") # Separador visual

# Inicializa a lista de suspensões na session_state se não existir
if 'suspensions' not in st.session_state:
    st.session_state.suspensions = []

suspensao_ocorreu = st.checkbox("Houve suspensão do prazo durante o processo?")

if suspensao_ocorreu:
    with st.container(border=True): # Usando container com borda
        st.subheader("🗓️ Registrar Períodos de Suspensão")

        col_susp_1, col_susp_2 = st.columns(2)
        with col_susp_1:
            susp_inicio = st.date_input("Data de Início da Suspensão:", key="susp_inicio", value=None, format="DD/MM/YYYY")
        with col_susp_2:
            susp_fim = st.date_input("Data de Fim da Suspensão:", key="susp_fim", value=None, format="DD/MM/YYYY")

        # Botão para adicionar a suspensão atual
        if st.button("➕ Adicionar Período de Suspensão", key="add_susp"):
            if susp_inicio and susp_fim:
                if susp_fim >= susp_inicio:
                    # Verifica se a suspensão começa DEPOIS da instauração
                    if data_instauracao and susp_inicio >= data_instauracao:
                         st.session_state.suspensions.append({"inicio": susp_inicio, "fim": susp_fim})
                         # Limpar campos após adicionar (opcional, mas melhora UX)
                         # Requer rerun ou truques mais complexos para limpar de fato
                         st.success(f"Período de {susp_inicio.strftime('%d/%m/%Y')} a {susp_fim.strftime('%d/%m/%Y')} adicionado.")
                    elif not data_instauracao:
                         st.warning("Por favor, informe a Data de Instauração antes de adicionar suspensões.")
                    else:
                         st.warning("A suspensão não pode começar antes da Data de Instauração.")

                else:
                    st.error("A data de fim da suspensão deve ser igual ou posterior à data de início.")
            else:
                st.warning("Preencha as datas de início e fim da suspensão.")

        # Exibi suspensões adicionadas
        if st.session_state.suspensions:
            st.markdown("**Períodos de Suspensão Registrados:**")
            # Usa pandas para formatar melhor
            susp_df_data = [{"Início": s["inicio"].strftime('%d/%m/%Y'), "Fim": s["fim"].strftime('%d/%m/%Y')} for s in st.session_state.suspensions]
            susp_df = pd.DataFrame(susp_df_data)
            st.dataframe(susp_df, hide_index=True, use_container_width=True)

            # Botão para remover a última suspensão
            if st.button("➖ Remover Último Período", key="remove_susp"):
                if st.session_state.suspensions:
                    removed = st.session_state.suspensions.pop()
                    st.info(f"Período de {removed['inicio'].strftime('%d/%m/%Y')} a {removed['fim'].strftime('%d/%m/%Y')} removido.")
                    st.rerun() # Atualiza a exibição imediatamente
                else:
                     st.info("Nenhum período para remover.")
else:
    # Limpa suspensões se o checkbox for desmarcado
    if st.session_state.suspensions:
        st.session_state.suspensions = []


# --- Botão de Cálculo e Resultados ---
st.markdown("---")
results_placeholder = st.empty()

if st.button("Calcular Prazo Prescricional", type="primary", use_container_width=True):
    valid_input = True
    if not natureza:
        results_placeholder.error("❌ Por favor, selecione a Natureza da Infração.")
        valid_input = False
    if not data_conhecimento:
        results_placeholder.error("❌ Por favor, informe a Data de Conhecimento do Fato.")
        valid_input = False
    if not data_instauracao:
        results_placeholder.error("❌ Por favor, informe a Data de Instauração.")
        valid_input = False

    if valid_input and data_conhecimento > data_instauracao:
         results_placeholder.error("❌ A Data de Instauração não pode ser anterior à Data de Conhecimento.")
         valid_input = False

    # --- Lógica de Cálculo ---
    if valid_input:
        prazo_base = NATUREZA_PRAZOS[natureza]

        # 1. Verifica prescrição ANTES da instauração (interrupção)
        prescricao_sem_interrupcao = data_conhecimento + prazo_base
        if data_instauracao >= prescricao_sem_interrupcao:
            results_placeholder.markdown(
                f"""
                <div class="result-container result-error">
                    ⚠️ <strong>PRESCRIÇÃO OCORRIDA (ANTES DA INSTAURAÇÃO)!</strong><br>
                    O prazo inicial ({natureza}) era de {prazo_base.years} ano(s) a partir de {data_conhecimento.strftime('%d/%m/%Y')}.<br>
                    A prescrição teria ocorrido em <strong>{prescricao_sem_interrupcao.strftime('%d/%m/%Y')}</strong>.<br>
                    A instauração em {data_instauracao.strftime('%d/%m/%Y')} foi posterior a essa data.
                </div>
                """, unsafe_allow_html=True
            )
        else:
            # 2. Calcula prazo a partir da data de instauração (interrupção)
            prescricao_base_interrompida = data_instauracao + prazo_base

            # 3. Calcula dias de suspensão
            total_dias_suspensao = datetime.timedelta(days=0)
            for susp in st.session_state.suspensions:
                duracao_susp = susp["fim"] - susp["inicio"] # Isso dá um timedelta
                if duracao_susp.days >= 0: # Garante que não seja negativo
                    total_dias_suspensao += duracao_susp # Soma os timedeltas

            # 4. Calcula data final com suspensões
            data_final_prescricao = prescricao_base_interrompida + total_dias_suspensao

            # 5. Compara com data atual e exibir resultado
            data_final_str = data_final_prescricao.strftime('%d/%m/%Y')
            total_dias_susp_str = total_dias_suspensao.days

            info_suspensao = f" ({total_dias_susp_str} dia(s) de suspensão adicionados)" if total_dias_susp_str > 0 else ""

            if data_final_prescricao < TODAY:
                # PRESCRIÇÃO OCORRIDA
                results_placeholder.markdown(
                    f"""
                    <div class="result-container result-error">
                        🚨 <strong>PRESCRIÇÃO OCORRIDA!</strong><br>
                        Considerando a natureza <strong>{natureza}</strong> ({prazo_base.years} ano(s)),
                        a interrupção em <strong>{data_instauracao.strftime('%d/%m/%Y')}</strong>{info_suspensao},
                        o prazo prescricional finalizou em <strong>{data_final_str}</strong>.
                    </div>
                    """, unsafe_allow_html=True
                )
            else:
                # DENTRO DO PRAZO
                results_placeholder.markdown(
                    f"""
                    <div class="result-container result-success">
                        ✅ <strong>DENTRO DO PRAZO PRESCRICIONAL</strong><br>
                        Considerando a natureza <strong>{natureza}</strong> ({prazo_base.years} ano(s)),
                        a interrupção em <strong>{data_instauracao.strftime('%d/%m/%Y')}</strong>{info_suspensao},
                        o prazo prescricional se encerrará em <strong>{data_final_str}</strong>.
                    </div>
                    """, unsafe_allow_html=True
                )

# --- Rodapé ---
st.markdown("---")
st.markdown("""
<div style="margin-top: 3rem; padding-top: 1rem; border-top: 1px solid #e6e6e6; text-align: center; font-size: 0.9rem; color: #666;">
    <p>© 2024 - Seção de Justiça e Disciplina - 7º Batalhão de Polícia Militar</p>
    <p>Desenvolvido pelo 1º SGT QPPM Mat. ******023 DIOGO <strong>RIBEIRO</strong></p>
</div>
""", unsafe_allow_html=True)
