# -*- coding: utf-8 -*-
"""
getting SENAMHI's precipitation data from webpage

"""

import bs4
from bs4 import BeautifulSoup
import pandas as pd
import requests
from datetime import datetime

#importando el archivo de las estaciones, exportado de GIS
df_import = pd.read_csv('est_usar.csv')

#loop para descargar data por cada estacion
for index, row in df_import.iterrows():
    #obtenemos sus datos #estacion, estado, tipo, categoria, codigo 
    nom_est=row['nom']
    est=row['cod']
    estado=row['estado']
    tipo_est=row['ico']
    cat=row['cate']
    cod_old=row['cod_old']
    #url en php donde se hara las consultas para cada estacion
    url_grafico = 'https://www.senamhi.gob.pe/mapas/mapa-estaciones-2/map_red_graf.php?cod={}&estado={}&tipo_esta={}&cate={}&cod_old={}'.format(est, estado,tipo_est,cat,cod_old)
    #uso de bs4 para hacer webscrapping
    page  = requests.get(url_grafico)
    soup =  BeautifulSoup(page.content,'html.parser')
    #lista de fechas con data disponible para la estacion en el ith loop
    date_list = [str(x.text) for x in soup.find(id="CBOFiltro").find_all('option')]
    #fecha de inicio de data disponible
    data_inicio = datetime.strptime(date_list[0], '%Y-%m').date()
    #fecha final de data disponible
    data_fin = datetime.strptime(date_list[-1], '%Y-%m').date()
    #rango de fechas en formato propio
    dates_range = pd.date_range(start = data_inicio,end = data_fin,freq = 'M')
    dates = [str(i)[:4] + str(i)[5:7] for i in dates_range]
    #lista de data por mes en formato df
    df_list=[]
    #loop por cada mes de todo el rango de fechas extraendo data de ppd y colocando en df
    for d in dates:
        url = 'https://www.senamhi.gob.pe/mapas/mapa-estaciones-2/_dato_esta_tipo02.php?estaciones={}&CBOFiltro={}&t_e={}&estado={}&cod_old={}&cate_esta={}'.format(est,d ,tipo_est,estado,cod_old,cat)
        page  = requests.get(url)
        soup =  BeautifulSoup(page.content,'html.parser')
        table = soup.find_all('table')
        df = pd.read_html(str(table))[1]
        new_df=df[2:].drop(df[2:].columns[1:-1],axis=1).rename(columns={df[2:].columns[0]:'date',df[2:].columns[-1]:'ppd'}).set_index('date')
        df_list.append(new_df)
    #concatenacion de todos los df en uno solo con formato de columns={'date','ppd'} con index = date
    final_df=pd.concat(df_list)
    output_text_file = 'ppd_est_{}.csv'.format(nom_est)
    final_df.to_csv(output_text_file)


