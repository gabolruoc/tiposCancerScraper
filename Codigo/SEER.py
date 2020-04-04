
import requests
from bs4 import BeautifulSoup
from bs4 import NavigableString
from bs4 import Tag
from bs4 import Comment
import re
import csv


""" 
    Estrae los datos de los porcentajes de supervivencia tras 5 años

    Entrada:
        chunk: Objeto tipo Tag con el fragmento HTML a procesar
        cadena: El texto a buscar para identificar el tipo de porcentaje
    Salida:
        devuelve una lista de dos elementos con los porcentajes:
        - % casos de cáncer en este estado al diagnosticarse
        - % casos que sobreviven tras 5 años
"""
def extrae_porc_5a(chunk, cadena):

    porcentajes = ['','']

    try:
        td_porcentajes = chunk.find(string=re.compile(cadena))\
            .find_parent("tr")\
            .select("td")
    except (AttributeError, IndexError, TypeError):
        return porcentajes

    try:
        porcentaje = td_porcentajes[0].string
        porcentaje = porcentaje[0:-1] if porcentaje[-1]  == "%" else porcentaje
        porcentajes[0] = porcentaje
    except (AttributeError, IndexError, TypeError):
        pass

    try:
        porcentaje = td_porcentajes[1].string
        porcentaje = porcentaje[0:-1] if porcentaje[-1]  == "%" else porcentaje
        porcentajes[1] = porcentaje
    except (AttributeError, IndexError, TypeError):
        pass

    return porcentajes



""" 
    Graba en el diccionario pasado como parámetro los valores de los
    porcentajes según la ubicación del cáncer:
        - de etapa de la enfermedad al diagnosticarse
        - de supervivencia a los 5   
    
    Entrada:
        chunk: Objeto tipo Tag con el fragmento HTML a procesar
        datos: El objeto de tipo diccionario donde grabar los datos extraidos
"""
def sobreviven_5a(chunk, datos):

    cabecera = chunk.find(string=re.compile("5\-Year Relative Survival by Stage at Diagnosis"))

    if cabecera == None:
        return

    datos['por_sobreviven_5_años_in_situ'], datos['por_etapa_en_diagnostico_in_situ'] = extrae_porc_5a(chunk, "In Situ")
    datos['por_sobreviven_5_años_local'], datos['por_etapa_en_diagnostico_local'] = extrae_porc_5a(chunk,  "Localized")
    datos['por_sobreviven_5_años_regional'], datos['por_etapa_en_diagnostico_regional'] = extrae_porc_5a(chunk, "Regional")
    datos['por_sobreviven_5_años_distant'], datos['por_etapa_en_diagnostico_distant'] = extrae_porc_5a(chunk, "Distant")
    datos['por_sobreviven_5_años_desc'], datos['por_etapa_en_diagnostico_desc'] = extrae_porc_5a(chunk, "Unknown")

    



""" 
    Graba en el diccionario pasado como parámetro los valores de los
    nuevos casos estimados 
    
    Entrada:
        chunk: Objeto tipo Tag con el fragmento HTML a procesar
        datos: El objeto de tipo diccionario donde grabar los datos extraidos
"""
def nuevos_casos_estimados(chunk, datos):

    try:      
        valor = chunk.find("span", string=re.compile("Estimated New Cases in "))\
                .parent\
                .find_all("span")[1]\
                .string\
                .replace(",","")

        datos['nuevos_casos_estimados'] = valor

    except (AttributeError, IndexError, TypeError):
        pass



""" 
    Graba en el diccionario pasado como parámetro los valores de las
    muertes estimadas
    
    Entrada:
        chunk: Objeto tipo Tag con el fragmento HTML a procesar
        datos: El objeto de tipo diccionario donde grabar los datos extraidos
"""
def nuevas_muertes_estimadas(chunk,datos):

    try:      
        valor = chunk.find("span", string=re.compile("Estimated Deaths in "))\
                .parent\
                .find_all("span")[1]\
                .string\
                .replace(",","")

        datos['nuevas_muertes_estimadas'] = valor

    except (AttributeError, IndexError, TypeError):
        pass



""" 
    Graba en el diccionario pasado como parámetro
    el porcentaje general de supervivencia a los 5 años
    
    Entrada:
        chunk: Objeto tipo Tag con el fragmento HTML a procesar
        datos: El objeto de tipo diccionario donde grabar los datos extraidos
"""
def por_sob_5_años(chunk, datos):

    try:
        valor = chunk.find(string=re.compile("Percent Surviving*")).find_parent("div").find("strong").string
        valor =  valor[0:-1] if valor[-1] == '%' else valor

        datos['porc_sobreviven_5_años'] = valor

    except (AttributeError, IndexError, TypeError):
        pass




