
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

from .models import (
    Course, Lesson, Enrollment, Question, Choice, Submission
)


def index(request):
    course_list = Course.objects.all()
    return render(
        request,
        "onlinecourse/course_list_bootstrap.html",
        {"course_list": course_list},
    )


def login_request(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("onlinecourse:index")

        return render(
            request,
            "onlinecourse/login.html",
            {"message": "Invalid username or password"},
        )

    return render(request, "onlinecourse/login.html")


def logout_request(request):
    logout(request)
    return redirect("onlinecourse:index")


@login_required
def enroll(request, course_id):
    course = get_object_or_404(Course, pk=course_id)

    Enrollment.objects.get_or_create(
        user=request.user,
        course=course,
    )

    return HttpResponseRedirect(
        reverse("onlinecourse:course_details", args=(course.id,))
    )


@login_required
def course_details(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    lessons = Lesson.objects.filter(course=course)
    questions = Question.objects.filter(lesson__course=course)
    enrollment = Enrollment.objects.filter(
        user=request.user, course=course
    ).first()

    context = {
        "course": course,
        "lesson_list": lessons,
        "question_list": questions,
        "enrollment": enrollment,
    }

    return render(
        request,
        "onlinecourse/course_details_bootstrap.html",
        context,
    )


@login_required
def submit(request, course_id):
    if request.method != "POST":
        return HttpResponseRedirect(
            reverse("onlinecourse:course_details", args=(course_id,))
        )

    course = get_object_or_404(Course, pk=course_id)
    enrollment = get_object_or_404(
        Enrollment, user=request.user, course=course
    )

    submission = Submission.objects.create(enrollment=enrollment)

    for key, values in request.POST.lists():
        if key.startswith("choice"):
            for choice_id in values:
                choice = get_object_or_404(Choice, pk=choice_id)
                if choice.question.lesson.course_id == course.id:
                    submission.choices.add(choice)

    return HttpResponseRedirect(
        reverse(
            "onlinecourse:show_exam_result",
            args=(course.id, submission.id),
        )
    )


@login_required
def show_exam_result(request, course_id, submission_id):
    course = get_object_or_404(Course, pk=course_id)
    submission = get_object_or_404(
        Submission,
        pk=submission_id,
        enrollment__user=request.user,
        enrollment__course=course,
    )

    questions = Question.objects.filter(lesson__course=course)
    selected_choices = submission.choices.all()

    context = {
        "submission": submission,
        "course": course,
        "question_list": questions,
        "choices": selected_choices,
        "total_questions": submission.get_total_questions(),
        "correct_answers": submission.get_correct_answers(),
        "score": submission.get_score(),
    }

    return render(
        request,
        "onlinecourse/exam_result_bootstrap.html",
        context,
    )
