import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.os_manager import ChromeType
from bs4 import BeautifulSoup

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

# Usar el controlador para acceder a una página web
driver = get_driver()
if driver:
    try:
        driver.get("http://example.com")
        
        # Analizar el HTML de la página con BeautifulSoup
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        # Extraer el contenido del primer elemento <h1>
        h1_text = soup.find('h1').get_text() if soup.find('h1') else "No se encontró <h1>"
        
        # Mostrar el contenido en Streamlit
        st.write("Contenido del <h1>:")
        st.code(h1_text)
    except Exception as e:
        st.error(f"Error al cargar la página: {e}")
    finally:
        driver.quit()
else:
    st.error("No se pudo inicializar el controlador de Selenium.")
