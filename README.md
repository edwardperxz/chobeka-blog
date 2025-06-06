# ChobekaBlog

ChobekaBlog es un proyecto de blog panameño para compartir memes, desarrollado utilizando Django, Celery y Redis.

## Requisitos

- Python 3.10+
- Redis (para tareas asíncronas con Celery)
- (Opcional) Anaconda para gestión de entornos

## Instalación

1. **Clona el repositorio**

   ```sh
   git clone <URL-del-repo>
   cd chobeka-blog
   ```

2. **Crea un entorno virtual (opcional pero recomendado)**

   ```sh
   python -m venv venv
   source venv/bin/activate  # En Windows: venv\Scripts\activate
   ```

3. **Instala las dependencias**

   ```sh
   pip install -r requirements.txt
   ```

4. **Configura Redis**
   - Instala y ejecuta Redis en tu máquina (en Windows puedes usar Docker o instalar desde https://github.com/tporadowski/redis/releases).
   - Por defecto, Celery usará `redis://localhost:6379/0`.

5. **Aplica migraciones y crea un superusuario**

   ```sh
   python manage.py migrate
   python manage.py createsuperuser
   ```

6. **Ejecuta el servidor de desarrollo**

   ```sh
   python manage.py runserver
   ```

7. **Ejecuta el worker de Celery**

   > **IMPORTANTE:** Si usas Windows, ejecuta Celery con el pool solo:
   ```sh
   celery -A blogproject worker --loglevel=info --pool=solo
   ```

## Funcionalidades principales

- Registro e inicio de sesión con Google y Facebook (Django Allauth y social-auth)
- Publicación, edición y eliminación de blogs
- Comentarios y reseñas en blogs
- Exportación de datos a CSV desde el admin (tarea asíncrona con Celery)
- Editor enriquecido con CKEditor 5

## Exportar datos a CSV

Desde el panel de administración puedes exportar usuarios, blogs, reseñas y comentarios a archivos CSV. Esta tarea se ejecuta en segundo plano usando Celery y los archivos se guardan en la raíz del proyecto.

## Estructura del proyecto

- `blogapp/` - Aplicación principal con modelos, vistas, tareas y administración personalizada
- `blogproject/` - Configuración principal de Django y Celery
- `media/` - Archivos subidos por los usuarios
- `static/` - Archivos estáticos (CSS, JS, imágenes)

## Dependencias principales

Consulta `requirements.txt` para la lista completa. Incluye:
- Django
- Celery
- Redis
- django-allauth
- social-auth-app-django
- django-ckeditor-5
- widget-tweaks

## Notas
- Asegúrate de que Redis esté corriendo antes de iniciar el worker de Celery.
- Para producción, configura las variables de entorno y la seguridad adecuadamente.
- Si usas Windows, recuerda siempre agregar `--pool=solo` al comando de Celery.

---

Desarrollado por el equipo de ChobekaBlog.