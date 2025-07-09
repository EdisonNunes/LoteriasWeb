# pip install streamlit
# pip install pillow
# pip install openpyxl
# pip install beautifulsoup4

import streamlit as st
import random
import requests
from pathlib import Path
#import pandas as pd
import openpyxl
import os
import glob
import time
from PIL import Image
# from Funcoes import ConstroiDicionario, dic_dados  # importa o dicionário e função
from Funcoes import *
from styles import inject_css

TOTAL_LINHAS_PRECALCULADAS = {
    1: 24 * 100000 + 65099,  # tipo 1: LotoFácil
    3: 16 * 100000 + 6651    # tipo 3: Dia de Sorte
}

# ----- Funções utilitárias -----
def mostrar_bolas_com_imagem(lista_numeros, caminho_fotos="Fotos", colunas_por_linha=6):
    lista_sem_zeros = [str(int(n)) for n in lista_numeros if n is not None]
    imagens = []
    for num in lista_sem_zeros:
        caminho_img = os.path.join(caminho_fotos, f"{num}.png")
        if os.path.exists(caminho_img):
            imagens.append(Image.open(caminho_img))
        else:
            st.warning(f"Imagem não encontrada para o número: {num}")

    for i in range(0, len(imagens), colunas_por_linha):
        cols = st.columns(colunas_por_linha)
        for j, img in enumerate(imagens[i:i+colunas_por_linha]):
            with cols[j]:
                img_reduzida = img.resize((80, 80))  # 👈 Tamanho reduzido
                st.image(img_reduzida, use_container_width=True)

    # for i in range(0, len(imagens), colunas_por_linha):
    #     cols = st.columns(colunas_por_linha)
    #     for j, img in enumerate(imagens[i:i+colunas_por_linha]):
    #         with cols[j]:
    #             largura_original, altura_original = img.size
    #             nova_largura = 40
    #             proporcao = float(nova_largura) / float(largura_original)
    #             nova_altura = int(altura_original * proporcao)
    #             img_reduzida = img.resize((nova_largura, nova_altura))  # 👈 Tamanho reduzido
    #             st.image(img_reduzida, use_container_width=True)

def FormataValor(valor, data=None):
    try:
        valor = float(valor.replace(",", "."))
        return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except:
        return valor

def encontrar_arquivos_combina(pasta_destino):
    try:
        arquivos = glob.glob(os.path.join(pasta_destino, "*Combina*"))
        return arquivos
    except Exception as e:
        st.error(f"Erro ao buscar arquivos: {e}")
        return []

def obter_linha_eficiente(linha, caminho_arquivo):
    try:
        wb = openpyxl.load_workbook(caminho_arquivo, read_only=True)
        ws = wb.active
        values = [cell.value for cell in next(ws.iter_rows(min_row=linha + 2, max_row=linha + 2))]
        return values
    except Exception as e:
        st.error(f"Erro ao ler linha {linha} de {caminho_arquivo}: {e}")
        return None

def sorteio_orientado(tipo, qtd, total_linhas=None):
    try:
        if tipo == 2:
            return None, None  # MegaSena não tem base de combinações

        nome_arquivo = f'Combina_{tipo}_{qtd}.xlsx'
        caminho_arquivo = os.path.join('Combinações', nome_arquivo)

        if not os.path.exists(caminho_arquivo):
            return None, None

        if total_linhas is None:
            return None, None  # evita depender de contagem dinâmica

        linha_aleatoria = random.randint(0, total_linhas - 1)

        df = pd.read_excel(caminho_arquivo, skiprows=linha_aleatoria, nrows=1, engine="openpyxl")
        numeros = df.iloc[0].tolist()
        numeros = [int(n) for n in numeros if pd.notna(n)]

        return numeros, total_linhas
    except Exception as e:
        print("Erro no sorteio orientado:", e)
        return None, None

def gerar_numeros_simples(tipo, qtd):
    if tipo == 1:
        max_n = 25
    elif tipo == 2:
        max_n = 60
    else:
        max_n = 31

    return sorted(random.sample(range(1, max_n + 1), int(qtd)))

def formatar_premio(premio):
    try:
        valor = premio["valorPremio"]
        ganhadores = premio["numeroDeGanhadores"]
        desc = premio["descricaoFaixa"]

        valor_formatado = f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        ganhadores_formatado = f"{ganhadores:,.0f}".replace(",", ".")
        linha = f"{ganhadores_formatado:>12} Ganhador(es) com {desc:<12}   Valor : {valor_formatado}"
        return linha
    except Exception as e:
        return f"Erro ao formatar: {e}"

