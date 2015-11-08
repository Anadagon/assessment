#add from assessment.settings_local import * to project settings.py

LOGIN_URL = 'assessment:assessment_login'
LOGOUT_URL = 'assessment:assessment_logout'
LOGIN_REDIRECT_URL = 'assessment:assessment_index'

AUTH_PROFILE_MODULE = 'assessment.UserProfile'

AUTHENTICATION_BACKENDS = (
    'assessment.auth.EmailOrUsernameModelBackend',
    'django.contrib.auth.backends.ModelBackend'
)
