# -*- coding: utf-8 -*-
"""
Created on Mon Sep  2 09:02:59 2024

@author: Alexandre Araújo Costa & Luca Vianna Zulato
"""

# Este programa realiza buscas na página de andamentos processuais do STF.
# O programa utiliza o módulo dsl, disponível no repositório GitHub.

import os
import requests
import dsl
from dsl import ext, clean, clext, get
from time import sleep
import pandas as pd
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.keys import Keys
import time
from selenium.webdriver.chrome.options import Options
from PyPDF2 import PdfReader
import google.generativeai as genai

lista = []
lista_dados_a_gravar = []
dados_a_gravar = []
respostas_gemini = []

# Defina os parâmetros de busca.
classe = "HC"
inicial = 193727
final = inicial + 4

arquivo_a_gravar = 'Dados_processuais_' + classe + '_' + str(inicial) + '_a_' + str(final)

# Define a custom user agent
my_user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36"

# Set up Chrome options
chrome_options = Options()
chrome_options.add_argument("--headless")
 
# Set the custom User-Agent
chrome_options.add_argument(f"--user-agent={my_user_agent}")

# Create a new instance of ChromeDriver with the desired options
driver = webdriver.Chrome(options=chrome_options)

# Set an implicit wait
driver.implicitly_wait(20)



def waitForLoad(inputXPath): 

    Wait = WebDriverWait(driver, 60)       
    Wait.until(EC.presence_of_element_located((By.XPATH, inputXPath)))
    
def xpath_get (xpath):
    
    waitForLoad(xpath)
    dados = driver.find_element(By.XPATH, xpath).get_attribute('innerHTML')
    
    return dados

for n in range (final-inicial+1):
    
    processo = inicial + n    

    url_2 = 'https://portal.stf.jus.br/processos/listarProcessos.asp?classe=' + classe + '&numeroProcesso=' + str(processo)

    dados = driver.get(url_2)
    
    nome_classe = xpath_get('//*[@id="texto-pagina-interna"]/div/div/div/div[2]/div[1]/div/div[1]')
    
    processo_número = str(nome_classe) + ' ' + str(processo)
    
    paciente = xpath_get('//*[@id="partes-resumidas"]/div[1]/div[2]')
    paciente = paciente.replace('&nbsp', '')
    
    resumo = xpath_get('//*[@id="texto-pagina-interna"]/div/div/div/div[2]/div[1]')
    
    andamentos = xpath_get('//*[@id="andamentos"]/div')
    
    
    
    origem = xpath_get('//*[@id="descricao-procedencia"]')
    origem = origem.replace('<span id="descricao-procedencia">', '')
    origem = origem.replace('    ', '')
    origem = origem.replace('</span>', '')
    origem = origem.replace('\n','')
    
    
        
# Dados extraídos a partir do get(url)

    dados_2 = get(url_2)
    
    incidente_id = ext(dados_2,'<input type="hidden" id="incidente" value="','"')
    
    n_unico = ext(dados_2,'Número Único: ','<')
    
    classe_numero = clean(ext(dados_2,'<input type="hidden" id="classe-numero-processo" value="','"'))
    
    classe = ext(classe_numero, '', ' ')
    
    numero = ext(classe_numero, ' ', '')
    
    classe_extenso = ext(dados_2,'<div class="processo-classe p-t-8 p-l-16">','<')
    
    relator_final = clext(dados_2,'<div class="processo-dados p-l-16">Relator: ','<')
    
    redator_acordao = clext(dados_2,'<div class="processo-dados p-l-16">Redator do acórdão:','<')
    
    relator_ultimo_incidente = clext(dados_2,'Relator do último incidente:','<')
    
    url_peças = 'https://redir.stf.jus.br/estfvisualizadorpub/jsp/consultarprocessoeletronico/ConsultarProcessoEletronico.jsf?seqobjetoincidente=' + str(incidente_id)
    
# Dados extaídos a partir do link do stf + número do incidente
    
    dados_processo = get('https://portal.stf.jus.br/processos/abaInformacoes.asp?incidente=' + incidente_id)
    
    
    assuntos = ext(dados_processo,'Assunto:','</ul').replace('</li>','')
    assuntos = assuntos.split('<li>')[1:]

    # Define o número do procesos a ser buscado e o imprime na tela.
    processo = n + inicial
    print (processo)

    #Define a URL a ser buscada.
    url = 'https://portal.stf.jus.br/processos/listarProcessos.asp?classe=' + classe + '&numeroProcesso=' + str(processo)

    # Busca os dados do prcesso contidos no código fonte recebido inicialmente.
    dados = get(url)
        
    # Extrai o identificador (incidente_id) e os dados disponíveis na página principal
    

    incidente_id = ext(dados,
                       '<input type="hidden" id="incidente" value="',
                       '"')
    
    # if '<div class="message-404">Processo não encontrado</div>' in dados:
        # incidente_id = '1480010'
    #     print(str(processo) + 'não encontrado')
    
    
    classe_numero = clean(ext(dados,
                              '<input type="hidden" id="classe-numero-processo" value="',
                              '"'))
    
    n_unico = ext(dados,
                  'Número Único: ',
                  '<')
    
    classe_extenso = ext(dados,
                         '<div class="processo-classe p-t-8 p-l-16">',
                         '<')
    
    relator_final = clext(dados,
                          '<div class="processo-dados p-l-16">Relator: ',
                          '<')
    
    redator_acordao = clext(dados,
                            '<div class="processo-dados p-l-16">Redator do acórdão:',
                            '<')
    
    relator_ultimo_incidente = clext(dados,
                                     'Relator do último incidente:',
                                     '<')
    