""" 
    Graba en el diccionario pasado como parámetro
    los datos clasificados por raza de:
    - nuevos casos
    - muertes

    Entrada:
        chunk: Objeto tipo Tag con el fragmento HTML a procesar
        cadena: El texto a buscar para identificar el tipo de porcentaje
"""
def datos_por_raza(chunk, datos):

    nuevos_casos = chunk.find(string=re.compile("Number of New Cases per "))
    muertes = chunk.find(string=re.compile("Number of Deaths per "))

    if nuevos_casos != None:
        prefijo_quien = "nuevos_casos_"
    elif muertes != None:
        prefijo_quien = "muertes_"
    else:
        return

    try:      
        divs_tabla = chunk.find_all("div", class_="scrapeTable halfSize")
              
        for div in divs_tabla:

            hombres = div.find("h5", string=re.compile("Males"))
            mujeres = div.find("h5", string=re.compile("Females"))

            if hombres != None:
                prefijo_sexo = "hombres_"
            elif mujeres != None:
                prefijo_sexo = "mujeres_"
            else:
                return

            tabla = div.find("table", id=re.compile("^scrapeTable"))

            filas = tabla.find_all("tr")

            for fila in filas:
                texto = fila.find("th").find("strong").string
                valor = fila.find("td").string
                
                if "All Races" == texto:
                    prefijo_raza = "todos"
                elif "White" == texto:
                    prefijo_raza = "blanco"
                elif "Black" == texto:
                    prefijo_raza = "negro"
                elif "Asian/Pacific Islander" == texto:
                    prefijo_raza = "asian"
                elif "American Indian/Alaska Native" == texto:
                    prefijo_raza = "ame_ind"
                elif "Hispanic" == texto:
                    prefijo_raza = "hisp"
                elif "Non-Hispanic" == texto:
                    prefijo_raza = "no_hisp"
                else:
                    prefijo_raza = ""
                    continue

                datos[prefijo_quien + prefijo_sexo + prefijo_raza] = valor
                prefijo_raza = ""
                                
    except (AttributeError, IndexError, TypeError):
        pass



""" 
    Graba en el diccionario pasado como parámetro
    los datos clasificados por edad de:
    - nuevos casos
    - muertes

    Entrada:
        chunk: Objeto tipo Tag con el fragmento HTML a procesar
        cadena: El texto a buscar para identificar el tipo de porcentaje
"""
def datos_por_edad(chunk, datos):

    nuevos_casos = chunk.find(string=re.compile("Percent of New Cases by Age Group"))
    muertes = chunk.find(string=re.compile("Percent of Deaths by Age Group"))

    if nuevos_casos != None:
        prefijo_quien = "nuevos_casos_"
    elif muertes != None:
        prefijo_quien = "muertes_"
    else:
        return

    try:
        tabla = chunk.find("table", id=re.compile("^scrapeTable")).find("tbody")

        filas = tabla.find_all("tr")

        for fila in filas:
            columnas = fila.find_all("td")

            rango_edad = columnas[0].string
            valor = columnas[1].string
            valor = valor[0:-1] if valor[-1] == '%' else valor
            
            if rango_edad == "<1":
                prefijo_rango = "menor1"
            elif rango_edad == "<20":
                prefijo_rango = "menor20"
            elif rango_edad == ">84":
                prefijo_rango = "mayor84"
            else:
                prefijo_rango = rango_edad

            datos[prefijo_quien + prefijo_rango] = valor
                                
    except (AttributeError, IndexError, TypeError):
        pass



