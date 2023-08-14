import pandas as pd
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt
import matplotlib.dates as mdate
import matplotlib.ticker as mtick
import datetime as dt
import statsmodels.api as sm
from bcb import sgs
import mplcyberpunk

plt.style.use('cyberpunk')

class estatisticasAcao:

    def __init__(self, ticker, dataIncio, dataFim):
        
        self.ticker = ticker
        tickers = [ticker, '^BVSP']
        self.dataIncio = dataIncio
        self.dataFim = dataFim
        
        dados = yf.download(tickers, self.dataIncio, self.dataFim)
        
        self.cotacoesAjustadas = dados['Adj Close'][ticker]
        self.volume = dados['Volume'][ticker]
        self.cotacoesFechamento = dados['Close'][ticker]
        self.ibov = dados['Adj Close']['^BVSP']

        print(self.ibov)

    def calcula_max_dd(self):
        
        cotacaoMaxima = self.cotacoesAjustadas.cummax()
        self.drawnDowns = (self.cotacoesAjustadas - cotacaoMaxima)/cotacaoMaxima
        self.maxDD = self.drawnDowns.min()

    def calcula_beta_acao(self):
        
        retornosAcao = self.cotacoesAjustadas.pct_change().dropna()
        retornosIbov = self.ibov.pct_change().dropna()
        retornosIbov.columns = ['Ibov']

        X = retornosIbov
        Y = retornosAcao
        X = sm.add_constant(X)

        model = sm.OLS(Y, X).fit()

        self.beta = model.params[1]
        self.rquadrado = model.rsquared
        self.sumario = str(model.summary())

    def calcula_premio_mercado(self):
        
        selic = sgs.get({'juros':11}, start= dataIncio)/100

        ibov = self.ibov.resample('M').last().to_frame()
        selic = selic.resample('M').last()

        ibov['retorno_ibov'] = ibov['^BVSP'].pct_change()
        selic['retorno_selic'] = selic['juros'].pct_change()
        ibov['Data'] = ibov.index.astype(str)
        selic['Data'] = selic.index.astype(str)

        dfDadosMercado = pd.merge(ibov, selic, how= 'inner', on= 'Data') 
        dfDadosMercado['premio_mercado'] = (1 + dfDadosMercado['retorno_ibov'])/(1 + dfDadosMercado['retorno_selic']) - 1
        dfDadosMercado = dfDadosMercado.dropna()
        dfDadosMercado = dfDadosMercado[['Data', 'premio_mercado']]
        dfDadosMercado['Data'] = pd.to_datetime(dfDadosMercado['Data']).dt.date

        self.retornoSelic = selic['retorno_selic'].dropna()
        self.retornoIbov = ibov['retorno_ibov'].dropna()
        self.dadosMercado = dfDadosMercado
        
    def calcula_capm(self):
        
        self.capm = self.retornoSelic[-1] + self.beta * (self.dadosMercado['premio_mercado'].mean() - self.retornoSelic[-1])

    def calcula_medias_moveis(self, mediaCurta, mediaLonga):

        MMmenor = self.cotacoesFechamento.rolling(mediaCurta).mean()
        MMmaior = self.cotacoesFechamento.rolling(mediaLonga).mean()
        
        dfMediasMoveis = self.cotacoesFechamento.to_frame()
       
        dfMediasMoveis[f'MM{mediaCurta}'] = MMmenor.values
        dfMediasMoveis[f'MM{mediaLonga}'] = MMmaior.values
        dfMediasMoveis = dfMediasMoveis.dropna()

        dfMediasMoveis['Ordem'] = np.where(dfMediasMoveis[f'MM{mediaCurta}'] > dfMediasMoveis[f'MM{mediaLonga}'], 'Compra', 'Venda')

        self.mediasMoveis = dfMediasMoveis

if __name__ == '__main__':

    hoje = dt.datetime.now()
    dataIncio = hoje - dt.timedelta(1500)

    ticker = 'BBAS3.SA'

    metricasAcao = estatisticasAcao(ticker= ticker, dataIncio= dataIncio, dataFim= hoje)
    
    # metricasAcao.calcula_max_dd()
    # metricasAcao.calcula_beta_acao()
    # metricasAcao.calcula_premio_mercado()
    # metricasAcao.calcula_capm()
    # metricasAcao.calcula_medias_moveis(menorPeriodo=30, maiorPeriodo=200)

    # print(metricasAcao.sumario)
    # print(metricasAcao.dadosMercado)
    # print(metricasAcao.mediasMoveis)
