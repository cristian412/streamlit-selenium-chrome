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

# --- VARIABLES INICIALES
fecha = date.today()
fecha_actual = fecha.strftime("%d/%m/%Y")
tiempo_inicio = time.time()
jornal = 103700

# --- Concepto juicio
concepto_juicio = 'juicioFormId:j_id109' # Acción Preparatoria de Juicio Ejecutivo

# Distrito por Defecto Juzgado de Paz
distrito_paz = '/html/body/form/div[1]/div/div[1]/ul/li[4]' # VILLA MORRA

# # CARGAR EL NUMERO DE JUICIO 
# ?p=401-1591666-estudiocloss3-union/sistema/juicios-creatsasa
query_params = st.query_params
# Extraer los valores de 'juicio', 'user' y 'pass'
juicio = query_params.get("juicio", [""])  
usuario = query_params.get("u", [""])     
password = query_params.get("p", [""])    
controlador = query_params.get("controlador", [""])    
proceso = query_params.get("proceso", [""])

# Validar los valores obtenidos
if juicio==[""] or usuario==[""] or controlador==[""] or proceso==[""]:
    st.warning("Bienvenido")
    st.stop()

st.write("🚀 Iniciar proceso !!")

url = 'https://' + str(controlador) + '/datos/' + str(juicio)
try:
    # Usar encabezados genéricos
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json() # data['id_juicios']
        id_juicio = str(juicio)
        cedula = data['ci1']
        monto = data['monto']
        actor_ruc = data['actor_ruc']
        actor_dom_real_calle = data['actor_dom_real_calle']
        actor_dom_real_ciudad = data['actor_dom_real_ciudad']
        actor_dom_procesal_calle = data['actor_dom_procesal_calle']
        actor_dom_procesal_ciudad = data['actor_dom_procesal_ciudad']
        concatenado = ""
        # Recorrer todas las claves y valores del diccionario
        for key, value in data.items():
            concatenado += f"{key}: {value} | "
        # Mostrar el resultado concatenado
        resultado = f"--- Datos: {concatenado.strip('| ')}"
        st.write(resultado)
    else:
        st.write(url)
        st.write(f"⚠️ Error.... {response.status_code}")
        st.stop()
        
except Exception as e:
    st.write(f"Error: {str(e)}")

st.write("⌛ procesando....") 

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
    
