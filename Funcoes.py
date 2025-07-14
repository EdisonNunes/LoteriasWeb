import os
import requests
from bs4 import BeautifulSoup

WIDTH = 600
HEIGHT = 400
MES = ['JANEIRO', 'FEVEREIRO', 'MARÇO', 'ABRIL', 'MAIO', 'JUNHO',
       'JULHO', 'AGOSTO', 'SETEMBRO', 'OUTUBRO', 'NOVEMBRO', 'DEZEMBRO']
caminho = os.getcwd()

opcoes_LotoFacil  = ['15', '16', '17', '18', '19', '20']
opcoes_Megasena   = ['6',   '7',  '8',  '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20']
opcoes_DiaDeSorte = ['7',   '8',  '9', '10', '11', '12', '13', '14', '15']
opcoes = opcoes_LotoFacil.copy()
cor = '#1f6aa5'
#cor = '#ff0000'

headers = {"User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'}
dic_dados = {}

def BuscaPrecoLotoFacil(url):
    requisicao = requests.get(url, headers=headers)
    #print(requisicao)  # <Response [200]>   requisição OK
    # print(requisicao.text)

    site = (BeautifulSoup(requisicao.text, "html.parser"))
    #print(site.prettify())

    ############### Tabela de Preços #############################
    tabela = site.find("div", id="WebPartWPQ4")
    #print(tabela.prettify())

    linhas = tabela.find_all("td")
    #print(linhas)
    lista_prob=["1 em 3.268.760 ", "1 em 204.298   ", "1 em 24.035    ", "1 em 4.006     ", "1 em 843       ", "1 em 211       "]
    j = 0
    for i, linha in enumerate(linhas):

        if i % 2 == 0:
            lista=[]
            l0 = linhas[i].text.replace('<td>','')
            #l0 = l0[:2]
            l0 = l0.replace('números', '')
            chave = '1_' + l0.strip()
        else:
            l0 = linhas[i].text.replace('<td>', '')
            l0 = l0.strip()
            while len(l0) < 10:
                l0 = l0 + ' '

            #lista.append('R$ ' + l0)
            lista.append(l0)
            lista.append(lista_prob[j])

            dic_dados[chave] = lista
            j += 1
        #print(l0)
    # print(dic_dados)

def BuscaPrecoMegaSena(url):
    requisicao = requests.get(url, headers=headers)
    #print(requisicao)  # <Response [200]>   requisição OK
 
    site = (BeautifulSoup(requisicao.text, "html.parser"))
    #print(site.prettify())

    ############### Tabela de Preços #############################
    #tabela = site.find("span", id="DeltaPlaceHolderMain")
    #tab =tabela.find('table', dir='ltr')
    # corpo = tab.find('tbody')
    
    tabela = site.find_all('table')

    ############### Tabela de Preços #############################
    corpo = tabela[2].find('tbody')  # 3ª Tabela do site
    linhas = corpo.find_all('tr')
    
    j = 0
    for i, linha in enumerate(linhas):
        lista=[]
        l1= str(linha)
        l1 = l1.replace('<td>', '')
        l1 = l1.replace('</td>', '')
        l1 = l1.replace('<tr>', '')
        l1 = l1.replace('</tr>', '').strip()
        l1 = l1.replace('<br/>', '').split()
        
        # while len(l1[1]) < 10:
        #     l1[1] = l1[1] + ' '
        # while len(l1[2]) < 10:
        #     l1[2] = l1[2] + ' '
        while len(l1[2]) < 10:
            l1[2] = l1[2] + ' '
        while len(l1[3]) < 10:
            l1[3] = l1[3] + ' '

        #while len(l1[2]) < 13:
        #    l1[2] = l1[2] + ' '
        # lista.append('R$ ' + l1[1])
        # lista.append('1 em ' + l1[2])
        lista.append('R$ ' + l1[2])
        lista.append('1 em ' + l1[3])
        #print(lista)
        chave = '2_' + l1[0].strip()

        dic_dados.update({chave:lista})
        j += 1

    #print(dic_dados)

def BuscaPrecoDiaDeSorte(url):
    requisicao = requests.get(url, headers=headers)
    site = (BeautifulSoup(requisicao.text, "html.parser"))
    # print(site.prettify())
    lista_prob=["2.629.575 ", "328.696   ", "73.043    ", "21.913    ", "843       ",
                "3.320     ", "1.532     ", "766       ", "408       "]

############### Tabela de Preços #############################
    tabela = site.find_all('table')
    body = tabela[2].find("tbody")
    linhas = body.find_all('td')
    #print(linhas)
    j = 0
    for i, linha in enumerate(linhas):
        l1 = str(linha)
        l1 = l1.replace('números + 1 Mês de Sorte', '')
        l1 = l1.replace('</td>', '')
        l1 = l1.replace('<td>', '')
        l1 = l1.replace('<br/>','')
        if i % 2 != 0:
            lista = []

            while len(l1) < 13:
                l1 = l1 + ' '

            # 3_15 ['R$ 16.087,50\u200b\u200b\u200b', '1 em 408       ']
            if len(l1) > 13:
                l1 = l1[:12]+' '
            lista.append(l1)
            lista.append('1 em ' + lista_prob[j])
            j += 1
            #print(chave, lista)
            dic_dados.update({chave: lista})
        else:
            chave = '3_' + l1.strip()

def ConstroiDicionario():
    url = r'https://loterias.caixa.gov.br/Paginas/Lotofacil.aspx'
    BuscaPrecoLotoFacil(url)
    url = r'https://loterias.caixa.gov.br/Paginas/Mega-Sena.aspx'
    BuscaPrecoMegaSena(url)
    url = r'https://loterias.caixa.gov.br/Paginas/Dia-de-Sorte.aspx'
    BuscaPrecoDiaDeSorte(url)
def PegaNoJogos(tipo):
       if tipo == 1:
              lista = opcoes_LotoFacil.copy()
       elif tipo == 2:
              lista = opcoes_Megasena
       else:
              lista = opcoes_DiaDeSorte

       # print(f'Qtd numeros a jogar: {lista[0]}  Tipo = {tipo}')
       return lista

def FormataValor(Valor, dt):
    try:
        fat = float(Valor)
        fat = f'{fat:,.2f}'
        fat = fat.replace('.', '_').replace(',', '.').replace('_', ',')
        fat = 'R$ ' + fat
        return f'Estimado em {dt} : {fat:<18}                 ' # Alinhamento a esquerda
    except:
        return 'Não determinado                             '


# {"Chave":"1_15","Preço":"R$ 3,00","Probabilidade":"1 em 3.268.760"}
# {"Chave":"1_16","Preço":"R$ 48,00","Probabilidade":"1 em 204.298"}
# {"Chave":"1_17","Preço":"R$ 408,00","Probabilidade":"1 em 24.035"}
# {"Chave":"1_18","Preço":"R$ 2.448,00","Probabilidade":"1 em 4.006"}
# {"Chave":"1_19","Preço":"R$ 11.628,00","Probabilidade":"1 em 843"}
# {"Chave":"1_20","Preço":"R$ 46.512,00","Probabilidade":"1 em 211"}
# {"Chave":"2_6","Preço":"R$ 5,00","Probabilidade":"1 em 50.063.860"}
# {"Chave":"2_7","Preço":"R$ 35,00","Probabilidade":"1 em 7.151.980"}
# {"Chave":"2_8","Preço":"R$ 140,00","Probabilidade":"1 em 1.797.995"}
# {"Chave":"2_9","Preço":"R$ 420,00","Probabilidade":"1 em 595.998"}
# {"Chave":"2_10","Preço":"R$ 1.050,00","Probabilidade":"1 em 238.399"}
# {"Chave":"2_11","Preço":"R$ 2.310,00","Probabilidade":"1 em 108.363"}
# {"Chave":"2_12","Preço":"R$ 4.620,00","Probabilidade":"1 em 54.182"}
# {"Chave":"2_13","Preço":"R$ 8.580,00","Probabilidade":"1 em 29.175"}
# {"Chave":"2_14","Preço":"R$ 15.105,00","Probabilidade":"1 em 16.671"}
# {"Chave":"2_15","Preço":"R$ 25.025,00","Probabilidade":"1 em 10.003"}
# {"Chave":"2_16","Preço":"R$ 40.040,00","Probabilidade":"1 em 6.252"}
# {"Chave":"2_17","Preço":"R$ 61.880,00","Probabilidade":"1 em 4.045"}
# {"Chave":"2_18","Preço":"R$ 92.820,00","Probabilidade":"1 em 2.697"}
# {"Chave":"2_19","Preço":"R$ 135.660,00","Probabilidade":"1 em 1.845"}
# {"Chave":"2_20","Preço":"R$ 193.800,00","Probabilidade":"1 em 1.292"}
# {"Chave":"3_7","Preço":"R$ 2,50","Probabilidade":"1 em 2.629.575"}
# {"Chave":"3_8","Preço":"R$ 20,00","Probabilidade":"1 em 328.696"}
# {"Chave":"3_9","Preço":"R$ 90,00","Probabilidade":"1 em 73.043"}
# {"Chave":"3_10","Preço":"R$ 300,00","Probabilidade":"1 em 21.913"}
# {"Chave":"3_11","Preço":"R$ 825,00","Probabilidade":"1 em 7.968"}
# {"Chave":"3_12","Preço":"R$ 1.980,00","Probabilidade":"1 em 3.320"}
# {"Chave":"3_13","Preço":"R$ 4.290,00","Probabilidade":"1 em 1.532"}
# {"Chave":"3_14","Preço":"R$ 8.580,00","Probabilidade":"1 em 766"}
# {"Chave":"3_15","Preço":"R$ 16.087,50","Probabilidade":"1 em 408"}