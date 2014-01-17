from django.db import models
from django.contrib.auth.models import User

class Lecture(models.Model):
  title = models.CharField(max_length=200)
  version = models.CharField(max_length=10)
  outside_info_name = models.CharField(max_length=200)
  outside_info_link = models.CharField(max_length=200)

  def __unicode__(self):
    return "%s, version %s" % (self.title, self.version)
    
class Exercise(models.Model):
  lecture = models.ForeignKey(Lecture)
  title = models.CharField(max_length=200)
  question_type = models.CharField(max_length=10)
  question_image = models.CharField(max_length=200)
  question_mp3 = models.CharField(max_length=200)
  question_ogg = models.CharField(max_length=200)

  def __unicode__(self):
    return self.question_mp3

class Choice(models.Model):
  exercise = models.ForeignKey(Exercise)
  answer_type = models.CharField(max_length=10)  
  correct = models.BooleanField()
  image = models.CharField(max_length=200)
  mp3 = models.CharField(max_length=200)
  ogg = models.CharField(max_length=200)

  def __unicode__(self):
    return """Choice
correct: %s,
image: %s,
mp3: %s,
ogg:%s""" %( repr(self.correct), self.image, self.mp3, self.ogg)

class Log(models.Model):
  user = models.ForeignKey(User)
  time = models.DateTimeField(auto_now=True)
  entry = models.CharField(max_length=200)

  def __unicode__(self):
    return "%s %s: %s" %(user, time, entry)
  
class UserLecture(models.Model):
  user = models.ForeignKey(User)
  lecture_name = models.CharField(max_length=200)
  lecture_version = models.CharField(max_length=10)
  num_questions = models.PositiveSmallIntegerField()
  score = models.PositiveSmallIntegerField()
  completed_date = models.DateTimeField(auto_now=True)
  completed = models.BooleanField()


  def __unicode__(self):
    return "%s %s (v. %s): %d/%d at %s" %( self.user, self.lecture_name, self.lecture_version,
                                          self.score, self.num_questions, self.completed_date.isoformat())
