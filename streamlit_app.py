import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.os_manager import ChromeType

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

from bs4 import BeautifulSoup

import requests
from datetime import date
import time
import os
import re
import glob
import shutil
import PyPDF2

# variables iniciales
fecha = date.today()
fecha_actual = fecha.strftime("%d/%m/%Y")


# Configurar opciones del navegador
options = Options()
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--headless")  # Ejecutar en modo headless para servidores.

# Inicializar el controlador sin usar caché
def get_driver():
    try:
        driver = webdriver.Chrome(
            service=Service(
                ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install()
            ),
            options=options,
        )
        return driver
    except Exception as e:
        st.error(f"Error al iniciar el controlador: {e}")
        return None
    
# FUNCION WAIT TRUE
def action(path='', value='click' ):
    while True:
        try:
            if '/' in path:
                element = driver.find_element(By.XPATH, path)
            else:
                element = driver.find_element(By.ID, path)        
            if value == 'click' :
                element.click()
            else:
                element.send_keys(value)
        except Exception as x:
            st.write("error en: ",path," y ",value)
            time.sleep(1)
            continue
        break

# Usar el controlador para acceder a una página web
driver = get_driver()
if driver:
    try:
        # # CARGAR EL NUMERO DE JUICIO
        query_params = st.query_params
        # Extraer los valores de 'juicio', 'user' y 'pass'
        juicio = query_params.get("juicio", [""])  # Extraer el primer valor o usar "" como predeterminado
        usuario = query_params.get("u", [""])      # Extraer el primer valor o usar "" como predeterminado
        password = query_params.get("p", [""])     # Extraer el primer valor o usar "" como predeterminado
        controlador = query_params.get("controlador", [""])     # Extraer el primer valor o usar "" como predeterminado

        # Validar los valores obtenidos
        if juicio==[""]:
            st.warning("No se proporcionó un número de juicio en la URL.")
            st.stop()
        if usuario==[""]:
            st.warning("No se proporcionó el usuario en la URL.")
            st.stop()
        if password==[""]:
            st.warning("No se proporcionó la contraseña en la URL.")
            st.stop()
        if controlador==[""]:
            st.warning("no controlador")
            st.stop()

        # Mostrar el valor en la interfaz
        # st.write(f"usuario: {usuario}")  
        # st.write(f"password: {password}")  
        # st.write(f"Número de juicio obtenido: {juicio}")  
        st.write("🚀 Iniciar proceso !!")

        url = 'https://unionnegocios.com.py/sistema/juicios/datos/' + juicio
        try:
            headers = {"Accept": "application/json"} # Cambiar Content-Type a Accept
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json() # data['id_juicios']
                cedula = data['ci1']
                monto = data['monto']
                st.write("--- CI: " + " | DEM: " + data['dem1'] + data['ci1'] + " | MONTO: " + data['monto'] )
            else:
                st.write("\x1b[⚠️ Error.... {response.status_code}\x1b[0m")
                
        except Exception as e:
            st.write(f"Error: {str(e)}")
            
        st.write("⌛ procesando....")

        # # URL del sitio web que deseas procesar
        url = 'https://ingresosjudiciales.csj.gov.py/LiquidacionesWeb/loginAbogados.seam'
        # driver = webdriver.Chrome()
        driver.get(url)

        wait = WebDriverWait(driver, 10)
        action('j_id3:username',usuario)
        action('j_id3:password',password)
        action('j_id3:submit','click')
        action('iconabogadosFormId:j_id17','click')
        action('iconabogadosFormId:j_id18','click')
        action('juicioFormId:fechaIdInputDate',fecha_actual)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        # h1_text = soup.find('h1').get_text() if soup.find('h1') else "No se encontró <h1>"
        # st.code(h1_text)

        # Agregar Demandante
        wait.until(EC.element_to_be_clickable((By.ID, 'juicioFormId:j_id59'))).click() 
        tipo_doc_demandante = Select(wait.until(EC.element_to_be_clickable((By.ID, 'juicioFormId:demandantesListId:0:tipoDocumentoContribuyenteId'))))
        tipo_doc_demandante.select_by_value('1')
        time.sleep(1)
        nro_doc_demandante = driver.find_element(By.ID, 'juicioFormId:demandantesListId:0:numeroDocumentoContribuyenteId')
        nro_doc_demandante.send_keys('80111738-0')
        st.write("ℹ Demandante agregado")

        # Agregar demandado
        wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/table/tbody/tr[5]/td/div/div/table/tbody/tr/td[2]/table/tbody/tr[6]/td/table/tbody/tr[2]/td[1]/table/tbody/tr/td/form/span/table[1]/tbody/tr[6]/td/table/tbody/tr/td[2]/a'))).click()
        nro_doc_demandado = wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/table/tbody/tr[5]/td/div/div/table/tbody/tr/td[2]/table/tbody/tr[6]/td/table/tbody/tr[2]/td[1]/table/tbody/tr/td/form/span/table[1]/tbody/tr[7]/td/table/tbody/tr/td[2]/input')))
        nro_doc_demandado.send_keys(cedula)
        st.write("ℹ Demandado agregado")
        if data['ci2'] is not None and data['ci2'].isdigit():
            wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/table/tbody/tr[5]/td/div/div/table/tbody/tr/td[2]/table/tbody/tr[6]/td/table/tbody/tr[2]/td[1]/table/tbody/tr/td/form/span/table[1]/tbody/tr[6]/td/table/tbody/tr/td[2]/a'))).click()
            nro_doc_demandado2 = wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/table/tbody/tr[5]/td/div/div/table/tbody/tr/td[2]/table/tbody/tr[6]/td/table/tbody/tr[2]/td[1]/table/tbody/tr/td/form/span/table[1]/tbody/tr[7]/td/table/tbody/tr[2]/td[2]/input')))
            nro_doc_demandado2.send_keys(data['ci2'])

        agregarConcepto = wait.until(EC.element_to_be_clickable((By.ID, 'juicioFormId:j_id109'))). click()

        # Hacer clic en el elemento 'agregarAccionPrep'
        agregarAccionPrep = wait.until(EC.element_to_be_clickable((By.NAME, 'modalPanelFormId:conceptosListId:5:j_id196'))).click()
        agregarMonto = wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/div/div[2]/div/div[2]/table/tbody/tr/td/form/span/div/div/div[2]/table/tbody/tr/td/div/table/tbody/tr[1]/td[5]/div/input')))
        agregarMonto.send_keys(monto)
        st.write("ℹ Monto agregado")
        time.sleep(1)
        grabar = wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/div/div[2]/div/div[2]/table/tbody/tr/td/form/table/tbody/tr/td[1]/input'))).click()

        # SOLUCIÓN 3 (#) Espera a que aparezca el cuadro de diálogo
        grabar2 = wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/table/tbody/tr[5]/td/div/div/table/tbody/tr/td[2]/table/tbody/tr[6]/td/table/tbody/tr[2]/td[1]/table/tbody/tr/td/form/table/tbody/tr/td/input'))).click()
        time.sleep(5)
        alert = WebDriverWait(driver, 3).until(EC.alert_is_present())
        alert.accept()
        st.write("⚠️ Formulario aceptado")
        # ----- PARA FINALIZAR SE TIENE QUE DESCARGAR LA TASA JUDICIAL
        time.sleep(5)
        imprimir = driver.find_element(By.XPATH, '/html/body/table/tbody/tr[5]/td/div/div/table/tbody/tr/td[2]/table/tbody/tr[6]/td/table/tbody/tr[2]/td[1]/table/tbody/tr/td/form/table/tbody/tr/td[1]/input').click()
        time.sleep(5)
        # ----- FIN.

        # Obtener una lista de archivos en la carpeta de descargas
        carpeta_descargas = '.'
        archivos_en_descargas = os.listdir(carpeta_descargas)
        # Inicializa la variable para el número más alto
        numero_mas_alto = 0
        # Busca el número más alto en los nombres de los archivos
        for archivo in archivos_en_descargas:
            if archivo.startswith("liquidacionJuicio") and archivo.endswith(".pdf"):
                # Extrae solo los dígitos del nombre del archivo
                numero_str = ''.join(filter(str.isdigit, archivo))
                if numero_str:
                    numero = int(numero_str)
                    numero_mas_alto = max(numero_mas_alto, numero)

        # Construye el nombre del archivo más alto
        nombre_archivo_mas_alto = f"liquidacionJuicio{numero_mas_alto}.pdf"
        # Rutas de archivo de origen y carpeta de destino
        archivo_a_copiar = os.path.join(carpeta_descargas, nombre_archivo_mas_alto)
        path_carpeta_destino = "tasas/"
        carpeta_destino = os.path.join(path_carpeta_destino, f"{juicio}-tasa.pdf")
        # Copia el archivo a la carpeta de destino y cambia su nombre
        shutil.copy(archivo_a_copiar, carpeta_destino)
        # Ruta del archivo original en la carpeta de descargas
        archivo_original = os.path.join(carpeta_descargas, nombre_archivo_mas_alto)
        # Borra el archivo original en la carpeta de descargas
        os.remove(archivo_original)
        pdf_path = "./tasas/" + str(juicio) + "-tasa.pdf"
        # URL de tu hosting para recibir el archivo
        upload_url = "https://" + controlador + "/uploadtasajudicial"  
        # Mostrar progreso en Streamlit
        st.write(f"📤 Enviando el archivo  al servidor...")
        try:
            # Abrir el archivo y enviarlo como parte del POST
            with open(pdf_path, "rb") as pdf_file:
                files = {"file": (f"{juicio}-tasa.pdf", pdf_file, "application/pdf")}
                response = requests.post(upload_url, files=files)
            # Verificar la respuesta del servidor
            if response.status_code == 200:
                st.success(f"✅ Archivo enviado con éxito al servidor.")
                # st.write("Respuesta del servidor:", response.text)
            else:
                st.error(f"❌ Error al enviar el archivo. Código de estado: {response.status_code}")
                st.write("Mensaje del servidor:", response.text)
        except Exception as e:
            st.error(f"⚠️ Ocurrió un error al enviar el archivo: {e}")

        # Ruta del PDF descargado
        pdf_path = "./tasas/" + str(juicio) + "-tasa.pdf"

        # Verificar si el archivo existe
        if os.path.exists(pdf_path):
            # st.markdown(f"[Abrir PDF del juicio {juicio}]({pdf_path})", unsafe_allow_html=True)
            with open(pdf_path, "rb") as pdf_file:
                reader = PyPDF2.PdfReader(pdf_file)
                texto_completo = ""

                # Extraer texto de cada página
                for i, page in enumerate(reader.pages):
                    texto_completo += f"--- Página {i + 1} ---\n"
                    texto_completo += page.extract_text() + "\n"

                patron = r"\b\d+[A-Z]\b"
                # Buscar el valor en el texto
                resultado = re.search(patron, texto_completo)
                liquidacion = resultado.group()
                st.header("Liquidación Nro.")
                st.code(liquidacion)
                st.header("Texto extraído del PDF:")
                st.text(texto_completo)
        else:
            st.text(f"El archivo {pdf_path} no existe.")
        # driver.get("http://example.com")
        # # Analizar el HTML de la página con BeautifulSoup
        # soup = BeautifulSoup(driver.page_source, 'html.parser')
        # # Extraer el contenido del primer elemento <h1>
        # h1_text = soup.find('h1').get_text() if soup.find('h1') else "No se encontró <h1>"
        # # Mostrar el contenido en Streamlit
        # st.write("Contenido del <h1>:")
        # st.code(h1_text)
    except Exception as e:
        st.error(f"Error al cargar la página: {e}")
    finally:
        driver.quit()
else:
    st.error("No se pudo inicializar el controlador de Selenium.")
