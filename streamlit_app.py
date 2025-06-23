import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
from banco import meusqldb
from main import main as main_outra

# --- Configuração da Página ---
st.set_page_config(
    page_title="Dashboard de Atividade Geomagnética",
    page_icon="🌌",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CSS Personalizado ---
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .stMetric {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 5px solid #1f77b4;
    }
    /* Correção para texto branco em fundo claro nos totalizadores (KPIs) */
    .stMetric [data-testid="stMetricLabel"] {
        color: #31333F; /* Cor mais escura para o rótulo */
    }
    .stMetric [data-testid="stMetricValue"] {
        color: #0d0d0d; /* Cor preta para o valor */
    }
</style>
""", unsafe_allow_html=True)

# --- Funções de Apoio ---
@st.cache_data(ttl=300)
def get_and_prepare_data():
    """Busca e prepara os dados do banco."""
    try:
        conn = meusqldb('root', 'MinhaSenhaSegura', '127.0.0.1', '3306', 'Banco_geral')
        kp_indices = conn.selecionar_dados('kp_indices')
        
        if not kp_indices:
            return None, None

        df = pd.DataFrame(kp_indices)
        df['time_tag'] = pd.to_datetime(df['time_tag'])
        
        def get_kp_level(kp_index):
            if kp_index <= 2: return "Calmo"
            if kp_index == 3: return "Instável"
            if kp_index == 4: return "Ativo"
            return "Tempestade"
            
        df['kp_level'] = df['kp_index'].apply(get_kp_level)
        
        now = datetime.now()
        df_hist = df[df['time_tag'] <= now].copy()
        df_prev = df[df['time_tag'] > now].copy()
        
        return df_hist, df_prev
    except Exception as e:
        st.error(f"Erro ao buscar dados: {e}")
        return None, None

def handle_data_update():
    """
    Função callback para ser executada ao clicar no botão.
    Ela atualiza os dados e armazena uma mensagem de status no st.session_state.
    """
    try:
        with st.spinner("Buscando novos dados das APIs..."):
            main_instance = main_outra()
            main_instance.main()
        st.cache_data.clear()
        st.session_state.update_message = {
            "type": "success", 
            "text": "Dados atualizados com sucesso!"
        }
    except Exception as e:
        st.session_state.update_message = {
            "type": "error",
            "text": f"Falha ao atualizar dados: {e}"
        }

# --- Interface Principal ---
def main():
    # --- Cabeçalho e Botões de Informação ---
    col_title, col_info, col_help = st.columns([0.8, 0.1, 0.1])
    with col_title:
        st.markdown('<h1 class="main-header">Dashboard de Atividade Geomagnética (Índice Kp)</h1>', unsafe_allow_html=True)
    with col_info:
        with st.popover("ℹ️ Info", use_container_width=True):
            st.markdown("""
            ### O que é o Índice Kp?
            
            O **Índice Kp** é uma medida global da atividade geomagnética, que indica a magnitude das perturbações no campo magnético da Terra. Ele é essencial para monitorar o "clima espacial".
            
            **Escala de Medição:**
            A escala vai de 0 a 9:
            - **0-2 (Calmo):** Condições tranquilas.
            - **3 (Instável):** Pequenas perturbações.
            - **4 (Ativo):** Atividade moderada.
            - **5+ (Tempestade):** Indica uma tempestade geomagnética.
            
            **Impactos de Tempestades:**
            - Interferência em rádio, degradação de GPS, risco a satélites e redes elétricas, e auroras visíveis.
            """)
    with col_help:
        with st.popover("❔ Como funciona?", use_container_width=True):
            st.markdown("""
            ### Guia Rápido do Dashboard
            
            **1. Use os Filtros na Barra Lateral ⬅️**
            - **Período:** Selecione um intervalo de datas para sua análise.
            - **Nível de Atividade:** Filtre por um ou mais níveis (de Calmo a Tempestade).
            
            **2. Analise os Indicadores (KPIs) no Topo**
            - Os cartões mostram um resumo dos dados filtrados, como a média e o pico do Kp.
            
            **3. Explore os Gráficos 📊**
            - **Série Temporal:** Acompanhe a evolução do Kp.
            - **Distribuição:** Veja a frequência de cada nível.
            - **Proporção de Atividade:** Entenda a composição da atividade.
            - **Top 10 Recentes:** Compare os valores dos últimos registros.
            
            **4. Atualize os Dados 🔄**
            - Clique no botão na barra lateral para buscar os dados mais recentes.
            """)

    # Exibe e limpa a mensagem de status da atualização
    if "update_message" in st.session_state:
        message = st.session_state.update_message
        if message["type"] == "success":
            st.success(message["text"])
        else:
            st.error(message["text"])
        del st.session_state.update_message

    # --- Carregar Dados ---
    df_hist, df_prev = get_and_prepare_data()

    if df_hist is None or df_hist.empty:
        st.warning("Nenhum dado histórico encontrado.")
        if st.button("Buscar dados na fonte"):
            with st.spinner("Atualizando..."):
                main_instance = main()
                main_instance.main()
                st.cache_data.clear()
                st.rerun()
        return

    # --- Barra Lateral com Filtros ---
    st.sidebar.header("Filtros do Dashboard")

    min_date = df_hist['time_tag'].min().date()
    max_date = df_hist['time_tag'].max().date()

    date_range = st.sidebar.date_input(
        "Selecione o Período",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
        key="date_range_picker"
    )

    if len(date_range) != 2:
        st.sidebar.warning("Por favor, selecione um período de início e fim.")
        st.stop()

    start_datetime = datetime.combine(date_range[0], datetime.min.time())
    end_datetime = datetime.combine(date_range[1], datetime.max.time())
    
    level_options = df_hist['kp_level'].unique()
    selected_levels = st.sidebar.multiselect(
        "Filtre por Nível de Atividade",
        options=level_options,
        default=level_options,
        placeholder="Selecione os níveis",
        key="level_multiselect"
    )
    
    st.sidebar.button(
        "Atualizar Dados da Fonte", 
        use_container_width=True, 
        type="primary", 
        on_click=handle_data_update
    )

    # --- Aplicar Filtros ---
    filtered_df = df_hist[
        (df_hist['time_tag'] >= start_datetime) &
        (df_hist['time_tag'] <= end_datetime) &
        (df_hist['kp_level'].isin(selected_levels))
    ]

    if filtered_df.empty:
        st.warning("Nenhum dado encontrado para os filtros selecionados.")
        st.stop()

    # --- Totalizadores (KPIs) ---
    st.subheader("Resumo do Período Selecionado")
    avg_kp = filtered_df['estimated_kp'].mean()
    max_kp = filtered_df['estimated_kp'].max()
    storm_records = len(filtered_df[filtered_df['kp_index'] >= 5])
    total_records = len(filtered_df)

    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    kpi1.metric("Média Kp (Estimado)", f"{avg_kp:.2f}")
    kpi2.metric("Máximo Kp (Estimado)", f"{max_kp:.2f}")
    kpi3.metric("Registros de Tempestade (Kp≥5)", f"{storm_records}")
    kpi4.metric("Total de Registros", f"{total_records}")

    st.markdown("---")

    # --- Gráficos (Grid 2x2) ---
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Série Temporal do Índice Kp")
        fig_line = go.Figure()
        fig_line.add_trace(go.Scatter(x=filtered_df['time_tag'], y=filtered_df['estimated_kp'], mode='lines', name='Histórico'))
        
        # Só exibe a previsão se o período selecionado incluir a data atual ou futura
        if date_range[1] >= datetime.now().date() and not df_prev.empty:
            fig_line.add_trace(go.Scatter(x=df_prev['time_tag'], y=df_prev['estimated_kp'], mode='lines', name='Previsão', line=dict(dash='dash')))
        
        fig_line.update_layout(height=350, margin=dict(l=40, r=20, t=20, b=20), legend=dict(x=0, y=1))
        st.plotly_chart(fig_line, use_container_width=True)

    with col2:
        st.subheader("Distribuição do Nível de Atividade")
        level_counts = filtered_df['kp_level'].value_counts()
        fig_bar = px.bar(x=level_counts.index, y=level_counts.values, labels={'x': 'Nível de Atividade', 'y': 'Contagem'})
        fig_bar.update_layout(height=350, margin=dict(l=20, r=20, t=20, b=20))
        st.plotly_chart(fig_bar, use_container_width=True)

    col3, col4 = st.columns(2)

    with col3:
        st.subheader("Proporção de Atividade")
        fig_pie = px.pie(filtered_df, names='kp_level', hole=0.4)
        fig_pie.update_layout(height=350, margin=dict(l=20, r=20, t=40, b=20), showlegend=False)
        st.plotly_chart(fig_pie, use_container_width=True)
        
    with col4:
        st.subheader("Top 10 Registros Mais Recentes")
        
        # Obter os 10 registros mais recentes e reordenar para o gráfico
        recent_df = filtered_df.sort_values(by='time_tag', ascending=False).head(10)
        recent_df = recent_df.sort_values(by='time_tag', ascending=True)
        
        # Formatar a hora para exibição no eixo Y
        recent_df['time_label'] = recent_df['time_tag'].dt.strftime('%d/%m %H:%M')
        
        fig_recent_bar = px.bar(
            recent_df,
            x='estimated_kp',
            y='time_label',
            orientation='h',
            color='kp_level',
            labels={'time_label': '', 'estimated_kp': 'Kp Estimado'},
            category_orders={"kp_level": ["Calmo", "Instável", "Ativo", "Tempestade"]},
            color_discrete_map={
                'Calmo': '#2ca02c',
                'Instável': '#ff7f0e',
                'Ativo': '#d62728',
                'Tempestade': '#9467bd'
            }
        )
        
        fig_recent_bar.update_layout(
            height=350, 
            margin=dict(l=10, r=10, t=20, b=20),
            legend_title_text='Nível'
        )
        st.plotly_chart(fig_recent_bar, use_container_width=True)

if __name__ == "__main__":
    main() 