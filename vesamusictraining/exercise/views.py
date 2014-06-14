import datetime
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
import json
import random
import sys # debug

from vesamusictraining.exercise.models import Lecture, UserLecture, Log

@login_required
def choose_lecture(request):
    """Render the chooser page."""
    complete_info = dict([
        (ue.lecture_name, ue)\
          for ue in UserLecture.objects.filter(user=request.user)])

    lectures = Lecture.objects.filter(language=request.LANGUAGE_CODE)
    for l in lectures:
        l.num_exercises = l.exercise_set.count()
        if l.title in complete_info:
            ue = complete_info[l.title]
            l.completed = ue.completed
            if ue.completed:
                l.complete_date = ue.completed_date.ctime()
                l.correct = ue.score
                l.total_responses = ue.num_questions
                l.completed_version = ue.lecture_version
        else:
            l.completed = False

    return render(
        request, "choose_lecture.html",
        {"lectures": lectures}
        )

@login_required
def show_lecture(request, lecture_name):
    """Render one lecture."""
    l = Lecture.objects.get(title=lecture_name)

    return render(request, "show_lecture.html",
                  {"lecture_name": l.title,
                   "num_exercises": l.exercise_set.count()
                   })

@login_required
def show_results(request, lecture_name):
    """Show results on completion."""
    ue = UserLecture.objects.get(user=request.user, lecture_name=lecture_name)

    return render(request, "show_results.html",
                  {"userlecture": ue})

@login_required
def get_question(request, lecture_name):
    """Return JSON question info."""
    if request.method == 'GET':
        l = Lecture.objects.get(title=lecture_name)
        first_exercise_idx = l.exercise_set.order_by("pk")[0].pk

        # Ugly kludge
        ei = int(request.GET["exercise_index"]) \
          if "exercise_index" in request.GET else 0
        ei = ei + first_exercise_idx

        if ei >= l.exercise_set.count() + first_exercise_idx: # FIXME: debug
            sys.stderr.write("Quick out\n")
            return HttpResponse(content=json.dumps(""))
        e = l.exercise_set.get(pk=ei)
        if ei == first_exercise_idx:
            try:
                ue = UserLecture.objects.get(
                    user=request.user, lecture_name=l.title)
            except UserLecture.DoesNotExist:
                ue = UserLecture(user=request.user, lecture_name=l.title)

            ue.score = 0
            ue.completed_date = None
            ue.completed = False
            ue.lecture_version = l.version
            ue.num_questions = l.exercise_set.count()
            ue.save()

        res_message = {
          "name" : e.title.capitalize(),
          "question_type" : e.question_type,
        }

        res_message["text"] = e.text
        if e.question_type == "audio":
            res_message["question_ogg"] = e.question_ogg
            res_message["question_mp3"] = e.question_mp3
        else:
            res_message["question_image"] = e.question_image

        choices = [r for r in e.choice_set.all()]
        random.shuffle(choices)
        res_message["num_alt"] = len(choices)
        for i, a in enumerate(choices):
            res_message["alt%d_text" %i] = a.text
            if a.answer_type == "image":
                res_message["alt%d_image" %i] = a.image
            else:
                res_message["alt%d_ogg" % i] = a.ogg
                res_message["alt%d_mp3" % i] = a.mp3

        return HttpResponse(content=json.dumps(res_message))

@login_required
def verify(request, lecture_name):
    """Check, if the answer was correct"""
    if request.method == 'GET':
        l = Lecture.objects.get(title=lecture_name)
        ei = int(request.GET["exercise_index"]) + \
          l.exercise_set.order_by("pk")[0].pk
        e = l.exercise_set.get(pk=ei)
        try:
            if e.question_type == "audio":
                alt = e.choice_set.get(image=request.GET["chosen"])
            else:
                alt = e.choice_set.get(ogg=request.GET["chosen"])
        except KeyError:
            alt = None

        correct = alt.correct if alt else False
        log = Log(user=request.user, entry="Lecture %s, Exercise %d: %s" % (
            l.title, e.pk, repr(correct)))
        log.save()

        res_message = {
          "correct": correct,
          "image": alt.image if alt else None,
          "mp3": alt.mp3 if alt else None,
          "ogg": alt.ogg if alt else None
          }

        return HttpResponse(content=json.dumps(res_message))


@login_required
def complete_lecture(request, lecture_name):
    """Write lecture completion info to db."""
    ue = UserLecture.objects.get(user=request.user, lecture_name=lecture_name)
    ue.score = request.GET["num_correct"]
    ue.completed_date = datetime.datetime.now()
    ue.completed = True
    ue.save()
    return HttpResponse("ok")
