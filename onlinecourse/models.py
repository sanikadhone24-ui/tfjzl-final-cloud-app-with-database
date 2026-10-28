
from django.conf import settings
from django.db import models
from django.utils.timezone import now


class Instructor(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    full_time = models.BooleanField(default=True)
    total_learners = models.IntegerField(default=0)

    def __str__(self):
        return self.user.username


class Learner(models.Model):
    STUDENT = "student"
    DEVELOPER = "developer"
    DATA_SCIENTIST = "data_scientist"
    DATABASE_ADMIN = "dba"

    OCCUPATION_CHOICES = [
        (STUDENT, "Student"),
        (DEVELOPER, "Developer"),
        (DATA_SCIENTIST, "Data Scientist"),
        (DATABASE_ADMIN, "Database Admin"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    occupation = models.CharField(
        max_length=20,
        choices=OCCUPATION_CHOICES,
        default=STUDENT
    )
    social_link = models.URLField(max_length=200, blank=True)

    def __str__(self):
        return f"{self.user.username},{self.occupation}"


class Course(models.Model):
    name = models.CharField(
        max_length=30,
        default="online course"
    )
    image = models.ImageField(
        upload_to="course_images/",
        blank=True,
        null=True
    )
    description = models.CharField(
        max_length=1000,
        blank=True
    )
    pub_date = models.DateField(
        null=True,
        blank=True
    )
    instructors = models.ManyToManyField(
        Instructor,
        blank=True
    )
    users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through="Enrollment",
        related_name="online_courses"
    )
    total_enrollment = models.IntegerField(default=0)

    def __str__(self):
        return f"Name: {self.name},Description: {self.description}"


class Lesson(models.Model):
    title = models.CharField(
        max_length=200,
        default="title"
    )
    order = models.IntegerField(default=0)
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE
    )
    content = models.TextField()

    def __str__(self):
        return self.title


class Enrollment(models.Model):
    AUDIT = "audit"
    HONOR = "honor"
    BETA = "BETA"

    COURSE_MODES = [
        (AUDIT, "Audit"),
        (HONOR, "Honor"),
        (BETA, "BETA"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE
    )
    date_enrolled = models.DateField(default=now)
    mode = models.CharField(
        max_length=5,
        choices=COURSE_MODES,
        default=AUDIT
    )
    rating = models.FloatField(default=5.0)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "course"],
                name="unique_user_course_enrollment"
            )
        ]

    def __str__(self):
        return f"{self.user.username} - {self.course.name}"


class Question(models.Model):
    question_text = models.CharField(
        max_length=200,
        default="question"
    )
    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE
    )
    grade = models.IntegerField(default=1)

    def __str__(self):
        return self.question_text

    def get_choices(self):
        return Choice.objects.filter(question=self)

    def is_get_score(self):
        return self.grade


class Choice(models.Model):
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE
    )
    choice_text = models.CharField(
        max_length=200,
        default="choice"
    )
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.choice_text


class Submission(models.Model):
    enrollment = models.ForeignKey(
        Enrollment,
        on_delete=models.CASCADE
    )
    choices = models.ManyToManyField(Choice)
    submission_time = models.DateTimeField(default=now)

    def __str__(self):
        return f"Submission {self.pk}"

    def get_score(self):
        questions = Question.objects.filter(
            lesson__course=self.enrollment.course
        )

        total_grade = sum(question.grade for question in questions)

        if total_grade == 0:
            return 0

        score = 0

        for question in questions:
            correct_ids = set(
                question.get_choices()
                .filter(is_correct=True)
                .values_list("id", flat=True)
            )

            selected_ids = set(
                self.choices
                .filter(question=question)
                .values_list("id", flat=True)
            )

            if correct_ids and correct_ids == selected_ids:
                score += question.grade

        return round((score / total_grade) * 100)

    def get_total_questions(self):
        return Question.objects.filter(
            lesson__course=self.enrollment.course
        ).count()

    def get_correct_answers(self):
        questions = Question.objects.filter(
            lesson__course=self.enrollment.course
        )

        correct_count = 0

        for question in questions:
            correct_ids = set(
                question.get_choices()
                .filter(is_correct=True)
                .values_list("id", flat=True)
            )

            selected_ids = set(
                self.choices
                .filter(question=question)
                .values_list("id", flat=True)
            )

            if correct_ids and correct_ids == selected_ids:
                correct_count += 1

        return correct_count
