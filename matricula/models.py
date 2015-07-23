# encoding: utf-8
from django.db import models

# Create your models here.


from django.contrib.auth.models import AbstractUser
from simple_email_confirmation import SimpleEmailConfirmationUserMixin
from ckeditor.fields import RichTextField
from django.utils.encoding import python_2_unicode_compatible, smart_text
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _



class Student(SimpleEmailConfirmationUserMixin, AbstractUser):
    pass

@python_2_unicode_compatible
class Period(models.Model):
    name = models.CharField(max_length=50, verbose_name=_("Name"))
    start_date = models.DateField(verbose_name=_("Period start date"))
    finish_date = models.DateField(verbose_name=_("Period finish date"))

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Period")
        verbose_name_plural = _("Periods")


@python_2_unicode_compatible
class Category(models.Model):
    name = models.CharField(max_length=300, verbose_name=_("Name"))
    description = RichTextField(verbose_name=_("Description"))

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")

@python_2_unicode_compatible
class Course(models.Model):
    category = models.ForeignKey(Category, verbose_name=_("Category"))
    name = models.CharField(max_length=300, verbose_name=_("Name"))
    content = RichTextField(verbose_name=_("Content"))

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Course")
        verbose_name_plural = _("Courses")

@python_2_unicode_compatible
class Group(models.Model):

    COURRENCY_CHOICES = (
            ("USD", "US Dollar"),
            ("EUR", "Euro"),
            ("CRC", "Costa Rican Colon"),
                         )

    period = models.ForeignKey(Period, verbose_name=_("Period"))
    course = models.ForeignKey(Course, verbose_name=_("Course"))
    name = models.CharField(max_length=50, verbose_name=_("Name"))
    schedule = models.CharField(max_length=300, verbose_name=_("Schedule"))

    pre_enroll_start = models.DateTimeField(verbose_name=_("Pre enroll start hour"))
    pre_enroll_finish = models.DateTimeField(verbose_name=_("Pre enroll finish hour"))

    enroll_start = models.DateTimeField(verbose_name=_("Enroll start hour"))
    enroll_finish = models.DateTimeField(verbose_name=_("Enroll finish hour"))
    currency = models.CharField(max_length=3, verbose_name=_("Currency"), choices=COURRENCY_CHOICES, default="CRC")
    cost = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("Course cost"))
    maximum = models.SmallIntegerField(verbose_name=_("Maximum number of students"))
    is_open = models.BooleanField(default=True)

    @property
    def in_enrollment(self):
        if self.pre_enroll_start <= timezone.now() <= self.pre_enroll_finish:
            return True
        return False

    def __str__(self):
        return smart_text(self.course) + " -- " + self.name

    class Meta:
        verbose_name = _("Group")
        verbose_name_plural = _("Groups")


@python_2_unicode_compatible
class Enroll(models.Model):
    enroll_finished = models.BooleanField(default=False, verbose_name=_("Is enroll finished?"))
    enroll_activate = models.BooleanField(default=False, verbose_name=_("Is active for enroll?"))
    group = models.ForeignKey(Group, verbose_name=_("Group"))
    student = models.ForeignKey(Student, verbose_name=_("Student"))
    enroll_date = models.DateTimeField(auto_now_add=True, verbose_name=_("Enroll date"))
    bill_created = models.BooleanField(default=False, verbose_name=_("Bill created"))  # is needed by bill sistem 

    def __str__(self):
        return self.student.username + " -- " + smart_text(self.group)

    class Meta:
        verbose_name = _("Enrollment")
        verbose_name_plural = _("Enrollments")