def mostrar_faixas_premiacao(lista_rateio):
    st.subheader("🎁 Faixas de premiação")
    for faixa in lista_rateio:
        texto = formatar_premio(faixa)
        st.markdown(f"- {texto}")

def obter_resultado_api(tipo, concurso=None):
    url_map = {
        1: "https://servicebus2.caixa.gov.br/portaldeloterias/api/lotofacil",
        2: "https://servicebus2.caixa.gov.br/portaldeloterias/api/megasena",
        3: "https://servicebus2.caixa.gov.br/portaldeloterias/api/diadesorte",
    }
    try:
        
        if concurso:
            url = url_map[tipo] + f'/{concurso}'
            response = requests.get(url=url)
        else:    
            response = requests.get(url_map[tipo])

        if response.text: 
            return response.json()
            #return response.text
    except:
        return {}


# ---------- Configuração da página ----------
st.set_page_config(page_title="Sorteio da Sorte", layout="centered")
inject_css()
# with open("mobile_style.css") as f:
#     st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


hide_streamlit_style = """
    <style>
    button[title="Open GitHub"] {display: none;}  }
    button[title="Edit this app"] {display: none;}
    /* Esconda ícones de configurações se necessário */
    [data-testid="stToolbar"] {display: none;}
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

if "dic_dados" not in st.session_state:
    ConstroiDicionario()  # atualiza o dicionário global
    st.session_state.dic_dados = dic_dados.copy()  # garante cópia local para a sessão
# ---------- Interface ----------    
st.title("🎯 LOTERIAS NUNES 🎯")

# Armazena o tempo do último sorteio por tipo
if "tempos_anteriores" not in st.session_state:
    #st.session_state.tempos_anteriores = {1: 1.0, 2: 1.0, 3: 1.0}
    st.session_state.tempos_anteriores = {1: 200.0, 2: 1.0, 3: 200.0}

tab1, tab2 = st.tabs(["🔢 Sortear", "📅 Histórico de Resultados"])

with tab1:
    tipo_jogo = st.radio("Escolha o tipo de jogo", ["LotoFácil", "MegaSena", "Dia de Sorte"], horizontal=True)

    if tipo_jogo == "LotoFácil":
        tipo = 1
        opcoes = opcoes_LotoFacil
    elif tipo_jogo == "MegaSena":
        tipo = 2
        opcoes = opcoes_Megasena
    else:
        tipo = 3
        opcoes = opcoes_DiaDeSorte

    container = st.container(border=False)
    with container:
        col1, col2,col3 = st.columns([1, 1, 2])
        with col1:
            qtd = st.selectbox("Total de Números", options=opcoes, width=200)
        with col2:
            if ((tipo == 1 and qtd == opcoes[0]) or (tipo == 3 and qtd == opcoes[0])):
                #st.markdown("###🏆 Pesquisa em combinações###")
                st.markdown(f'<div style="text-align: left; color: orange;"><h5>Pesquisa em combinações</h5></div>', unsafe_allow_html=True)

        
    # Info da aposta
    chave_aposta = f"{tipo}_{qtd}"
    valor_aposta, probabilidade = st.session_state.dic_dados.get(chave_aposta, ["N/D", "N/D"])

    resultado = obter_resultado_api(tipo)

    data_prox = resultado['dataProximoConcurso']
    valor_estimado = FormataValor(str(resultado['valorEstimadoProximoConcurso']), data_prox)

    texto = f'Data do Sorteio 👉 {data_prox}'
    st.markdown(f'<div style="text-align: left; color: lightgray;"><h5>{texto}</h5></div>', unsafe_allow_html=True)

    container = st.container(border=True)
    with container:
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            st.markdown("**💰 Valor da aposta**")
            st.markdown(f'<div style="text-align: center;"><h5>{valor_aposta}</h5></div>', unsafe_allow_html=True)
        with col2:
            st.markdown("**🎯 Probabilidade**")
            st.markdown(f'<div style="text-align: center;"><h5>{probabilidade}</h5></div>', unsafe_allow_html=True)
        with col3:
            st.markdown("**🏆 Prêmio estimado**")
            st.markdown(f'<div style="text-align: center; color: orange;"><h5>{valor_estimado}</h5></div>', unsafe_allow_html=True)


    # Placeholders dinâmicos (limpam e atualizam a interface)
    msg_placeholder = st.empty()
    bolas_placeholder = st.empty()
    tempo_placeholder = st.empty()
    mes_placeholder = st.empty()

    if st.button("🎲 Sortear Números"):
        # Limpa conteúdo anterior imediatamente
        msg_placeholder.empty()
        bolas_placeholder.empty()
        tempo_placeholder.empty()
        mes_placeholder.empty()

        with st.spinner("Processando sorteio...", show_time=True):
            inicio_total = time.time()
            # numeros, tempo_real = sorteio_orientado(tipo, qtd)
            numeros, _ = sorteio_orientado(tipo, qtd, total_linhas=TOTAL_LINHAS_PRECALCULADAS.get(tipo))
            fim_total = time.time()
            tempo_total = fim_total - inicio_total

            if numeros:
                msg_placeholder.success("Sorteio orientado por base de combinações:")
            else:
                numeros = gerar_numeros_simples(tipo, qtd)
                tempo_total = fim_total - inicio_total  # atualiza tempo para o sorteio aleatório

            bolas_placeholder.markdown("### 🎯 Números sorteados:")
            mostrar_bolas_com_imagem(numeros)

            # Sorteio do mês se for Dia de Sorte
            if tipo == 3:
                mes_sorteado = random.randint(1, 12)
                mes_nome = MES[mes_sorteado - 1]
                mes_placeholder.success(f"📅 Mês da Sorte sorteado\n###### :point_right: {mes_nome}")


            minutos = int(tempo_total // 60)
            segundos = int(tempo_total % 60)
            if minutos > 0:
                tempo_placeholder.info(f"⏱️ Tempo total do sorteio: {minutos} minuto(s) e {segundos} segundo(s)")


            # Salva tempo para estimativa futura (por tipo)
            st.session_state.tempos_anteriores[tipo] = tempo_total


with tab2:
    st.subheader("🔍 Consultar resultado de concursos anteriores")

    tipo_hist = st.radio("Tipo de jogo", ["LotoFácil", "MegaSena", "Dia de Sorte"], key="hist_tipo",
                         horizontal= True)

    if tipo_hist == "LotoFácil":
        jogo = 1 # LotoFacil
    elif tipo_hist == "MegaSena":
        jogo = 2 # MegaSena
    else:
        jogo = 3 #DiadeSorte
    resultado = obter_resultado_api(jogo)    

    # Obtem o número do último concurso automaticamente
    try:
        #ultimo_concurso = jogo().numero()
        ultimo_concurso = resultado['numero']
    except:
        ultimo_concurso = 1000  # fallback caso falhe a API

    num = st.number_input(
        "Número do concurso",
        min_value=1,
        step=1,
        width=200,
        value=int(ultimo_concurso),
        format="%d"
    )
    

    if st.button("📌 Mostrar resultado do concurso"):
        try:
            # dados = jogo(str(int(num))).todosDados()
            dados = obter_resultado_api(jogo, str(num))

            # Cabeçalho com tipo, número e data
            tipo_jogo = dados.get("tipoJogo", "").replace("_", " ").title()
            numero = dados.get("numero", "?")
            data = dados.get("dataApuracao", "?")
            st.info(f"### 🧾 {tipo_jogo} - Concurso {numero} em {data}")

            # Números sorteados com imagem
            dezenas = dados.get("listaDezenas", [])
            if dezenas:
                mostrar_bolas_com_imagem(dezenas)
            else:
                st.warning("Números sorteados não disponíveis.")

            # Mês da Sorte (Dia de Sorte)
            if dados.get("tipoJogo") == "DIA_DE_SORTE":
                # mes = dados.get("mesSorte")
                mes = dados.get("nomeTimeCoracaoMesSorte")
                if mes:
                    # st.success(f"📅 Mês da Sorte: **{mes.upper()}**")
                    st.success(f"📅 Mês da Sorte sorteado\n###### :point_right: {mes.upper()}")

            # Faixas de premiação
            if dados.get("listaRateioPremio"):
                mostrar_faixas_premiacao(dados["listaRateioPremio"])
            else:
                st.info("Premiação não disponível para esse concurso.")

        except Exception as e:
            st.error(f"Erro ao buscar resultado: {e}")