""" 
    Rutina principal
"""
def run():

    # nombres de los campos para el fichero csv
    campos = ['nombre', 
    'nuevos_casos_estimados', 'nuevas_muertes_estimadas', 'porc_sobreviven_5_años',
    'por_etapa_en_diagnostico_in_situ', 'por_etapa_en_diagnostico_local', 
    'por_etapa_en_diagnostico_regional', 'por_etapa_en_diagnostico_distant','por_etapa_en_diagnostico_desc',
    'por_sobreviven_5_años_in_situ', 'por_sobreviven_5_años_local', 
    'por_sobreviven_5_años_regional', 'por_sobreviven_5_años_distant','por_sobreviven_5_años_desc', 
    'nuevos_casos_hombres_todos', 'nuevos_casos_mujeres_todos',
    'nuevos_casos_hombres_blanco', 'nuevos_casos_mujeres_blanco',
    'nuevos_casos_hombres_negro', 'nuevos_casos_mujeres_negro',
    'nuevos_casos_hombres_asian', 'nuevos_casos_mujeres_asian',
    'nuevos_casos_hombres_ame_ind', 'nuevos_casos_mujeres_ame_ind',
    'nuevos_casos_hombres_hisp', 'nuevos_casos_mujeres_hisp',
    'nuevos_casos_hombres_no_hisp', 'nuevos_casos_mujeres_no_hisp',
    'muertes_hombres_todos', 'muertes_mujeres_todos',
    'muertes_hombres_blanco', 'muertes_mujeres_blanco',
    'muertes_hombres_negro', 'muertes_mujeres_negro',
    'muertes_hombres_asian', 'muertes_mujeres_asian',
    'muertes_hombres_ame_ind', 'muertes_mujeres_ame_ind',
    'muertes_hombres_hisp', 'muertes_mujeres_hisp',
    'muertes_hombres_no_hisp', 'muertes_mujeres_no_hisp',
    'nuevos_casos_menor1', 'muertes_menor1',
    'nuevos_casos_1-4', 'muertes_1-4',
    'nuevos_casos_5-9', 'muertes_5-9',
    'nuevos_casos_10-14', 'muertes_10-14',
    'nuevos_casos_15-19', 'muertes_15-19',
    'nuevos_casos_menor20', 'muertes_menor20',
    'nuevos_casos_20-34', 'muertes_20-34',
    'nuevos_casos_35-44', 'muertes_35-44',
    'nuevos_casos_45-54', 'muertes_45-54',
    'nuevos_casos_55-64', 'muertes_55-64',
    'nuevos_casos_65-74', 'muertes_65-74',
    'nuevos_casos_75-84', 'muertes_75-84',
    'nuevos_casos_mayor84', 'muertes_mayor84']


    # url principal del sitio
    inicio = 'https://seer.cancer.gov'

    # url con la lista de los tipo de cáncer
    lista = 'https://seer.cancer.gov/statfacts/more.html'

    # definimos la identificación del agente 
    firefox = 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:74.0) Gecko/20100101 Firefox/74.0'
    headers = {'user-agent': firefox}

    try:
        pagina = requests.get(lista, headers=headers, timeout=5)
    except requests.exceptions.Timeout:
        print("Tiempo de espera agotado")
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)

    # este parser arregla el html cuando faltan etiquetas de inicio o final
    soup = BeautifulSoup(pagina.content, 'html5lib') 

    cadena = soup.find(class_="alphaList")
    enlaces = cadena.find_all("a")

    with open('tipos_cancer.csv', 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=campos)

        writer.writeheader()

        for enlace in enlaces:
            if type(enlace.string) != NavigableString or len(enlace.string) == 0:
                continue

            if enlace.string == "All Cancers" or \
               enlace.string == "Female Breast Subtypes" or \
               enlace.string == "Cancer Disparities" or \
               enlace.string == "Common Cancer Sites":
               continue
            

            # inicializamos el dicionario que almacenrá los registros a grabar en el fichero csv
            registro = {}

            print("Nombre: " + enlace.string)
            registro['nombre'] =  enlace.string

            if 'href' in enlace.attrs:
                direccion = inicio + enlace['href']

                try:
                    pagina_detalle = requests.get(direccion, headers=headers, timeout=5)
                except requests.exceptions.Timeout:
                    print("Tiempo de espera agotado")
                except requests.exceptions.RequestException as e:
                    raise SystemExit(e)

                detalle = BeautifulSoup(pagina_detalle.content, 'html5lib')

                div_de_un_vistazo = detalle.find("div",class_="glance-factSheet")

                if div_de_un_vistazo != None:
                    div = div_de_un_vistazo.find("div",class_="glanceBox new")
                    nuevos_casos_estimados(div, registro)

                    div = div_de_un_vistazo.find("div",class_="glanceBox death")
                    nuevas_muertes_estimadas(div, registro)

                    div = div_de_un_vistazo.find("div",class_="statBox")
                    por_sob_5_años(div, registro)
                
                div_sobreviven_5a = detalle.find("div",class_="survival-factSheet")
                if div_sobreviven_5a != None:
                    sobreviven_5a(div_sobreviven_5a, registro)

                divs_diagramas_por_raza = detalle.find_all("div",class_="bar-factSheet")
                for div_diagrama_por_raza in divs_diagramas_por_raza:
                    datos_por_raza(div_diagrama_por_raza, registro)

                divs_diagramas_por_edad = detalle.find_all("div", class_="whogets-factSheet")
                for div_diagrama_por_edad in divs_diagramas_por_edad:
                    datos_por_edad(div_diagrama_por_edad, registro)

                # registramos los datos en el fichero
                writer.writerow(registro)




if __name__ == "__main__":
    run()


