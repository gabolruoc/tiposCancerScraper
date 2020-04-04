# tiposCancerScraper

Scraper que extrae información estadística sobre número de muertes, número de casos y porcentaje de supervivencia de tipos de cáncer en base a datos publicados en la página web (https://seer.cancer.gov/statfacts/more.html) del Programa de Vigilancia, Epidemiología y Resultados Finales (SEER) del Instituto Nacional del Cáncer (NCI)  que sigue la incidencia del cáncer y la supervivencia a partir de datos procedentes, basados en la población, los registros de cáncer centrales definidas geográficamente en los Estados Unidos. 

## Descripción ficheros

El proyecto contiene dos ficheros en python que extraen los datos de la paginas web de cada tipo de cáncer y de una tabla publicada en estos sitios.
La salida de estos ficheros son dos archivos CSV con las estadísticas de cada tipo de cáncer.

### tiposCancerScraper/Codigo/SEER.py
Extrae estadísticas demográficas sobre muertes, número de casos y supervivencia de cada tipo de cáncer.
### tiposCancerScraper/Codigo/scraper1.ipynb
Extrae datos históricos sobre número de muertes, casos y supervivencia desde 1975 contenidos en las páginas de web de cada tipo de cáncer.
### tiposCancerScraper/tipos_cancer.csv
Contiene estadísticas demográficas más actualizadas categorizadas por raza, edad y sexo del número de muertes, casos y porcentaje de supervivencia.
### tiposCancerScraper/test.csv
Contiene datos históricos desde el año de 1975 de número de muertes, casos y porcentaje de supervivencia; así también el proyectado mediante diferentes análisis realizados por el instituto.

## Autores

* Gabriel Loja Rodas
* Alfredo Rubio Navarro
