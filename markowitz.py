import pandas as pd
import numpy as np
import datetime as dt
import yfinance as yf
from scipy.optimize import minimize
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import mplcyberpunk

plt.style.use('cyberpunk')

class otimizacao_markowitz():

    def __init__(self, ativos, cotacoesAjustadas):

        self.ativos = ativos
        self.numeroAtivos = len(ativos)
        self.cotacoesAjustadas = cotacoesAjustadas
    
    def calcula_estatisticas(self):

        self.retornosLog = self.cotacoesAjustadas.pct_change().apply(lambda x: np.log(1+x)).dropna()
        self.mediaRetornos = self.retornosLog.mean()
        self.matrizCov = self.retornosLog.cov()

    def calcula_vetor_sharp(self, numeroCarteiras):

        vetorRetornosEsperados = np.zeros(numeroCarteiras)
        vetorVolatilidadeEsperada = np.zeros(numeroCarteiras)
        vetorSharp = np.zeros(numeroCarteiras)
        tabelaPesos = np.zeros((numeroCarteiras, self.numeroAtivos))

        for i in range(numeroCarteiras):

            pesos = np.random.random(self.numeroAtivos)
            pesos = pesos/np.sum(pesos)
            tabelaPesos[1,:] = pesos

            vetorRetornosEsperados[i] = np.sum(self.mediaRetornos * pesos * 252)
            vetorVolatilidadeEsperada[i] = np.sqrt(np.dot(pesos.T, np.dot(self.matrizCov*252, pesos)))

            vetorSharp[i] = vetorRetornosEsperados[i]/vetorVolatilidadeEsperada[i]

        self.indiceDoSharpMaximo = vetorSharp.argmax()
        self.vetorSharp = vetorSharp
        self.vetorVolatilidadeEsperada = vetorVolatilidadeEsperada
        self.retornosEsperadosArit = np.exp(vetorRetornosEsperados) -1

    def pegando_retorno(self, pesoTeste):
        pesoTeste = np.array(pesoTeste)
        retorno = np.sum(self.mediaRetornos * pesoTeste) * 252
        retorno = np.exp(retorno) - 1
        
        return retorno

    def checando_soma_pesos(self, pesoTeste):
        
        return np.sum(pesoTeste) - 1

    def pegando_vol(self, pesoTeste):
        pesoTeste = np.array(pesoTeste)
        vol = np.sqrt(np.dot(pesoTeste.T, np.dot(self.matrizCov * 252, pesoTeste)))
        
        return vol

    def otimizacao(self):

        eixoYFronteiraEficiente = np.linspace(self.retornosEsperadosArit.min(), self.retornosEsperadosArit.max(), 50)

        pesoInicial = [1/self.numeroAtivos] * self.numeroAtivos
        limites = tuple([(0,1) for ativo in self.ativos])        

        eixoXFronteiraEficiente = []

        for retornoPossivel in eixoYFronteiraEficiente:

            restricoes = ({'type':'eq',
                           'fun': self.checando_soma_pesos},
                           {'type':'eq',
                            'fun': lambda w: self.pegando_retorno(w) - retornoPossivel})
            
            result = minimize(self.pegando_vol, pesoInicial, method= 'SLSQP', bounds= limites, constraints= restricoes)

            eixoXFronteiraEficiente.append(result['fun'])
        

        self.eixoYFronteiraEficiente = eixoYFronteiraEficiente
        self.eixoXFronteiraEficiente = eixoXFronteiraEficiente
        self.result = result


if __name__ == '__main__':

    dataFim = dt.date(2022,12,31)
    dataInicio = dt.date(2015,1,1)

    ativos = ['AAPL', 'v', 'AMZN', 'KO']

    cotacoesAjustadas = yf.download(ativos, dataInicio, dataFim)['Adj Close']


    otimizacaoMarkowitz = otimizacao_markowitz(ativos, cotacoesAjustadas)

    otimizacaoMarkowitz.calcula_estatisticas()
    otimizacaoMarkowitz.calcula_vetor_sharp(numeroCarteiras= 10000)
    otimizacaoMarkowitz.otimizacao()

    print(otimizacaoMarkowitz.result)

    fig, ax = plt.subplots()

    ax.scatter(otimizacaoMarkowitz.vetorVolatilidadeEsperada, otimizacaoMarkowitz.retornosEsperadosArit, c= otimizacaoMarkowitz.vetorSharp)
    plt.xlabel('Volatilidade Esperada')
    plt.ylabel('Retornos Esperados')
    ax.scatter(otimizacaoMarkowitz.vetorVolatilidadeEsperada[otimizacaoMarkowitz.indiceDoSharpMaximo], otimizacaoMarkowitz.retornosEsperadosArit[otimizacaoMarkowitz.indiceDoSharpMaximo], c= '#F5D300')
    ax.plot(otimizacaoMarkowitz.eixoXFronteiraEficiente, otimizacaoMarkowitz.eixoYFronteiraEficiente)
    ax.yaxis.set_major_formatter(mtick.PercentFormatter(1.0))
    ax.xaxis.set_major_formatter(mtick.PercentFormatter(1.0))

    plt.show()