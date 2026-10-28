from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Course(models.Model):
    name = models.CharField(null=False, max_length=30, default='online course')
    description = models.CharField(null=False, max_length=255, default='online course description')

    def __str__(self):
        return "Name: " + self.name


class Lesson(models.Model):
    title = models.CharField(null=False, max_length=200, default='lesson')
    content = models.TextField(null=False, default='lesson content')
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    def __str__(self):
        return "Title: " + self.title


class Enrollment(models.Model):
    AUDIT = 'audit'
    HONOR = 'honor'
    BETA = 'beta'
    ENROLLMENT_CHOICES = [
        (AUDIT, 'Audit'),
        (HONOR, 'Honor'),
        (BETA, 'Beta'),
    ]

    enroll_user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    enroll_mode = models.CharField(max_length=5, choices=ENROLLMENT_CHOICES, default=AUDIT)
    enroll_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('enroll_user', 'course')

    def __str__(self):
        return "Enrollment: " + self.enroll_user.username + " - " + self.course.name


class Question(models.Model):
    question_text = models.CharField(null=False, max_length=200, default='question')
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)

    def __str__(self):
        return "Question: " + self.question_text

    def get_choices(self):
        return Choice.objects.filter(question=self)


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(null=False, max_length=200, default='choice')
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return "Choice: " + self.choice_text + " (Question: " + self.question.question_text + ")"


class Submission(models.Model):
    enroll = models.ForeignKey(Enrollment, on_delete=models.CASCADE)
    choices = models.ManyToManyField(Choice)
    submit_time = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return "Submission: " + str(self.pk)

    def get_total_questions(self):
        return Question.objects.filter(lesson__course=self.enroll.course).count()

    def get_correct_answers(self):
        return self.choices.filter(is_correct=True).count()

    def get_score(self):
        total_questions = self.get_total_questions()
        if total_questions == 0:
            return 0
        return int(self.get_correct_answers() * 100 / total_questions)
