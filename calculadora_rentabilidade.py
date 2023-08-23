import pandas as pd
import numpy as np
import datetime as dt
import yfinance as yf
from bcb import sgs

import matplotlib.pyplot as plt
import mplcyberpunk

plt.style.use('cyberpunk')

class calculadoraRentabilidade():

    def __init__(self, ativos, dataInicio, capital, aporte = None):
        
        self.tickers = ativos
        self.dataInicio = dataInicio
        self.capital = capital
        self.pesos = 1/len(ativos)

        if aporte != None:

            self.aporte = aporte
    
    def pegando_dados(self):
        
        inicio = dt.date(2015,1,1)
        fim = dt.date(2022, 12, 31)

        self.dadosEmpresas = yf.download(self.tickers, inicio, fim)['Adj Close']
        self.selic = sgs.get({'juros': 11}, inicio)/100

    def calculando_retornos(self, frequencia):

        retornosEmpresas = self.dadosEmpresas.pct_change().dropna()
        retornosEmpresasAcum = ((1 + retornosEmpresas).cumprod() - 1).resample(f'{frequencia.upper()}').last()
        retornosEmpresasAcum.columns = self.tickers

        retornoSelicAcum = (1 + self.selic).cumprod() - 1
        retornoSelicAcum = retornoSelicAcum.resample(f'{frequencia.upper()}').last()

        self.retornosEmpresasAcum = retornosEmpresasAcum
        self.retornosSelicAcum = retornoSelicAcum
        self.rentabilidade = retornosEmpresasAcum[retornosEmpresasAcum.columns].sum(axis=1) * self.pesos

    def calculando_acumulo_capital(self):

        dfGanho = pd.DataFrame()

        dfGanho['Rentabilidade'] = self.rentabilidade

        for ativo in self.retornosEmpresasAcum.columns:

            dfGanho[f'Ganho_{ativo}'] = (self.retornosEmpresasAcum[ativo] * float(self.capital*self.pesos)) + float(self.capital*self.pesos)

        dfGanho['Ganho_total_acoes'] = dfGanho[dfGanho.columns].sum(axis=1)
        
        dfGanho['Ganho_selic'] = (self.retornosSelicAcum * float(self.capital)) + float(self.capital)

        self.ganhoPorAcao = dfGanho

   
if __name__ == '__main__':

    ativos = ['BBAS3.SA', 'VALE3.SA', 'WEGE3.SA']
    inicio = dt.date(2018,5,14)
    capital = 1000

    carteira = calculadoraRentabilidade(ativos, inicio, capital)

    carteira.pegando_dados()
    carteira.calculando_retornos(frequencia= 'M')
    carteira.calculando_acumulo_capital()

    print(carteira.ganhoPorAcao)

    carteira.ganhoPorAcao[['Ganho_total_acoes', 'Ganho_selic']].plot()
    plt.show()

