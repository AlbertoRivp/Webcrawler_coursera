import requests
import re
from bs4 import BeautifulSoup
import os
from time import sleep
from colorama import Fore, init

clear_command = 'clear'

init(autoreset=True)

def crawler_get_modules(url: str):
    response = requests.get(url)

    if response.status_code != 200:
        return [], None

    soup = BeautifulSoup(response.text, 'html.parser')

    contenido = soup.find('div', class_="css-1i4o2ol")

    ratings_flag = "/specializations/" in url or "/professional-certificates/" in url

    modulos = []

    try:
      for div in contenido:
          header3 = div.find('h3')
          info = div.find('div', class_='cds-119 css-mc13jp cds-121')
          datos_modulos: dict = {}

          if header3:
              datos_modulos["titulo"] = header3.text
              # Extraemos el url dentro del h3
              url = header3.find('a')
              if url:
                 datos_modulos["url"] = url.get("href")

          if info:
              span = info.find_all('span', class_=lambda clase: clase != 'css-18yxyo6')

              for index, datos in enumerate(span):
                  if index % 2 != 0:
                      # La mitad de los datos dentro de los span no son utiles o estan repetidos
                      # Es por ello que los descartamos con este continue
                      continue

                  if "Module" in datos.text or "Course" in datos.text:
                      # Nos aseguramos de perservar el texto y no solo extraer el numero
                      datos_modulos["parte"] = datos.text
                  else:
                      numeros = re.findall(r'(\d+\.\d+|\d+)', datos.text.strip().replace(',', ''))
                      if numeros:
                          if ratings_flag:
                              if index % 3 == 0:
                                  datos_modulos["rating"] = numeros[0]
                              elif index % 3 == 1:
                                  datos_modulos["calificacion"] = numeros[0]
                              else:
                                  datos_modulos["tiempo_horas"] = numeros[0]
                          else:
                              # Cuando no se trata de una especilizacion o un certificado,
                              # Solo recibimos el tiempo que dura el modulo.
                              datos_modulos["tiempo_horas"] = numeros[0]

          modulos.append(datos_modulos)
    except:
       return [], None
    return modulos, ratings_flag

def crawler_cursos_en_linea(url, search):
    # Realizar la solicitud a la página web
    response = requests.get(url + search)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        cursos = []

        cursosContent = soup.find_all('li', class_='cds-9 css-0 cds-11 cds-grid-item cds-56 cds-64 cds-76')

        for curso in cursosContent:
          titulo_curso = ""
          calificacion = ""
          skill = ""
          skills_curso = ""

          titulo = curso.find('h3', class_='cds-119 cds-CommonCard-title css-e7lgfl cds-121')
          calificacion = curso.find('p', class_='cds-119 css-11uuo4b cds-121')
          link = curso.find('a', class_='cds-119 cds-113 cds-115 cds-CommonCard-titleLink css-si869u cds-142')
          skill = curso.find('div', class_='cds-CommonCard-bodyContent')

          titulo_curso = titulo.text.strip()
          if calificacion:
            calificacion_curso = float(calificacion.text.strip())
          else:
            calificacion_curso = 0
          link_curso = link.get('href')
          if skill:
            skillContent = skill.find('p')
            skills_curso = skillContent.text.strip()


          cursos.append({'titulo': titulo_curso, 'calificacion': calificacion_curso, 'link': link_curso, 'skills': skills_curso})

        # Ordenar la lista de cursos por calificación de mayor a menor
        cursos_ordenados = sorted(cursos, key=lambda x: x['calificacion'], reverse=True)

        # Mostrar los 5 cursos con mayor calificación
        for i, curso in enumerate(cursos_ordenados[:5]):
            modulos, valores_extra = crawler_get_modules(url + curso['link'])
            print("-------------------------------------------------")
            print(f"{Fore.CYAN}{i+1}.- Título: {curso['titulo']}")
            print(f"{Fore.LIGHTGREEN_EX}Calificación: {curso['calificacion']}")
            print(f"Aprendizajes: {curso['skills']}")
            print(f"{Fore.LIGHTBLUE_EX}Link --> {url + curso['link']}")
            if modulos:
              print(f"{Fore.CYAN}<--------------------- Contenido del curso ---------------------> ")
              print_course_info(modulos, valores_extra)
              print(f"{Fore.CYAN}<---------------------------------------------------------------> ")
                
                 
            print("-------------------------------------------------")

    else:
        print(f"No se pudo acceder a la página. Código de estado: {response.status_code}")

def print_course_info(info_curso:list, is_certificate_or_specialization:bool):
  for datos in info_curso:
    print(f"{Fore.BLUE}{datos['parte']}", end=' | ')
    print(f"{Fore.LIGHTWHITE_EX}{datos['titulo']}", end='\n ---> ')
    print(f"{datos['tiempo_horas']}", end=' ')
    print(f"{Fore.BLUE}hora/s", end=' ')
    if is_certificate_or_specialization:
      print("| ", end='')
      print(f"{Fore.LIGHTGREEN_EX}Calificación: {datos['calificacion']}", end=' | ')
      print(f"{Fore.GREEN}Calificado por {datos['rating']} personas")
      if "url" in datos:
         sleep(.02)
         print(f"{Fore.LIGHTBLUE_EX} Link --> {url + datos['url']}")
         print(f"{Fore.RED}<---------------------  Modulos  ---------------------> ")
         modulos, is_certificate = crawler_get_modules(url + datos["url"])
         print_course_info(modulos, is_certificate)
         print(f"{Fore.RED}<-----------------------------------------------------> ")
    else:
      print("")

while True:
  palabra = "WebCrawler Coursera"

  # Imprimir el rectángulo con la palabra
  print(f"{Fore.YELLOW}{'*' * (len(palabra) + 4)}")
  print(f"{Fore.BLUE}* {palabra} *")
  print(f"{Fore.YELLOW}{'*' * (len(palabra) + 4)}")

  print("[+] Preciona *B* Para buscar un nuevo curso")
  print("[+] Preciona *Q* Para salir del programa")
  des = input("[*] --> ")
  des = des.upper()
  if des == "B":
    os.system(clear_command)
    # Imprimir el rectángulo con la palabra
    print(f"{Fore.YELLOW}{'*' * (len(palabra) + 4)}")
    print(f"{Fore.BLUE}* {palabra} *")
    print(f"{Fore.YELLOW}{'*' * (len(palabra) + 4)}")
    topic = input("[+] Necesito cursos de --> ")
    url = 'https://www.coursera.org'
    search = f'/search?query={topic}'
    crawler_cursos_en_linea(url, search)
  elif des == "Q":
   os.system(clear_command)
   print(f"{Fore.BLUE}[:)] Espero haber sido de ayuda")
   break
  else:
    os.system(clear_command)
    print(f"{Fore.RED}[-] ERROR: Opción inválida")


'''
"pre-Algolia": (\w*algolia\w*?):"(.+?)" "Algolia" : "(\w{10}|\w{32})"\s*,\s*"(\w{10}|\w{32})"
Send to:
Everyone
'''