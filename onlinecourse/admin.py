
from django.contrib import admin
from .models import (
    Instructor,
    Learner,
    Course,
    Lesson,
    Enrollment,
    Question,
    Choice,
    Submission,
)


class LessonInline(admin.StackedInline):
    model = Lesson
    extra = 1


class ChoiceInline(admin.StackedInline):
    model = Choice
    extra = 1


class CourseAdmin(admin.ModelAdmin):
    list_display = ("name", "description", "total_enrollment")
    search_fields = ("name", "description")
    inlines = [LessonInline]


class LessonAdmin(admin.ModelAdmin):
    list_display = ("title", "course", "order")
    list_filter = ("course",)
    search_fields = ("title",)


class QuestionAdmin(admin.ModelAdmin):
    list_display = ("question_text", "lesson", "grade")
    list_filter = ("lesson",)
    search_fields = ("question_text",)
    inlines = [ChoiceInline]


class SubmissionAdmin(admin.ModelAdmin):
    list_display = ("id", "enrollment", "submission_time")
    list_filter = ("submission_time",)
    search_fields = ("enrollment__user__username",)


admin.site.register(Instructor)
admin.site.register(Learner)
admin.site.register(Course, CourseAdmin)
admin.site.register(Lesson, LessonAdmin)
admin.site.register(Enrollment)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Choice)
admin.site.register(Submission, SubmissionAdmin)
