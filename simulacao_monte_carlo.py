import numpy as np
import pandas as pd
import datetime as dt
import yfinance as yf
from numpy import linalg as LA
import matplotlib.pyplot as plt
import mplcyberpunk

plt.style.use('cyberpunk')

class simulacao_monte_carlo:

    def __init__(self, diasProjetados, capitalIncial):

        self.diasProjetados = diasProjetados
        self.capitalIncial = capitalIncial

    def calcula_estatisticas(self, cotacoesAjustadas):

        self.numeroAtivos = len(cotacoesAjustadas.columns)

        retornos = cotacoesAjustadas.pct_change().dropna()
        matrizCov = retornos.cov()
        retornoMedio = retornos.mean(axis=0).to_numpy()

        self.pesosCarteira = np.full(self.numeroAtivos, 1/self.numeroAtivos)
        self.matrizRetornoMedio = retornoMedio * np.ones(shape= (self.diasProjetados, self.numeroAtivos))
        self.L = LA.cholesky(matrizCov)

    def simulacao(self, numeroSimulacoes):

        retornosCarteira = np.zeros([self.diasProjetados, numeroSimulacoes])
        montanteFinal = np.zeros(numeroSimulacoes)

        for i in range(numeroSimulacoes):

            Rpdf = np.random.normal(size= [self.diasProjetados, self.numeroAtivos])

            retornoSintetico = self.matrizRetornoMedio + np.inner(Rpdf, self.L)

            retornosCarteira[:,i] = np.cumprod(np.inner(self.pesosCarteira, retornoSintetico) + 1) * self.capitalIncial

            montanteFinal[i] = retornosCarteira[-1, i]

        self.montanteFinal = montanteFinal
        self.retornosCarteira = retornosCarteira

    def calcula_montantes(self):

        self.montante99 = np.percentile(self.montanteFinal, 1)
        self.montante95 = np.percentile(self.montanteFinal, 5)
        self.montanteMediano = np.percentile(self.montanteFinal, 50)
        self.cenarioLucro = (len(self.montanteFinal[self.montanteFinal > self.capitalIncial])/len(self.montanteFinal)) * 100

    def calcula_var(self):

        self.var99 = self.montante99/1000 -1
        self.var95 = self.montante95/1000 -1
        self.var50 = self.montanteMediano/1000 -1


if __name__ == '__main__':

    ativos = ['WEGE3.SA', 'PCAR3.SA', 'LREN3.SA', 'PETR4.SA', 'VALE3.SA']

    dataInicial = dt.datetime.now() - dt.timedelta(300)
    dataFinal = dt.datetime.now()

    cotacoes = yf.download(ativos, dataInicial, dataFinal)['Adj Close']

    simulacaoMonteCarlo = simulacao_monte_carlo(diasProjetados= 252, capitalIncial= 1000)

    simulacaoMonteCarlo.calcula_estatisticas(cotacoesAjustadas= cotacoes)
    simulacaoMonteCarlo.simulacao(numeroSimulacoes= 100000)
    simulacaoMonteCarlo.calcula_montantes()
    simulacaoMonteCarlo.calcula_var()


    # Gráfico de Linha
    fig, ax = plt.subplots()
    ax.plot(simulacaoMonteCarlo.retornosCarteira, linewidth= 1)
    ax.set_xlabel('Dias')
    ax.set_ylabel('Dinheiro')
    
    # plt.savefig('ferramentas_financeiras/grafico_linhas_simulacao_monte_carlo')
    # plt.show()

    print(f'''Ao investir R$ 1000,00 na carteira {ativos}, 
    podemos esperar esses resultados para os próximo ano, 
    utilizando o método de Monte Carlo com 10 mil simulações:

    Com 50% de probabilidade, o montante será maior que R$ {str(simulacaoMonteCarlo.montanteMediano)}. 

    Com 95% de probabilidade, o montante será maior que R$ {str(simulacaoMonteCarlo.montante95)}.

    Com 99% de probabilidade, o montante será maior que R$ {str(simulacaoMonteCarlo.montante99)}.

    Em {simulacaoMonteCarlo.cenarioLucro:.2f}% dos cenários, foi possível obter lucro no próximo ano.''')

    # Histograma distribuição montantes finais
    config = dict(histtype = "stepfilled", alpha = 0.8, density = False, bins = 150)
    fig, ax = plt.subplots()
    ax.hist(simulacaoMonteCarlo.montanteFinal, **config)
    ax.xaxis.set_major_formatter('R${x:.0f}')
    ax.set_ylabel('Frequencia')
    ax.set_xlabel('Montante Final (R$)')
    ax.set_title('Distribuição Montantes Finais MC')
    
    # plt.savefig('ferramentas_financeiras/histogram_montates_finais')
    # plt.show()
