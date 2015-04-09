from django.db import models

# Create your models here.


from django.contrib.auth.models import AbstractUser
from simple_email_confirmation import SimpleEmailConfirmationUserMixin
from ckeditor.fields import RichTextField
from django.utils.encoding import python_2_unicode_compatible
from django.utils import timezone

class Student(SimpleEmailConfirmationUserMixin, AbstractUser):
    pass


@python_2_unicode_compatible
class Course(models.Model):
    name = models.CharField(max_length=300)
    content = RichTextField()

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class Group(models.Model):
    course = models.ForeignKey(Course)
    name = models.CharField(max_length=50)
    schedule = models.CharField(max_length=300)

    pre_enroll_start = models.DateTimeField()
    pre_enroll_finish = models.DateTimeField()

    enroll_start = models.DateTimeField()
    enroll_finish = models.DateTimeField()

    @property
    def in_enrollment(self):
        print(self.name,
              self.pre_enroll_start , "(" , timezone.now(), ")" , self.pre_enroll_finish)
        if self.pre_enroll_start <= timezone.now() <= self.pre_enroll_finish:
            return True
        return False


    def __str__(self):
        return str(self.course) + " -- " + self.name


@python_2_unicode_compatible
class Enroll(models.Model):
    enroll_finished = models.BooleanField(default=False)
    enroll_activate = models.BooleanField(default=False)
    group = models.ForeignKey(Group)
    student = models.ForeignKey(Student)
    enroll_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.student.username + " -- " + str(self.group)