# FUNCION ACTION WAIT TRUE
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

        if proceso=='creartasa':
            
            url = 'https://ingresosjudiciales.csj.gov.py/LiquidacionesWeb/loginAbogados.seam'
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
            nro_doc_demandante.send_keys(actor_ruc)
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

            agregarConcepto = wait.until(EC.element_to_be_clickable((By.ID, concepto_juicio))). click()

            # Hacer clic en el elemento 'agregarAccionPrep'
            agregarAccionPrep = wait.until(EC.element_to_be_clickable((By.NAME, 'modalPanelFormId:conceptosListId:5:j_id196'))).click()
            agregarMonto = wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/div/div[2]/div/div[2]/table/tbody/tr/td/form/span/div/div/div[2]/table/tbody/tr/td/div/table/tbody/tr[1]/td[5]/div/input')))
            agregarMonto.send_keys(monto)
            st.write("ℹ Monto agregado")
            time.sleep(5)
            grabar = wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/div/div[2]/div/div[2]/table/tbody/tr/td/form/table/tbody/tr/td[1]/input'))).click()

            # SOLUCIÓN 3 (#) Espera a que aparezca el cuadro de diálogo
            grabar2 = wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/table/tbody/tr[5]/td/div/div/table/tbody/tr/td[2]/table/tbody/tr[6]/td/table/tbody/tr[2]/td[1]/table/tbody/tr/td/form/table/tbody/tr/td/input'))).click()
            time.sleep(5)
            alert = WebDriverWait(driver, 3).until(EC.alert_is_present())
            alert.accept()
            st.write("⚠️ Formulario aceptado")
            # ----- PARA FINALIZAR SE TIENE QUE DESCARGAR LA TASA JUDICIAL
            time.sleep(15)
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
 
             # LEER OCR DEL PDF DESCARGADO
            # Ruta del PDF descargado
            # Verificar si el archivo existe
            if os.path.exists(nombre_archivo_mas_alto):
                # st.markdown(f"[Abrir PDF del juicio {juicio}]({pdf_path})", unsafe_allow_html=True)
                with open(nombre_archivo_mas_alto, "rb") as pdf_file:
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
 
 
            # Rutas de archivo de origen y carpeta de destino
            archivo_a_copiar = os.path.join(carpeta_descargas, nombre_archivo_mas_alto)
            path_carpeta_destino = "tasas/"
            carpeta_destino = os.path.join(path_carpeta_destino, f"{juicio}-{liquidacion}-tasa.pdf")
            # Copia el archivo a la carpeta de destino y cambia su nombre
            shutil.copy(archivo_a_copiar, carpeta_destino)
            # Ruta del archivo original en la carpeta de descargas
            archivo_original = os.path.join(carpeta_descargas, nombre_archivo_mas_alto)
            # Borra el archivo original en la carpeta de descargas
            #os.remove(archivo_original)

            # ENVIAR TASA GENERADA AL SERVIDOR
            pdf_path = "./tasas/" + str(juicio) + "-tasa.pdf"
            # URL de tu hosting para recibir el archivo
            upload_url = "https://" + controlador + "/uploadtasajudicial"  
            # Mostrar progreso en Streamlit
            st.write(f"📤 Enviando el archivo  al servidor...")
            try:
                # Abrir el archivo y enviarlo como parte del POST
                with open(pdf_path, "rb") as pdf_file:
                    files = {"file": (f"{juicio}-tasa.pdf", pdf_file, "application/pdf")}
                    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}
                    response = requests.post(upload_url, files=files, headers=headers)
                # Verificar la respuesta del servidor
                if response.status_code == 200:
                    st.success(f"✅ Archivo enviado con éxito al servidor.")
                    # st.write("Respuesta del servidor:", response.text)
                else:
                    st.error(f"❌ Error al enviar el archivo. Código de estado: {response.status_code}")
                    st.write("Mensaje del servidor:", response.text)
            except Exception as e:
                st.error(f"⚠️ Ocurrió un error al enviar el archivo: {e}")


                
        # ---- PROCESO DAR ENTRADA
        if proceso=='darentrada':
            st.write( '⌛ procesa DAR ENTRADA')

            if int(monto) > (jornal*300):
                # --- poder general
                # ------- OBSERVACION: SOLAMENTE SIN PODER POR AHORA (JUZGADO DE PAZ)
                if not os.path.exists("poder_general_union.pdf"):
                    st.write("El archivo poder_general_union.pdf no existe.")
                    st.stop()
            else:
                # --- Descarga el pdf del juicio en caso que sea Juzgado de Paz
                pdf_url = "https://" + controlador + "/preparacion_pdf/" +  id_juicio + "/?usuario="+usuario+"&pass="+password
                st.write(pdf_url)
                headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}
                response = requests.get(pdf_url, headers=headers)
                if response.status_code == 200:
                    # Abre un archivo local en modo binario para escribir el contenido del PDF
                    with open("tasas/"+id_juicio+"-archivo.pdf", "wb") as pdf_file:
                        pdf_file.write(response.content)
                    st.write( "--- PDF descargado exitosamente como: " + id_juicio+"-archivo.pdf")
                else:
                    st.write(  "No se pudo descargar el PDF. Código de respuesta:", response.status_code)
                    st.stop()
            # FUNCION waitclick
            def waitclick(wait_time=0.5, xpath='', driver='' ):
                time.sleep(wait_time)
                element = driver.find_element(By.XPATH, xpath)
                element.click()
            # Inicia el DRIVER
            url = 'https://www.csj.gov.py/gestion/'
            driver.get(url)
            wait = WebDriverWait(driver, 10)
            # --- Iniciar sesión con Usuario y password
            wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/form/div[4]/div/div/div[2]/div[2]/div[1]/div/span[1]/input[1]'))).send_keys(usuario) # Usuario
            wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/form/div[4]/div/div/div[2]/div[2]/div[2]'))).click()
            wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/form/div[4]/div/div/div[2]/div[2]/div[3]/div/span/input[1]'))).send_keys(password)  # Enviar las teclas directamente al campo de contraseña sin hacer clic
            wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/form/div[4]/div/div/div[2]/div[3]/input'))).click()
            # --- Inicia el proceso
            time.sleep(1)
            driver.switch_to.frame(0)
            # circunscripcion
            wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/form/div[3]/div/div[2]/div/table/tbody/tr[1]/td'))).click() 
            driver.switch_to.default_content()
            # ---- SI ES PRIMERA INSTANCIA
            if int(monto) > (jornal*300):
                st.write("es mayor a 300 jornales")
                waitclick(1,'/html/body/form/div[5]/div/div[2]/div/div/table/tbody/tr/td[1]/div/div/div/ul/li[1]/div/ul/li[1]/a',driver) 
            else:
                st.write("es menor a 300 jornales")
                jpaz = wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/form/div[5]/div/div[2]/div/div/table/tbody/tr/td[1]/div/div/div/ul/li[2]'))).click()
                time.sleep(1)
                civil = wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/form/div[5]/div/div[2]/div/div/table/tbody/tr/td[1]/div/div/div/ul/li[2]/div/ul/li[1]'))).click()
            # ---- Agregar Caso
            time.sleep(1)
            agregarCaso = driver.find_element(By.XPATH, '/html/body/form/div[5]/div/div[2]/div/div/table/tbody/tr/td[3]/div/div/div/div[2]/div/div/table/thead/tr[1]/td/table/tbody/tr[1]/td[2]/a').click()
            time.sleep(0.2)
            driver.switch_to.frame('rwDetalle')
            driver.find_element(By.XPATH, '/html/body/form/div[4]/div[2]/div/div[1]/div[2]/div/table/tbody/tr/td[2]/a').click() #distrito_btn
            time.sleep(1)
            st.write("- El botón de Agregar caso ha sido pulsado")
            # primera instancia ASUNCION o VILLA MORRA
            if int(monto) > (jornal*300):
                driver.find_element(By.XPATH, '/html/body/form/div[1]/div/div[1]/ul/li[2]').click() #distrito ASUNCION
            else:
                driver.find_element(By.XPATH, distrito_paz).click() #distrito VILLA MORRA
            time.sleep(1)
            driver.find_element(By.XPATH, '/html/body/form/div[5]/div[2]/div/div[2]/div[2]/div/table/tbody/tr/td[2]/a').click() #tipoProceso_btn
            time.sleep(0.5)
            driver.find_element(By.XPATH, '/html/body/form/div[1]/div/div[1]/ul/li[2]').click() #tipoProceso
            time.sleep(1)
            driver.switch_to.default_content()
            driver.switch_to.frame('rwDetalle')
            objetoBtn = driver.find_element(By.XPATH, '/html/body/form/div[4]/div[2]/div/div[3]/div[2]/div/table/tbody/tr/td[1]/input').click()
            time.sleep(1)
            objeto = driver.find_element(By.XPATH, '/html/body/form/div[1]/div/div[1]/ul/li[3]').click()
            time.sleep(1)

            if int(monto) > (jornal*100):
                a = 1
                # ------- OBSERVACION: SOLAMENTE PARA SIN TASA POR AHORA
                # # acá va si es tasa judicial
                # if not os.path.exists(id_juicio+" tasa.pdf"):
                #     st.write("El archivo "+juicio+" tasa.pdf NO EXISTE.")
                #     st.stop()      
                # with open(id_juicio+" tasa.pdf", "rb") as pdf_file:
                #     text = PyPDF3.PdfFileReader(pdf_file).getPage(0).extractText()
                #     lineas = text.split('\n') # Nro Liquidacion: lineas[4]
                #     nroLiquidacion = lineas[4]
                # nroLiquidacionInput = driver.find_element(By.ID, 'ctl16_txtNumeroLiquidacion')
                # nroLiquidacionInput.click()
                # nroLiquidacionInput.send_keys(nroLiquidacion)
                # time.sleep(1)
                # consultarLiquidacion = driver.find_element(By.ID, 'ctl16_btnVerificarliquidacion')
                # consultarLiquidacion.click() # consultarLiquidacion
            else:
                montoJuicio = driver.find_element(By.XPATH, '//html/body/form/div[4]/div[2]/div/div[4]/div[2]/span/input[1]')
                montoJuicio.click()
                montoJuicio.send_keys(monto)
                time.sleep(1)
                st.write("- Se ha cargado el monto del juicio")


            # Seleccionar nuevo juicio
            seleccionar2Div = driver.find_element(By.XPATH, '/html/body/form/div[4]/div[4]').click() 
            time.sleep(0.5)
            seleccionar2 = driver.find_element(By.XPATH, '/html/body/form/div[4]/div[4]/a[1]').click() 
            time.sleep(0.5)
            driver.switch_to.default_content()

            # ----- Registro de Causa
            p = '/html/body/form/div[5]/div/div[2]/div[1]/div/table/tbody/tr/td[3]/div/div/div/div[1]/div/div[4]/div[1]/div[7]/div[2]/span/input[1]'
            cantFojas = driver.find_element(By.XPATH, p)
            cantFojas.click()
            if int(monto) > (jornal*300):
                cantFojas.send_keys('15')
            else:
                cantFojas.send_keys('10')
            time.sleep(0.3)
            st.write("- Cantidad de fojas cargada")

            p = '/html/body/form/div[5]/div/div[2]/div[1]/div/table/tbody/tr/td[3]/div/div/div/div[1]/div/div[4]/div[2]/div/a[1]'
            registrar = driver.find_element(By.XPATH, p).click()
            time.sleep(1)
            #  --- boton partes de la causa
            p = '/html/body/form/div[5]/div/div[2]/div[1]/div/table/tbody/tr/td[1]/div/div/div/div/ul/li/div/ul/li[2]/a'
            partesBtn = driver.find_element(By.XPATH, p).click() 
            time.sleep(0.5)
            #  --- Agregar parte
            p = '/html/body/form/div[5]/div/div[2]/div/div/table/tbody/tr/td[3]/div/div/div/div[2]/div/div/table[1]/thead/tr/td/table/tbody/tr/td[2]/a'
            waitclick(2,p,driver)
            #  --- Agregar Demandante
            driver.switch_to.frame("rwDetalle")
            time.sleep(0.5)
            driver.find_element(By.XPATH, '/html/body/form/div[4]/div[3]/div[1]/div[1]/div[2]/div/table/tbody/tr/td[1]/input').send_keys('Demandante')# Tipo Parte
            waitclick(0.2,'/html/body/form/div[4]/div[3]/div[1]/div[2]/div[2]',driver) # Tipo de Persona Div click
            waitclick(0.5,'/html/body/form/div[4]/div[3]/div[1]/div[2]/div[2]/select/option[2]',driver) # Tipo de Persona 
            waitclick(0.1,'/html/body/form/div[4]/div[3]/div[1]/div[3]/div[2]',driver) #demandanteTipoDocDivCampo
            waitclick(0.1,'/html/body/form/div[4]/div[3]/div[1]/div[3]/div[2]/select/option[2]',driver) #demandanteTipoDocDivCampo
            waitclick(0.1,'/html/body/form/div[4]/div[3]/div[1]/div[4]/div[2]',driver) # demandante NroDoc DivCampo
            driver.find_element(By.XPATH, '/html/body/form/div[4]/div[3]/div[1]/div[4]/div[2]/span/input[1]').send_keys(actor_ruc)  #demandanteNroDoc
            waitclick(0.5,'/html/body/form/div[4]/div[3]/div[1]/div[4]/a',driver) # Demandante obtener datos
            waitclick(0.5,'/html/body/form/div[4]/div[3]/div[2]/div/table/tbody/tr/td[1]/input',driver) #demandanteSeleccionarDato
            waitclick(1,'/html/body/form/div[4]/div[4]/a[1]/input[1]',driver) #demandanteRegistrar
            st.write("- parte actora agregada")
            # ---- Actor Domicilio Real
            Agregar = driver.find_element(By.ID, 'ctl16_rdListaDomicilios_ctl00_ctl02_ctl00_lnkAgregar').click()
            driver.switch_to.frame(0)
            waitclick(0.1,'/html/body/form/div[3]/div/div[4]/div/div[1]/div[2]',driver) #demandanteTipoDomicilioProcesalDivCampo
            waitclick(0.1,'/html/body/form/div[3]/div/div[4]/div/div[1]/div[2]/select/option[3]',driver) #demandanteTipoDomicilioProcesal
            calle = wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/form/div[3]/div/div[4]/div/div[3]/div[2]/input')))
            calle.send_keys(actor_dom_real_calle)
            localidad = wait.until(EC.element_to_be_clickable((By.ID, 'ctl16_rcLocalidad_Input')))
            localidad.click()
            localidad.send_keys(actor_dom_real_ciudad)
            st.write("- parte actora domicilio real agregado")
            waitclick(2,'/html/body/form/div[4]/div/div[5]/a[1]/input[1]',driver) #demandanteRegistrarProcesal
            # ---- Switch to frame
            driver.switch_to.default_content()
            driver.switch_to.frame("rwDetalle")
            time.sleep(2)
            # ---- Actor Domicilio Procesal
            Agregar = driver.find_element(By.ID, 'ctl16_rdListaDomicilios_ctl00_ctl02_ctl00_lnkAgregar').click()
            driver.switch_to.frame(0)
            calle = wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/form/div[3]/div/div[4]/div/div[3]/div[2]/input')))
            calle.send_keys(actor_dom_procesal_calle)
            localidad = wait.until(EC.element_to_be_clickable((By.ID, 'ctl16_rcLocalidad_Input')))
            localidad.click()
            localidad.send_keys(actor_dom_procesal_ciudad)
            waitclick(2,'/html/body/form/div[4]/div/div[5]/a[1]/input[1]',driver) #demandanteRegistrarProcesal
            st.write("- parte actora domicilio procesal agregado")
            # ---- Guardar
            time.sleep(1)
            driver.switch_to.default_content()
            driver.switch_to.frame("rwDetalle")
            demandanteGuardar = driver.find_element(By.ID, 'ctl15_btnGuardar').click()
            time.sleep(0.5)
            demandanteCerrar = driver.find_element(By.ID, 'ctl15_btnCerrar').click()
            st.write("- parte demandada agregada")
            # ---- Switch to frame
            time.sleep(1)
            driver.refresh()
            driver.switch_to.default_content()
            #  --- Agregar Parte
            waitclick(1,'/html/body/form/div[5]/div/div[2]/div/div/table/tbody/tr/td[1]/div/div/div/ul/li/div/ul/li[2]/a/span/span[2]',driver)
            waitclick(2,'/html/body/form/div[5]/div/div[2]/div/div/table/tbody/tr/td[3]/div/div/div/div[2]/div/div/table[1]/thead/tr/td/table/tbody/tr/td[2]/a',driver)

            #  --- AGREGAR DEMANDADO
            driver.switch_to.frame("rwDetalle")
            time.sleep(0.5)
            demandadoTipoParteSelect = driver.find_element(By.XPATH, '/html/body/form/div[4]/div[3]/div[1]/div[1]/div[2]/div/table/tbody/tr/td[1]/input').send_keys('Demandado')
            waitclick(0.2,'/html/body/form/div[4]/div[3]/div[1]/div[2]/div[2]',driver) #demandadoTipoPersonaDivCampo
            waitclick(0.2,'/html/body/form/div[4]/div[3]/div[1]/div[2]/div[2]/select/option[1]',driver) #demandadoTipoPersona
            waitclick(0.2,'/html/body/form/div[4]/div[3]/div[1]/div[3]/div[2]',driver) #demandadoTipoDocDivCampo
            waitclick(0.2,'/html/body/form/div[4]/div[3]/div[1]/div[3]/div[2]/select/option[2]',driver) #demandadoTipoDoc
            waitclick(0.2,'/html/body/form/div[4]/div[3]/div[1]/div[4]/div[2]',driver) #demandadoNroDocDivCampo
            demandadoNroDoc = driver.find_element(By.XPATH, '/html/body/form/div[4]/div[3]/div[1]/div[4]/div[2]/span/input[1]').send_keys(data['ci1'])
            waitclick(0.5,'/html/body/form/div[4]/div[3]/div[1]/div[4]/a',driver) #demandadoObtener
            waitclick(1,'/html/body/form/div[4]/div[3]/div[2]/div/table/tbody/tr/td[1]/input',driver) #demandadoSeleccionarDato
            select_element = driver.find_element(By.ID, 'ctl15_lblSexo')
            select = Select(select_element)
            select_value = select.first_selected_option.get_attribute('value')
            select_value = int(select_value)
            if select_value == 0:
                select.select_by_value('1')
            waitclick(1,'/html/body/form/div[4]/div[4]/a[1]/input[1]',driver) #demandadoRegistrar
            # ---- Domicilio
            waitclick(2,'/html/body/form/div[4]/div[6]/div/div[1]/div/div/div/div/table/thead/tr[1]/td/table/tbody/tr/td[2]/a',driver) #agregar domicilio
            driver.switch_to.frame(0)
            waitclick(0.2,'/html/body/form/div[3]/div/div[4]/div/div[1]/div[2]',driver) #demandadoTipoDomicilioRealDivCampo
            waitclick(0.2,'/html/body/form/div[3]/div/div[4]/div/div[1]/div[2]/select/option[3]',driver) #demandadoTipoDomicilioReal
            calle = driver.find_element(By.XPATH, '/html/body/form/div[3]/div/div[4]/div/div[3]/div[2]/input')
            calle.send_keys(data['dom1'])
            localidad = driver.find_element(By.ID, 'ctl16_rcLocalidad_Input')
            localidad.click()
            localidad.send_keys(data['ciu1'])
            waitclick(2,'/html/body/form/div[4]/div/div[5]/a[1]/input[1]',driver) #demandadoRegistrarReal
            # ---- GUARDAR
            driver.switch_to.default_content()
            driver.switch_to.frame("rwDetalle")
            waitclick(1,'/html/body/form/div[5]/div[4]/a[1]',driver) #demandadoGuardar
            waitclick(1,'/html/body/form/div[4]/div[4]/a[2]/input[1]',driver) #demandadoCerrar
            st.write("- parte demandada domicilio agregado")

            # ---- Agregar Codeudor
            if data['ci2'] is not None and data['ci2'].isdigit():
                # ---- Switch to frame
                time.sleep(1)
                driver.refresh()
                driver.switch_to.default_content()
                #  --- Agregar Parte
                waitclick(1,'/html/body/form/div[5]/div/div[2]/div/div/table/tbody/tr/td[1]/div/div/div/ul/li/div/ul/li[2]/a/span/span[2]',driver)
                waitclick(2,'/html/body/form/div[5]/div/div[2]/div/div/table/tbody/tr/td[3]/div/div/div/div[2]/div/div/table[1]/thead/tr/td/table/tbody/tr/td[2]/a',driver)
                driver.switch_to.frame("rwDetalle")
                tipoParte = driver.find_element(By.XPATH, '/html/body/form/div[4]/div[3]/div[1]/div[1]/div[2]/div/table/tbody/tr/td[1]/input').send_keys('Demandado')
                waitclick(0.2,'/html/body/form/div[4]/div[3]/div[1]/div[2]/div[2]',driver) #demandadoTipoPersonaDivCampo
                waitclick(0.2,'/html/body/form/div[4]/div[3]/div[1]/div[2]/div[2]/select/option[1]',driver) #demandadoTipoPersona
                waitclick(0.2,'/html/body/form/div[4]/div[3]/div[1]/div[3]/div[2]',driver) #demandadoTipoDocDivCampo
                waitclick(0.2,'/html/body/form/div[4]/div[3]/div[1]/div[3]/div[2]/select/option[2]',driver) #demandadoTipoDoc
                waitclick(0.2,'/html/body/form/div[4]/div[3]/div[1]/div[4]/div[2]',driver) #demandadoNroDocDivCampo
                NroDoc = driver.find_element(By.XPATH, '/html/body/form/div[4]/div[3]/div[1]/div[4]/div[2]/span/input[1]').send_keys(data['ci2'])
                waitclick(0.5,'/html/body/form/div[4]/div[3]/div[1]/div[4]/a',driver) #demandadoObtener
                waitclick(1,'/html/body/form/div[4]/div[3]/div[2]/div/table/tbody/tr/td[1]/input',driver) #demandadoSeleccionarDato
                waitclick(1,'/html/body/form/div[4]/div[4]/a[1]/input[1]',driver) #demandadoRegistrar
                # ---- Domicilio
                waitclick(2,'/html/body/form/div[4]/div[6]/div/div[1]/div/div/div/div/table/thead/tr[1]/td/table/tbody/tr/td[2]/a',driver) #agregar domicilio
                driver.switch_to.frame(0)
                waitclick(0.2,'/html/body/form/div[3]/div/div[4]/div/div[1]/div[2]',driver) #demandadoTipoDomicilioRealDivCampo
                waitclick(0.2,'/html/body/form/div[3]/div/div[4]/div/div[1]/div[2]/select/option[3]',driver) #demandadoTipoDomicilioReal
                calle = driver.find_element(By.XPATH, '/html/body/form/div[3]/div/div[4]/div/div[3]/div[2]/input')
                calle.send_keys(data['dom2'])
                localidad = driver.find_element(By.ID, 'ctl16_rcLocalidad_Input')
                localidad.click()
                localidad.send_keys(data['ciu1'])
                waitclick(2,'/html/body/form/div[4]/div/div[5]/a[1]/input[1]',driver) #demandadoRegistrarReal
                # ---- GUARDAR
                driver.switch_to.default_content()
                driver.switch_to.frame("rwDetalle")
                waitclick(1,'/html/body/form/div[5]/div[4]/a[1]',driver) #demandadoGuardar
                waitclick(1,'/html/body/form/div[4]/div[4]/a[2]/input[1]',driver) #demandadoCerrar

            # ---- Si es Primera Instancia ya debe estar cargado
            #  FISCALIZADO, DOCUMENTOS, PODER

            driver.switch_to.default_content()
            # ----- Agregar pdf de la preparación del juicio
            time.sleep(2)
            datosGenerales = driver.find_element(By.XPATH, '/html/body/form/div[6]/div/div[2]/div/div/table/tbody/tr/td[1]/div/div/div/ul/li/div/ul/li[1]/a/span/span[2]').click()
            # datosGenerales              
            time.sleep(2)
            # Documentos
            driver.find_element(By.XPATH, '/html/body/form/div[5]/div/div[2]/div[1]/div/table/tbody/tr/td[3]/div/div/div/div[1]/div[2]/div/ul/li[2]/a/span/span/span').click()
            time.sleep(2)

            # Agregar Documentos
            driver.find_element(By.XPATH, '/html/body/form/div[5]/div/div[2]/div[1]/div/table/tbody/tr/td[3]/div/div/div/div[1]/div[3]/div[2]/div/div/div/div/table[1]/thead/tr/td/table/tbody/tr/td[2]/a').click()
            driver.switch_to.frame("rwDetalle")
            time.sleep(1)
            if int(monto) > (jornal*300):
                cant_fojas_nro = '4'
                archivo_alzar = "poder_general_union.pdf"
            else:
                cant_fojas_nro = '1'
                archivo_alzar = "tasas/"+id_juicio + "-archivo.pdf"
                
            # Cantidad de Fojas
            cantFojas = driver.find_element(By.XPATH, '/html/body/form/div[3]/div[2]/div/div[3]/div[2]/span/input[1]')
            cantFojas.send_keys(cant_fojas_nro)
            # subir archivo
            if int(monto) > (jornal*300):
                tipo_doc = driver.find_element(By.XPATH, '/html/body/form/div[3]/div[2]/div/div[2]/div[2]/div/table/tbody/tr/td[1]/input')
                tipo_doc.click()
                time.sleep(1)
                tipo_doc2 = driver.find_element(By.XPATH, '/html/body/form/div[1]/div/div/ul/li[2]')
                tipo_doc2.click()
            input_file_pdf = driver.find_element(By.ID, "ctl16_AsyncUpload1file0")
            input_file_pdf.send_keys(os.path.abspath(archivo_alzar))
            time.sleep(4)
            # Guardar archivo
            guardarArchivo = driver.find_element(By.ID, "ctl16_btnGuardar_input")
            guardarArchivo.click()
            driver.switch_to.default_content()
            time.sleep(5)
            st.write("- documentos alzados")

            # ---- SORTEAR
            SORTEAR = driver.find_element(By.XPATH, '/html/body/form/div[5]/div/div[2]/div[1]/div/table/tbody/tr/td[3]/div/div/div/div[1]/div[1]/div[4]/div[2]/div/a[2]')
            SORTEAR.click()
            st.write("- sortear click realizado")
            time.sleep(5)
            alert = driver.switch_to.alert
            alert.accept()
            time.sleep(2)
            st.write("- alert aceptado")
            driver.switch_to.window(driver.window_handles[1])
            st.write("- driver switch_to window 1")
            # popup_url = driver.current_url
            # st.write("- popup_url obtenido" + driver.current_url)
            # driver.switch_to.window(driver.window_handles[0])
            # st.write("- se solicita switch_to default_content")
            # time.sleep(5)
            st.write("- causa sorteada")

            # carpeta_descargas = '.'
            # archivos_en_descargas = os.listdir(carpeta_descargas)
            # # Inicializa la variable para el número más alto
            # numero_mas_alto = 0
            # # Busca el número más alto en los nombres de los archivos
            # for archivo in archivos_en_descargas:
            #     if archivo.startswith("Contraseña Entrada ") and archivo.endswith(".pdf"):
            #         # Extrae solo los dígitos del nombre del archivo
            #         numero_str = ''.join(filter(str.isdigit, archivo))
            #         if numero_str:
            #             numero = int(numero_str)
            #             numero_mas_alto = max(numero_mas_alto, numero)

            # # Construye el nombre del archivo más alto
            # nombre_archivo_mas_alto = f"Contraseña Entrada {numero_mas_alto}.pdf"
            # # Rutas de archivo de origen y carpeta de destino
            # archivo_a_copiar = os.path.join(carpeta_descargas, nombre_archivo_mas_alto)
            # path_carpeta_destino = "tasas/"
            # carpeta_destino = os.path.join(path_carpeta_destino, f"{juicio}-caratula.pdf")
            # # Copia el archivo a la carpeta de destino y cambia su nombre
            # shutil.copy(archivo_a_copiar, carpeta_destino)
            # # Ruta del archivo original en la carpeta de descargas
            # archivo_original = os.path.join(carpeta_descargas, nombre_archivo_mas_alto)
            # # Borra el archivo original en la carpeta de descargas
            # os.remove(archivo_original)

            # # ENVIAR CARATULA AL SERVIDOR
            # pdf_path = "./tasas/" + str(juicio) + "-caratula.pdf"
            # # URL de tu hosting para recibir el archivo
            # upload_url = "https://" + controlador + "/uploadcaratula"  
            # # Mostrar progreso en Streamlit
            # st.write(f"📤 Enviando el archivo  al servidor...")
            # try:
            #     # Abrir el archivo y enviarlo como parte del POST
            #     with open(pdf_path, "rb") as pdf_file:
            #         files = {"file": (f"{juicio}-caratula.pdf", pdf_file, "application/pdf")}
            #         headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}
            #         response = requests.post(upload_url, files=files)
            #     # Verificar la respuesta del servidor
            #     if response.status_code == 200:
            #         st.success(f"✅ Archivo enviado con éxito al servidor.")
            #         # st.write("Respuesta del servidor:", response.text)
            #     else:
            #         st.error(f"❌ Error al enviar el archivo. Código de estado: {response.status_code}")
            #         st.write("Mensaje del servidor:", response.text)
            # except Exception as e:
            #     st.error(f"⚠️ Ocurrió un error al enviar el archivo: {e}")


            time.sleep(3)
            tiempo_fin = time.time()
            duracion = round( tiempo_fin - tiempo_inicio)
            st.write("FINALIZADO. En " + str(duracion) + " segundos !!!")

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
