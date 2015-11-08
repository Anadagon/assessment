import sys
from django.conf import settings
from django.utils import timezone
from django.core.management.base import NoArgsCommand
from django.db import IntegrityError

from assessment.models import Survey, Question, SurveyImage


class Command(NoArgsCommand):

    survey_instance = {
        'name': 'Case Analysis',
        'slug': 'casestudy',
        'description': 'Respond to the following questions using information gathered from the case study.',
        'pub_date': timezone.now(),
        'minutes_allowed': 45,
        'is_active': 'True',
    }

    image = {
        'image': settings.MEDIA_URL + 'assessment/casestudyfile.jpg'
    }

    questions = [

        {
            'question': 'What is the problem?',
            'question_type': '3',
        },

        {
            'question': 'What is the best solution?',
            'question_type': '3',
        },

        {
            'question': 'Defend your answer to #2 with facts and data from the case.',
            'question_type': '3',
        }
    ]

    help = 'Creates the Case Study Survey.'

    def handle_noargs(self, **options):
        try:
            survey = Survey(**self.survey_instance)
            survey.save()
            image = SurveyImage(survey=survey, **self.image)
            image.save()
            q = {}
            for i in range(3):
                q[i] = Question(survey=survey, **self.questions[i])
                q[i].save()

            self.stdout.write(
                "Successfully created case study survey: %s" % survey.slug
            )

        except IntegrityError:
            err = sys.exc_info()[0]
            self.stdout.write(
                "FAILED to create case study survey: %s" % err
            )