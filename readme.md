# Assessment Automation System

### Installation

#### Requirements

 * PostgreSQL (and psycopg2) or MySQL
 * Python
 * Python/Django
 * Python/Pillow
 * Python/pip
 * Django-braces

#### Steps

1. On Arch Linux: ```sudo pacman -S postgresql python python-psycopg2 python-django python-pillow python-pip```
2. Install Django-braces via pip: ```sudo pip install django-braces```
3. Create a new Django project: ```python django-admin.py startproject yourdjangodirectory```
4. Configure your webserver to point to Django, or use the built-in server by changing directory to your project: ```cd /path/to/yourdjangodirectory``` and running ```python manage.py runserver```. The site will be available at ```http://127.0.0.1:8000/```
5. ```cd``` into the Django root folder and ```git clone git@bitbucket.org:jlanzobr/assessment.git```
6. Add ```url(r'^assessment/', include('assessment.urls', namespace="assessment", app_name='assessment')),``` to the urlpatterns in your project's urls.py
7. Define the following in your project's ```settings.py```:
    1. ```STATIC_URL = '/python/static/'```
    2. ```MEDIA_URL = '/python/media/'```
    3. ```STATIC_ROOT = os.path.join(BASE_DIR, 'static')```
    4. ```MEDIA_ROOT = os.path.join(BASE_DIR, 'media')```
    5. ```STATICFILES_DIRS = ("/usr/lib/python3.4/site-packages/django/contrib/admin/static/admin/",)```
8. Add ```'assessment',``` to ```INSTALLED_APPS``` in ```settings.py```
9. Run ```python manage.py syncdb``` to create the database
10. Run ```python manage.py collectstatic``` to link all the CSS and JavaScript so it can be used.
11. To create the PDS Inventory survey: ```python manage.py pdssurvey```
12. To create the case analysis survey: a) copy or move management/commands/casestudyfile.jpg to the MEDIA_URL defined in settings.py (eg. /python/media/assessment/)
                                        b) run ```python manage.py casestudy``` 