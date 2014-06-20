"""Admin interface to models"""
from django.contrib import admin
from vesamusictraining.exercise.models import \
     Lecture, Log, UserLecture, Exercise, Choice

class ExerciseInline(admin.StackedInline):
    model = Exercise
    extra = 0

class LectureAdmin(admin.ModelAdmin):
    inlines = [ExerciseInline]

class ChoiceInline(admin.StackedInline):
    model = Choice
    extra = 0

class ExerciseAdmin(admin.ModelAdmin):
    list_display = ('title', 'question_type')
    inlines = [ChoiceInline]

admin.site.register(Lecture, LectureAdmin)
admin.site.register(Exercise)
admin.site.register(Choice)
admin.site.register(Log)
admin.site.register(UserLecture)
