"""Django models: Lecture, Exercise, Choice, Log and UserLecture"""
from django.db import models
from django.contrib.auth.models import User

class Lecture(models.Model):
    title = models.CharField(max_length=200)
    language = models.CharField(max_length=10)
    version = models.CharField(max_length=10)
    # The fractional counts are used for ordering within one int level
    level = models.DecimalField(max_digits=3, decimal_places=2, null=True)
    outside_info_name = models.CharField(max_length=200)
    outside_info_link = models.CharField(max_length=200)
    instructions = models.CharField(max_length=8000)

    def __unicode__(self):
        return "%s, version %s" % (self.title, self.version)

class Exercise(models.Model):
    lecture = models.ForeignKey(Lecture, on_delete=models.CASCADE)
    language = models.CharField(max_length=10)
    title = models.CharField(max_length=200)
    text = models.CharField(max_length=200)
    question_type = models.CharField(max_length=10)
    question_image = models.CharField(max_length=200)
    question_mp3 = models.CharField(max_length=200)
    question_ogg = models.CharField(max_length=200)

    def __unicode__(self):
        return self.question_mp3

class Choice(models.Model):
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    answer_type = models.CharField(max_length=10)
    correct = models.BooleanField()
    image = models.CharField(max_length=200)
    mp3 = models.CharField(max_length=200)
    ogg = models.CharField(max_length=200)
    text = models.CharField(max_length=200)

    def __unicode__(self):
        return """Choice
correct: %s,
image: %s,
mp3: %s,
ogg:%s""" %(repr(self.correct), self.image, self.mp3, self.ogg)

class Log(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    time = models.DateTimeField(auto_now=True)
    entry = models.CharField(max_length=200)

    def __unicode__(self):
        return "%s %s: %s" %(user, time, entry)

class UserLecture(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    lecture_name = models.CharField(max_length=200)
    lecture_version = models.CharField(max_length=10)
    num_questions = models.PositiveSmallIntegerField()
    score = models.PositiveSmallIntegerField()
    completed_date = models.DateTimeField(auto_now=True)
    completed = models.BooleanField()


    def __unicode__(self):
        return "%s %s (v. %s): %d/%d at %s" %(
            self.user, self.lecture_name, self.lecture_version,
            self.score, self.num_questions, self.completed_date.isoformat())
