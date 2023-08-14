import pandas as pd
import numpy as np
import datetime as dt
import yfinance as yf
from bcb import sgs


class calculadoraRentabilidade():

    def __init__(self, ativos, dataInicio, capital):
        
        self.tickers = ativos
        self.dataInicio = dataInicio
        self.capital = capital
    

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

    def calculando_rentabilidade(self):

        peso = 1/len(self.retornosEmpresasAcum.columns)

        dfRentabilidades = pd.DataFrame()
        


if __name__ == '__main__':

    ativos = ['BBAS3.SA', 'VALE3.SA']
    inicio = dt.date(2018,5,14)
    capital = 1000

    carteira = calculadoraRentabilidade(ativos, inicio, capital)

    # carteira.pegando_dados()
    # carteira.calculando_retornos(frequencia= 'M')
    # carteira.calculando_rentabilidade()