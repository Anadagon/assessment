import datetime
from django.db import models
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db.models.signals import post_delete, post_save
from django.db.models.signals import class_prepared
from django.core.validators import MaxLengthValidator
from django.utils.translation import ugettext as _
from uuid import uuid4
from django.utils.text import slugify

try:
    from django.contrib.auth import get_user_model
    User = get_user_model()
except ImportError:
    from django.contrib.auth.models import User


# allow longer username
def longer_username_signal(sender, *args, **kwargs):
    if sender.__name__ == "User" and sender.__module__ == "django.contrib.auth.models":
        patch_user_model(sender)
class_prepared.connect(longer_username_signal)

MAX_LENGTH = 200

def patch_user_model(model, fieldname):
    field = model._meta.get_field(fieldname)

    field.max_length = MAX_LENGTH
    field.help_text = _("Required, %s characters or fewer. Only letters, "
                        "numbers, and @, ., +, -, or _ "
                        "characters." % MAX_LENGTH)

    # patch model field validator because validator doesn't change if we change
    # max_length
    for v in field.validators:
        if isinstance(v, MaxLengthValidator):
            v.limit_value = MAX_LENGTH

# check if User model is patched
if User._meta.get_field("username").max_length != MAX_LENGTH:
    patch_user_model(User, "username")
    patch_user_model(User, "email")
    patch_user_model(User, "first_name")
    patch_user_model(User, "last_name")


class Survey(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=255)
    insertion = models.CharField(max_length=200, blank=True)
    description = models.TextField()
    pub_date = models.DateTimeField(auto_now=False, default=datetime.datetime.now)
    external_survey_url = models.CharField(max_length=255, blank=True)
    minutes_allowed = models.FloatField(max_length=10, default=0)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        app_label = 'assessment'
        ordering = ['pub_date']
        verbose_name = "Survey"
        verbose_name_plural = "Surveys"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('assessment:assessment_survey', kwargs={'slug': self.slug})
    
    def get_external_url(self):
        if 'https://' in self.external_survey_url or 'http://' in self.external_survey_url:
            return self.external_survey_url
        else:
            return False

    def save(self, *args, **kwargs):
        varprocs1 = [self.insertion]
        i = 0
        if self.insertion is not "":
            while i < 20:
                try:
                    self.description = self.description % tuple(varprocs1)
                except TypeError:
                    i += 1
                    varprocs1.append(self.insertion)
        self.slug = slugify(self.name)
        super(Survey, self).save(*args, **kwargs)


class SurveyImage(models.Model):
    survey = models.ForeignKey(Survey, related_name='images')
    image = models.ImageField(upload_to='assessment', blank=True)
    
    def __str__(self):
        return self.image.url


class Available(models.Model):
    user = models.ForeignKey(User)
    survey = models.ForeignKey(Survey)
    url = models.CharField(max_length=255)
    
    class Meta:
        app_label = 'assessment'
        unique_together = ('survey', 'user')


class Question(models.Model):
    TRUEFALSE = 1
    MULTICHOICE = 2
    TEXT = 3
    EXTERNAL = 4
    MULTISELECT = 5
    RANGE = 6
    DISPOSITION = 7

    QUESTION_TYPE = (
        (TRUEFALSE, 'True or False'),
        (MULTICHOICE, 'Multiple Choice'),
        (MULTISELECT, 'Multiple Select'),
        (TEXT, 'Text'),
        (EXTERNAL, 'External Survey'),
        (RANGE, 'Range'),
        (DISPOSITION, 'Disposition'),
    )

    survey = models.ForeignKey(Survey)
    page_number = models.DecimalField(max_digits=2, decimal_places=0, default=1)
    question_sum = models.IntegerField(max_length=25, blank=True, null=True)
    question_name = models.CharField(max_length=255)
    question = models.TextField()
    question_type = models.IntegerField(
        max_length=1,
        choices=QUESTION_TYPE,
        default=MULTICHOICE)

    class Meta:
        app_label = 'assessment'
        ordering = ['survey', 'id']
        verbose_name = 'Question'
        verbose_name_plural = 'Questions'

    def __str__(self):
        return self.question

    def save(self, *args, **kwargs):
        varprocs1 = [self.survey.insertion]
        i = 0
        if self.survey.insertion is not "":
            while i < 20:
                try:
                    self.question = self.question % tuple(varprocs1)
                except TypeError:
                    i += 1
                    varprocs1.append(self.survey.insertion)
        if self.question_sum is None:
            self.question_sum = 100
        super(Question, self).save(*args, **kwargs)


