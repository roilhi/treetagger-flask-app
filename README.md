# 🧠 Proyecto LCR Lab
El sitio web está disponible desde la url [lcrlab.com.mx](https://lcrlab.com.mx)
El laboratorio LCR es una iniciativa de investigación independiente dedicada al diseño, desarrollo y análisis de corpus y herramientas digitales ligüísticas. El laboratorio integra la compilación de corpus y construicción de bases de datos morfológicas, procesamiento computacional, metodología e innovación con un marco de investigación coherente.

A través de LCR Lab se hospedan 3 iniciativas:

- [**MexLeC 3.0:**](https://lcrlab.com.mx/mexlec) Corpus Longitudinal Mexicano de Aprendizaje 
- [**Morph 1.0:**](https://lcrlab.com.mx/morph) Aplicación de análisis lingüístico de textos ligado a una base de datos
- [**Seminario Permanente de LCR:**](https://lcrlab.com.mx/seminario) Series de seminarios para el intercambio académico de información sobre métodos de corpus de aprendizaje

# Morph: 
Aplicación web basada en un corpus para el conteo de sufijos derivados y para la identificación de palabras complejas que los contengan.
## 🚀 Características
- **Etiquetado de textos**: Morph realiza el etiquetado o asignación de tags a través de la librería [TreeTagger](https://www.cis.uni-muenchen.de/~schmid/tools/TreeTagger/), particularmente la versión diseñada para Python: [*TreeTagger Wrapper*](https://treetaggerwrapper.readthedocs.io/en/latest/). Teniendo los tags de referencia, la aplicación etiqueta cada palabra de un archivo txt y cuenta las veces que se repite para cada palabra, creando una tabla de referencia así como un archivo txt disponible para su descarga con los tags encontrados.
- **Almacenamiento y Corpus:** Por medio de una base de datos en MongoDB, se almacenan los registros de un corpus. Cada documento es una palabra con sus respectivas etiquetas, así como el sufijo correspondiente. Esto permite un análisis un análisis más profundo para cada palabra
- **Aplicación web:** A través de la herramienta Flask de Python, Morph provee una interfaz gráfica en un ambiente amigable para el usuario, de tal manera que pueda cargar archivos de texto, visualizar el conteo de sufijos y etiquetas, así como descargar un texto etiquetado.
- **Diseño responsivo:** La aplicación web ofrece una experiencia de diseño responsiva, de tal forma que el usuario pueda utilizarla en varios dispositivos y pantallas con diferentes tamaños sin afectar las vistas.

## 🛠️ Herramientas (STACK) Técnico de Morph
* **Frontend**: HTML, CSS, Bootstrap
* **Backend**: Flask, Python
* **Base de datos**: MongoDB
* **Procesamiento del texto**: TreeTagger
* **Análisis de datos**: Pandas, NumPy, SciPy, scikit-learn
* **Contenedores**: Docker
* **Orquestación**: Docker Compose

## 📦 Instalación
Para instalar el proyecto se deberán seguir los siguientes pasos:
1. Clonar el repositorio usando `git clone`.
2. Instalar las dependencias usando `pip install -r requirements.txt`.
3. Crear la imagen de Docker `docker build -t lcr-lab`.
4. Correr el contenedor `docker run -p 5000:5000 lcr-lab`.
Los pasos 3-5 se pueden suplir por el comando
a. `docker-compose up`

## 💻 Manual de uso
Para usar Morph, se deberán seguir los siguientes pasos:
1. Dar clic en el menú de Morph, en la sección Test Morph:
   <img width="1256" height="431" alt="image" src="https://github.com/user-attachments/assets/15478c82-5b6e-4951-8a10-0284a10a6dee" />
2. Cargar un archivo de texto (.txt) en la aplicación:
<img width="1276" height="437" alt="image" src="https://github.com/user-attachments/assets/362f8a07-c4fe-4e57-a9fc-e4d9b2bead0d" />
2. Dar clic en `Process File` (Procesar Archivo)
<img width="1276" height="437" alt="image" src="https://github.com/user-attachments/assets/3ad34a6c-b48b-490d-8a70-d28d1786ba7a" />

3. La aplicación hará el etiquetado llamado a la librería *TreeTagger Wrapper*

4. Se hará una consulta a la base de datos MongoDB para cada palabra de acuerdo con su etiqueta

5. De acuerdo con las coincidencias en los sufijos y etiquetas de cada palabra se realizará un conteo

6. El usuario podrá visualizar una tabla con el respectivo conteo de palabras y sufijos que se encuentren en la base de datos
   <img width="1435" height="857" alt="image" src="https://github.com/user-attachments/assets/6231e70b-2adf-4e7a-84df-364bd5f40b51" />
7. Si el usuario lo desea, puede descargar el texto con las etiquetas por medio del botón `Download Tagged File`
<img width="1296" height="482" alt="image" src="https://github.com/user-attachments/assets/8cb9a407-4066-49ad-b921-c09b1b5d32cc" />

<img width="1909" height="604" alt="image" src="https://github.com/user-attachments/assets/4646d15c-30a0-452e-a059-e90fe6ac19f1" />
 
## 🤝 Contribuir
Para contribuir con el proyecto, se le pide a los usuarios hacer un *fork* al repositorio y someter un *pull request* con los cambios realizados. En caso de uso de la herramienta con fines académicos, se podrá realizar de la siguiente manera:
`Flores, A. (2026). Mexican Learner Corpus 3.0 [Data set]. DOI:` 
## 📝 Licencia
Mexican Learner Corpus (MexLeC) 3.0 está bajo la licencia de *Creative Commons Attribution-NonCommercial 4.0 International License (CC BY-NC 4.0)*, que puede consultarse en [este enlace](https://creativecommons.org/licenses/by-nc/4.0/)

## 📬 Contacto
Para mayor información favor de contactar a la dirección email [mexicanlearnercorpus@gmail.com](mexicanlearnercorpus@gmail.com).
