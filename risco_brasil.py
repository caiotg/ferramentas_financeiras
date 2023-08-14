from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
import pandas as pd


class risco_brasil:

    def __init__(self, listaCDS):
        
        self.listaCDS = listaCDS


    def pegando_riso_brasil(self):

        headers = {'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36'}


        listaDfs = []
        
        for anoCDS in self.listaCDS:

            url = f'https://br.investing.com/rates-bonds/brazil-{anoCDS}-usd-historical-data'
            
            req = Request(url, headers= headers)
            page = urlopen(req)

            soup = BeautifulSoup(page, features= 'lxml')

            table =soup.find_all('table')[1]

            dfCDS = pd.read_html(str(table))[0][['Último', 'Data']]
            dfCDS = dfCDS.set_index('Data')
            dfCDS.index = pd.to_datetime(dfCDS.index, format= '%d.%m.%Y')

            dfCDS.columns = [anoCDS]

            listaDfs.append(dfCDS)

        self.baseCDS = pd.concat(listaDfs, axis= 1)


if __name__ == '__main__':

    listaCDS = ['cds-1-year', 'cds-2-years', 'cds-3-years', 'cds-4-years', 'cds-5-years', 'cds-7-years', 'cds-10-years']

    riscoBr = risco_brasil(listaCDS= listaCDS)

    riscoBr.pegando_riso_brasil()

    print(riscoBr.baseCDS)