class Choice(models.Model):
    question = models.ForeignKey(Question)
    choice_value = models.TextField(max_length=500)
    weight = models.FloatField(max_length=10, default=0)

    class Meta:
        app_label = 'assessment'
        ordering = ['id']
    
    def __str__(self):
        return self.choice_value

    def save(self, *args, **kwargs):
        varprocs1 = [self.question.survey.insertion]
        i = 0
        if self.question.survey.insertion is not "":
            while i < 20:
                try:
                    self.choice_value = self.choice_value % tuple(varprocs1)
                except TypeError:
                    i += 1
                    varprocs1.append(self.question.survey.insertion)
        super(Choice, self).save(*args, **kwargs)


class Result(models.Model):
    user = models.ForeignKey(User, related_name='results', editable=False)
    survey = models.ForeignKey(Survey, related_name='results', editable=False)
    started_on = models.DateTimeField(auto_now=False, editable=False)
    completed_on = models.DateTimeField(auto_now=True, default=datetime.datetime.now)
    excess_seconds = models.IntegerField(editable=False)
    score = models.CharField(max_length=10, default=0, editable=False)

    class Meta:
        app_label = 'assessment'
        unique_together = ('survey', 'user')

    def __str__(self):
        return "%s, %s" % (self.survey, self.user)

    def get_absolute_url(self):
        return reverse('assessment:survey_results', kwargs={'pk': self.id})


class Answer(models.Model):
    result = models.ForeignKey(Result, related_name='answers', editable=False)
    question = models.ForeignKey(Question, related_name='answers', editable=False)
    answer = models.TextField(blank=True, null=True)

    class Meta:
        app_label = 'assessment'
        ordering = ['result', 'question']
        verbose_name = 'Answer'
        verbose_name_plural = 'Answers'
    
    def __str__(self):
        return self.answer


class UserProfile(models.Model):
    user = models.ForeignKey(User, unique=True)
    gender = models.CharField(max_length=MAX_LENGTH, blank=True, null=True)
    phone_number = models.CharField(max_length=MAX_LENGTH, blank=True, null=True)
    job_title = models.CharField(max_length=MAX_LENGTH, blank=True, null=True)
    job_department = models.CharField(max_length=MAX_LENGTH, blank=True, null=True)
    job_location = models.CharField(max_length=MAX_LENGTH, blank=True, null=True)
    company = models.CharField(max_length=MAX_LENGTH, blank=True, null=True)
    assessment_protocol = models.CharField(max_length=MAX_LENGTH, blank=True, null=True)
    profile_token = models.CharField(max_length=MAX_LENGTH, blank=True, null=True, unique=True)

    def get_absolute_url(self):
        return reverse('assessment:assessment_results', args=(user.id,))

    def save(self, *args, **kwargs):
        if not self.id:
            self.profile_token = str(uuid4())
        super(UserProfile, self).save(*args, **kwargs)


def create_user_profile(sender, instance, **kwargs):
    try:
        UserProfile.objects.create(user=instance)
    except:
        pass


def delete_user_profile(sender, instance, **kwargs):
    try:
        UserProfile.objects.get(user=instance).delete()
    except:
        pass


post_save.connect(create_user_profile, sender=User)
post_delete.connect(delete_user_profile, sender=User)
