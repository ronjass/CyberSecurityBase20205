from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from django.shortcuts import get_object_or_404, render
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
from django.utils import timezone
from django.views import generic
from django.db import connection

from .models import Choice, Question

""" FLAW 5: Add logging import and logger setup
import logging

logger = logging.getLogger(__name__)
"""

class IndexView(generic.ListView):
    template_name = 'polls/index.html'
    context_object_name = 'latest_question_list'

    def get_queryset(self):
        """
        Return the last five published questions (not including those set to be
        published in the future).
        """
        return Question.objects.filter(
            pub_date__lte=timezone.now()
        ).order_by('-pub_date')[:5]

class DetailView(generic.DetailView):
    model = Question
    template_name = 'polls/detail.html'

    def get_queryset(self):
        """
        Excludes any questions that aren't published yet.
        """
        return Question.objects.filter(pub_date__lte=timezone.now())

class ResultsView(generic.DetailView):
    model = Question
    template_name = 'polls/results.html'

""" FLAW 1: SQL Injection """
""" FLAW 4: Identification and Authentication Failures """
@csrf_exempt
def vote(request, question_id):
    choice_id = request.POST['choice']
    """ FIX FLAW 4: add the two lines below
    if request.session.get('voted_' + str(question_id)):
        return HttpResponseForbidden("You have already voted.")
    """
    with connection.cursor() as cursor:
        cursor.execute(
            f"UPDATE polls_choice SET votes = votes +1 WHERE id = {choice_id}"
        )
    """ FIX FLAW 4: add the line below
    request.session['voted_' + str(question_id)] = True
    """
    return HttpResponseRedirect(reverse('polls:results', args=(question_id,)))

""" FIX FLAW 1: SQL Injection: Delete the function above, including the @csrf_exempt 
    and add the function below.
    This function also includes the FIX for FLAW 4.

def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        # Redisplay the question voting form.
        return render(request, 'polls/detail.html', {
            'question': question,
            'error_message': "You didn't select a choice.",
        })
    else:
        if request.session.get('voted_' + str(question_id)):
            return HttpResponseForbidden("You have already voted.")
        
        selected_choice.votes += 1
        selected_choice.save()
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        request.session['voted_' + str(question_id)] = True
        return HttpResponseRedirect(reverse('polls:results', args=(question.id,)))
"""

""" FLAW 2: Broken Access Control """
""" FLAW 5: Security Logging and Monitoring Failures """
""" FIX FLAW 2: Broken Access Control: Add @login_required decorator
@login_required """
def delete_question(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    """ FIX FLAW 2: Add the if statement below
    if not request.user.is_staff:
    """
    """ FIX FLAW 5: Add the logging line below
        logger.warning(
            f"Unauthorized delete attempt by user {request.user.username} on question {question_id}"
        )
    """
    """ FIX FLAW 2: Add the return line below
        return HttpResponseForbidden("You are not allowed to delete this question.")
    """
    question.delete()

    """ FIX FLAW 5: Add the logging line below 
    logger.info(
        f"Poll {question_id} deleted by user {request.user}"
    )
    """

    return HttpResponseRedirect(reverse('polls:index'))
