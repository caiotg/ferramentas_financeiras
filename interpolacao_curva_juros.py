from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import pandas as pd
import datetime as dt
from pandas.tseries.offsets import *
import os

from scipy import interpolate
import mplcyberpunk
import matplotlib.pyplot as plt

plt.style.use("cyberpunk")

class interpolacao_curva_juros():

    def __init__(self, mercadoria, dataDI):
        
        self.url = f'''https://www2.bmf.com.br/pages/portal/bmfbovespa/boletim1/SistemaPregao1.asp?pagetype=pop&caminho=Resumo%20Estat%EDstico%20-%20Sistema%20Preg%E3o&Data={dataDI}&Mercadoria={mercadoria}'''
        self.ano = int(dataDI[-4:])
        self.mes = int(dataDI[3:5])
        self.dia = int(dataDI[:2])

    def pegando_dados(self):

        driver = webdriver.Chrome(service= Service(), options= webdriver.ChromeOptions())

        driver.get(self.url)

        driver.implicitly_wait(3)

        elementoIndice = driver.find_element('xpath', '/html/body/div/div[2]/form[1]/table[3]/tbody/tr[3]/td[1]/table')
        elementoTabela = driver.find_element('xpath', '/html/body/div/div[2]/form[1]/table[3]/tbody/tr[3]/td[3]/table')

        htmlIndice = elementoIndice.get_attribute('outerHTML')
        htmlTabela = elementoTabela.get_attribute('outerHTML')
        
        indice = pd.read_html(htmlIndice)[0]
        tabela = pd.read_html(htmlTabela)[0]

        driver.quit()

        indice.columns = indice.iloc[0]
        indice = indice.drop(0, axis=0)

        tabela.columns = tabela.iloc[0]
        tabela = tabela.drop(0, axis=0)
        tabela = tabela['ÚLT. PREÇO']
        tabela.index = indice['VENCTO']
        tabela = tabela.astype(int)
        tabela = tabela[tabela != 0]
        tabela = tabela/1000

        self.tabela = tabela

    def formata_datas(self):

        legenda = pd.Series(['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
                            index = ['F', 'G', 'H', 'J', 'K', 'M', 'N', 'Q', 'U', 'V', 'X', 'Z'])
        
        listaDatas = []

        for indice in self.tabela.index:

            letra = indice[0]

            ano = indice[1:3]
            mes = legenda[letra]

            data = f'{mes}-{ano}'
            data = dt.datetime.strptime(data, '%b-%y')

            listaDatas.append(data)

        self.tabela.index = listaDatas

    def calcula_dias_para_data(self, ano, mes, dia):
  
        curvaDiasUteis = []

        diaAtual = dt.datetime(self.ano, self.mes, self.dia)

        for data in self.tabela.index:

            diasUteis = len(pd.date_range(diaAtual, data, freq= BDay()))
            curvaDiasUteis.append(diasUteis)

        taxas = self.tabela.values
        
        self.taxas = list(taxas)
        self.curvaDiasUteis = curvaDiasUteis
        self.diasUteisDaquiParaData = len(pd.date_range(diaAtual, dt.datetime(ano, mes, dia), freq= BDay()))

    def fazendo_interpolacao(self):

        linear = interpolate.interp1d(self.curvaDiasUteis, self.taxas, kind= 'linear')
        cubica = interpolate.interp1d(self.curvaDiasUteis, self.taxas, kind= 'cubic')

        diasNovos = [self.diasUteisDaquiParaData]

        self.taxaLinear = list(linear(diasNovos))
        self.taxasCubica = list(cubica(diasNovos))

if __name__ == '__main__':

    curvaJuros = interpolacao_curva_juros(mercadoria= 'DI1', dataDI= '06/03/2019')

    curvaJuros.pegando_dados()
    curvaJuros.formata_datas()
    curvaJuros.calcula_dias_para_data(2025,5,31)
    curvaJuros.fazendo_interpolacao()

    fig, ax = plt.subplots()
    ax.scatter(curvaJuros.curvaDiasUteis, curvaJuros.taxas)
    ax.scatter(curvaJuros.diasUteisDaquiParaData, curvaJuros.taxasCubica)
    plt.show()