# Busca os dados contidos na aba Informações, cuja url pode ser descoberta inspecionando a rede.
    dados_processo = get('https://portal.stf.jus.br/processos/abaInformacoes.asp?incidente='+incidente_id)
    
    ## Extrai os dados contidos na aba informações
    
    assuntos = ext(dados_processo,
                   'Assunto:','</ul').replace('</li>',
                                              '')
    assuntos = assuntos.split('<li>')[1:]
    
    origem_orgao = ext(dados_processo,
                       'Órgão de Origem:',
                       '<div class="col-md-7')
    
    origem_orgao = clean(clext(origem_orgao,
                               'processo-detalhes">',
                               '<'))
    origem_orgao = clean(origem_orgao.replace('SUPREMO TRIBUNAL FEDERAL','STF').replace('\r',''))
    
    origem_numero = ext(dados_processo,
                        'Número de Origem:',
                        '<div class="col-md-12')
    
    origem_numero = clean(ext(origem_numero,
                              'processo-detalhes">',
                              '<').replace('\r',''))
    
    numeros = ext(dados_processo,
                  '<div class="col-md-12 col-lg-6 processo-informacao__col m-t-8 m-b-8" style="display: flex;justify-content: space-between;">',
                  '<div id="partes" class="tab-pane">').split('<div class="numero">')
    
    
    origem = 'NA'
    volumes = 'NA'
    folhas = 'NA'
    apensos = 'NA'
    for x in numeros[1:]:
        origem = clean(ext(x,'<span id="descricao-procedencia">','<').replace('\r',''))
        if 'volumes' in x:
            volumes = (ext(x,'','<'))
        else:
            volumes = 'NA'
        if 'folhas' in x:
            folhas = (ext(x,'','<'))
        else:
            folhas = 'NA'
        if 'apensos' in x:
            apensos = (ext(x,'','<'))
        else:
            apensos = 'NA'


# Busca os dados contidos na aba Partes.
    dados_partes = get('https://portal.stf.jus.br/processos/abaPartes.asp?incidente='+incidente_id)
    
    # Limita os dados às informações completas, excluindo a seção de partes resumidas.
    dados_partes = ext(dados_partes,'','div id="partes-resumidas">')
    
    # Cria uma lista com os dados de cada parte.
    partes0 = dados_partes.split('<div class="processo-partes lista-dados m-l-16 p-t-0">')[1:]
    partes = []
    index = 0
    n_adv = 0
    parte1 = 'NA'
    for parte in partes0:
        parte_tipo = ext(parte,'<div class="detalhe-parte">','<')
        parte_tipo = parte_tipo.replace('.(S)','')
        parte_tipo = parte_tipo.replace('.(A/S)','')
        parte_tipo = parte_tipo.replace('AM. CURIAE.','AMICUS')
        
        parte_nome = ext(parte,'<div class="nome-parte">','<')
        parte_nome = dsl.remover_acentos(parte_nome)
        parte_nome = dsl.ajustar_nome(parte_nome)
        parte_nome = dsl.ajusta_requerentes(parte_nome)
        
        if 'ADV' in parte_tipo:
            index_adv = str(index)+'a'
            n_adv = n_adv + 1
            partes.append({"index": index_adv,
                            "tipo": parte_tipo,
                            "nome": parte_nome})
        else:
            index = (index+1)
            n_partes = index
            if index == 1:
                parte1 = parte_nome
            partes.append({"index": str(index),
                            "tipo": parte_tipo,
                            "nome": parte_nome})
            
    
    partes_json = json.dumps(partes, ensure_ascii=False)
    

