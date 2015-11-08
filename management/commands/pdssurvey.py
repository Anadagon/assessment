import sys

from django.utils import timezone
from django.core.management.base import NoArgsCommand
from django.db import IntegrityError

from assessment.models import Survey, Question, Choice


class Command(NoArgsCommand):

    survey_instance = {
        'name': 'PDS Survey',
        'slug': 'PDSSurvey',
        'description': "This measure assesses the way you make decisions in a variety of different contexts. Please"
                       "answer each statement by selecting the choice that best describes you. The answers range from"
                       " 1(Not True) to 5(Very True)",
        'pub_date': timezone.now(),
        'is_active': 'True',
    }

    questions = [

        {
            'question': 'My first impressions of people usually turn out to be right',
            'question_type': '2',
        },

        {
            'question': 'It would be hard for me to break any of my bad habits',
            'question_type': '2',
        },

        {
            'question': 'I don\'t care to know what other people really think of me',
            'question_type': '2'
        },

        {
            'question': 'I have not always been honest with myself',
            'question_type': '2',
        },

        {
            'question': 'I always know why I like things',
            'question_type': '2',
        },

        {
            'question': 'When my emotions are aroused, it biases my thinking',
            'question_type': '2',
        },

        {
            'question': 'Once I\'ve made up my mind, other people cannot change my opinion',
            'question_type': '2',
        },

        {
            'question': 'I am not a safe driver when I exceed the speed limit',
            'question_type': '2',
        },

        {
            'question': 'I am fully in control of my own fate',
            'question_type': '2',
        },

        {
            'question': 'It\'s hard for me to shut off a disturbing thought',
            'question_type': '2',
        },

        {
            'question': 'I never regret my decisions',
            'question_type': '2',
        },

        {
            'question': 'I sometimes lose out on things because I can\'t make up my mind soon enough',
            'question_type': '2',
        },

        {
            'question': 'The reason I vote is because my vote can make a difference',
            'question_type': '2',
        },

        {
            'question': 'People don\'t seem to notice me and my abilities',
            'question_type': '2',
        },

        {
            'question': 'I am a completely rational person',
            'question_type': '2',
        },

        {
            'question': 'I rarely appreciate criticism',
            'question_type': '2',
        },

        {
            'question': 'I am very confident about my judgements',
            'question_type': '2',
        },

        {
            'question': 'I have sometimes doubted my ability as a lover',
            'question_type': '2',
        },

        {
            'question': 'It\'s alright with me if some people happen to dislike me',
            'question_type': '2',
        },

        {
            'question': 'I\'m just an average person',
            'question_type': '2',
        },

        {
            'question': 'I sometimes tell lies if I have to',
            'question_type': '2',
        },

        {
            'question': 'I never cover up my mistakes',
            'question_type': '2',
        },

        {
            'question': 'There have been occasions when I have taken advantage of someone',
            'question_type': '2',
        },

        {
            'question': 'I never swear',
            'question_type': '2',
        },

        {
            'question': 'I sometimes try to get even rather than forgive and forget',
            'question_type': '2',
        },

        {
            'question': 'I always obey laws, even if I\'m unlikely to get caught',
            'question_type': '2',
        },

        {
            'question': 'I have said something bad about a friend behind their back',
            'question_type': '2',
        },

        {
            'question': 'When I hear people talking privately, I avoid listening',
            'question_type': '2',
        },

        {
            'question': 'I have received too much change from a salesperson without telling him or her',
            'question_type': '2',
        },

        {
            'question': 'I always declare everything at customs',
            'question_type': '2',
        },

        {
            'question': 'When I was young, I sometimes stole things',
            'question_type': '2',
        },

        {
            'question': 'I never dropped litter on the street',
            'question_type': '2',
        },

        {
            'question': 'I sometimes drive faster than the speed limit',
            'question_type': '2',
        },

        {
            'question': 'I never read sexy books or magazines',
            'question_type': '2',
        },

        {
            'question': 'I have done things that I don\'t tell other people about',
            'question_type': '2',
        },

        {
            'question': 'I never take things that don\'t belong to me',
            'question_type': '2',
        },

        {
            'question': 'I have taken sick-leave from work or school even when I wasn\'t really sick',
            'question_type': '2',
        },

        {
            'question': 'I have never damaged a library book or store merchandise without reporting it',
            'question_type': '2',
        },

        {
            'question': 'I have some pretty awful habits',
            'question_type': '2',
        },

        {
            'question': 'I don\'t gossip about other people\'s business',
            'question_type': '2',
        },

    ]

    choices = [

        {
            'choice_value': 'Not True',
            'weight': 1,
        },

        {
            'choice_value': 'Mostly Untrue',
            'weight': 2,
        },

        {
            'choice_value': 'Somewhat True',
            'weight': 3,
        },

        {
            'choice_value': 'Mostly True',
            'weight': 4,
        },

        {
            'choice_value': 'Very True',
            'weight': 5,
        },

    ]

    help = 'Creates a pds inventory survey.'

    def handle_noargs(self, *args, **options):
        try:
            survey = Survey(**self.survey_instance)
            survey.save()
            q = {}
            c = {}
            for i in range(40):
                q[i] = Question(survey=survey, **self.questions[i])
                q[i].save()
                for j in range(5):
                    c[j] = Choice(question=q[i], **self.choices[j])
                    c[j].save()

            self.stdout.write(
                "Successfully created pds survey: %s" % survey.slug
            )
        except IntegrityError:
            err = sys.exc_info()[0]
            self.stdout.write(
                "FAILED to create pds survey: %s" % err
            )