# Busca os dados contidos na aba Andamentos.
    andamentos_dados = get('https://portal.stf.jus.br/processos/abaAndamentos.asp?incidente=' + incidente_id)
    

    
    # Cria uma lista com os dados dos andamentos
    andamentos0 = andamentos_dados.split('<div class="andamento-item">')[1:]
    andamentos_lista = []
    decisoes = []
    data1 = 'NA'
    index = len(andamentos0) + 1
    for item in andamentos0:
        index = index - 1
        andamento_data = ext(item,'<div class="andamento-data ">','<')
        andamento_nome =  ext(item,'<h5 class="andamento-nome ">','<')
        if index == 1:
            data1 = andamento_data
        if '<a href="' in item:
            andamento_docs = 'https://portal.stf.jus.br/processos/' + ext(item,'<a href="','"')
        else:
            andamento_docs = 'NA'

        if 'andamento-julgador' in item:
            andamento_julgador = ext(item,'"andamento-julgador badge bg-info ">','</')
        else:
            andamento_julgador = 'NA'
            
        andamento_complemento = dsl.clean(ext(item,'<div class="col-md-9 p-0','<'))
        if andamento_complemento == '':
            andamento_complemento = 'NA'
        
        # Cria dicionário com os dados dos andamentos            
        andamento_dados = {'index': index,
                           'data': andamento_data,
                           'nome': dsl.remover_acentos(andamento_nome.upper()),
                           'complemento': dsl.remover_acentos(andamento_complemento.upper()),
                           'julgador': dsl.remover_acentos(andamento_julgador.upper()),
                           'docs': andamento_docs,
                           # 'item': item.replace('\r\n','')
                            }

        # Acrescenta os andamentos a uma lista com todos os andamentos do processo.
        andamentos_lista.append(andamento_dados)
        
        if andamento_julgador != 'NA':
            decisoes.append(andamento_dados)
    
    andamentos_json = json.dumps(andamentos_lista, ensure_ascii=False)
    
    data_protocolo = 'NA'
    for elemento in reversed(andamentos_lista):
        if elemento['nome'] == 'PROTOCOLADO':
            data_protocolo = elemento['data']
            break
    
    data_autuacao = 'NA'
    for elemento in reversed(andamentos_lista):
        if elemento['nome'] == 'AUTUADO':
            data_autuacao = elemento['data']
            break
    
    data_distribuicao = 'NA'
    for elemento in reversed(andamentos_lista):
        if elemento['nome'] == 'DISTRIBUIDO':
            data_distribuicao = elemento['data']
            primeiro_relator = elemento['complemento']
            break
        else:
            primeiro_relator = "NA"
    
    decisoes_monocraticas = []
    decisoes_colegiadas = []
    inclusao_pauta = []
    decisoes_embargos = []
    dje_lista = []
    decisoes_e_acordaos = []
    for elemento in reversed(andamentos_lista):
      #  print ('(' + elemento['nome'] + ')')
        if elemento['nome'] in ['PUBLICACAO, DJE','PUBLICADO ACORDAO, DJE']:
            decisoes_e_acordaos.append(elemento)
        if elemento['julgador'] != 'NA':
            if ('DJE' in elemento['nome']):
                dje_lista.append(elemento)
            if ('INCLUA-SE EM PAUTA' in elemento['nome'] or
                'INCLUIDO NA LISTA' in elemento['nome'] or
                'APRESENTADO EM MESA' in elemento['nome']):
                inclusao_pauta.append(elemento)
            elif ('EMBARGOS' in elemento['nome']):
                decisoes_embargos.append(elemento)
            elif ('MIN.' in elemento['julgador']):
                decisoes_monocraticas.append(elemento)
            else:
                decisoes_colegiadas.append(elemento)
                
    relatorio_decisao = [elemento['docs'] for elemento in decisoes_e_acordaos]
    
    # Debug: Print all URLs first
    print("\nAll URLs found:")
    for i, url in enumerate(relatorio_decisao):
        print(f"{i+1}. {url}")
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    pdf_dir = os.path.join(script_dir, 'pdfs')
    if not os.path.exists(pdf_dir):
        os.makedirs(pdf_dir)
        print(f"\nCreated directory: {pdf_dir}")
    
    print(f"\nPDFs will be saved to: {pdf_dir}")
    print("\nStarting downloads...")
    
    # Counter for naming files
    doc_counter = 1
    
    # Headers that mimic a browser
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'application/pdf,application/x-pdf,application/octet-stream,*/*',
        'Accept-Language': 'en-US,en;q=0.9',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
    
    # Create a session to maintain cookies
    session = requests.Session()
    session.headers.update(headers)
    
    for doc_url in relatorio_decisao:
        if doc_url and doc_url != 'NA':
            try:
                print(f"\nProcessing URL: {doc_url}")
                
                # First make a HEAD request to check content type
                try:
                    head_response = session.head(doc_url, verify=False, timeout=10)
                    print(f"HEAD response status: {head_response.status_code}")
                    print(f"Content-Type: {head_response.headers.get('content-type', 'Not specified')}")
                except Exception as head_error:
                    print(f"HEAD request failed: {str(head_error)}")
                    continue
                
                # Now try to download
                print("Attempting download...")
                response = session.get(doc_url, verify=False, timeout=30, stream=True)
                print(f"GET response status: {response.status_code}")
                
                if response.status_code == 200:
                    filename = os.path.join(pdf_dir, f"{classe_numero}_doc_{doc_counter}.pdf")
                    print(f"Saving to: {filename}")
                    
                    with open(filename, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            if chunk:
                                f.write(chunk)
                    
                    if os.path.exists(filename):
                        size = os.path.getsize(filename)
                        print(f"Success! File saved ({size} bytes)")
                        doc_counter += 1
                    else:
                        print("Error: File was not created")
                else:
                    print(f"Error: Server returned status {response.status_code}")
                    print(f"Response headers: {dict(response.headers)}")
                
                #Extrair texto do PDF
                leitor = PdfReader(filename)
                texto_total = []
                for pagina in leitor.pages:
                    texto_total.append(pagina.extract_text())
                texto_completo = "\n".join(texto_total)
                with open(filename + '.txt', "w") as text_file:
                    text_file.write(texto_completo)
                    
                    
                #Executar prompt com Gemini API
                prompt = """
Analise o texto e identifique:
    1. Paciente
    2. Relator do acórdão
    3. Autoridade coatora
    4. Crime cometido
    5. Condenação do paciente
    6. Fundamento do pedido
    7. Argumentos principais
    8. Pedido liminar (se houver)
    9. Decisão (se houver)
    10. Fundamento da decisão
    
    Ao terminar a análise escreva a seguinte frase: 'FIM DA ANÁLISE'
    
    Segue o texto a ser analisado:
                """
                prompt_completo = prompt + '\n' + texto_completo
                genai.configure(api_key="AIzaSyDVwxSwX9dz7_TkQKqekJ394FKVQ7q_9j8")
                model = genai.GenerativeModel("gemini-1.5-pro")
                response = model.generate_content(prompt_completo)
                with open(filename + '.resposta.txt', "w") as text_file:
                    text_file.write(response.text)
                    #print ('análise concluída')
                    respostas_gemini = str(response.text)
                    dados_a_gravar = [classe + ' ' + str(processo),
                                      n_unico, 
                                      paciente,
                                      origem,
                                      assuntos,
                                      relator_final,
                                      url_2,
                                      dsl.ext(respostas_gemini, '1. **Paciente:**', '2. **Relator do acórdão:**'),
                                      dsl.ext(respostas_gemini, '2. **Relator do acórdão:**', '3. **Autoridade coatora:**'),
                                      dsl.ext(respostas_gemini, '3. **Autoridade coatora:**', '4. **Crime cometido:**'),
                                      dsl.ext(respostas_gemini, '4. **Crime cometido:**', '5. **Condenação do paciente:**'),
                                      dsl.ext(respostas_gemini, '5. **Condenação do paciente:**', '6. **Fundamento do pedido:**'),
                                      dsl.ext(respostas_gemini, '6. **Fundamento do pedido:**', '7. **Argumentos principais:**'),
                                      dsl.ext(respostas_gemini, '7. **Argumentos principais:**', '8. **Pedido liminar:**'),
                                      dsl.ext(respostas_gemini, '8. **Pedido liminar:**', '9. **Decisão:**'),
                                      dsl.ext(respostas_gemini, '9. **Decisão:**', '10. **Fundamento da decisão:**'),
                                      dsl.ext(respostas_gemini, '10. **Fundamento da decisão:**', 'FIM DA ANÁLISE'),
                                      ]
        
                    colunas = ['Processo',
                               'Número único', 
                               'Paciente site',
                               'Origem',
                               'Assuntos',
                               'Relator final',
                               'url página pública',
                               'Paciente Gemini',
                               'Relator Gemini',
                               'Autoridade Coatora',
                               'Crime',
                               'Condenação',
                               'Fundamento pedido',
                               'Argumentos',
                               'Liminar',
                               'Decisão',
                               'Fundamento decisão']
                
                # grava dados no arquivo
                    lista_dados_a_gravar.append(dados_a_gravar)
                    print ('Análise adicionada à lista')
                # sleep(2)  # Add delay between downloads
                
            except requests.exceptions.RequestException as e:
                print(f"Request error: {str(e)}")
            except Exception as e:
                print(f"Unexpected error: {str(e)}")
                print(f"Error type: {type(e).__name__}")

# Convertendo a lista de dados para um DataFrame
df2 = pd.DataFrame(lista_dados_a_gravar, columns=colunas)

# Salvando o DataFrame em um arquivo Excel
output_file = os.path.join(script_dir, 'pdfs', arquivo_a_gravar + '.xlsx')
df2.to_excel(output_file, index=False)
print(f"Arquivo salvo em: {output_file}")
