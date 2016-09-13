# encoding: utf-8
from django.db import models
from django.contrib.auth.models import AbstractUser
from simple_email_confirmation.models import SimpleEmailConfirmationUserMixin
from ckeditor.fields import RichTextField
from django.utils.encoding import python_2_unicode_compatible, smart_text
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator


class Hour(models.Model):
    day_position = models.SmallIntegerField(
        validators=[
            MaxValueValidator(168),
            MinValueValidator(0),
        ]
    )
    description = models.TextField()
    active = models.BooleanField(default=True)

    def __str__(self):
        return str(self.day_position)


class Week(models.Model):
    hours = models.ManyToManyField(Hour)


class Student(SimpleEmailConfirmationUserMixin, AbstractUser):
    pass


@python_2_unicode_compatible
class Period(models.Model):
    name = models.CharField(max_length=50, verbose_name=_("Name"))
    start_date = models.DateField(verbose_name=_("Period start date"))
    finish_date = models.DateField(verbose_name=_("Period finish date"))
    active = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Period")
        verbose_name_plural = _("Periods")


@python_2_unicode_compatible
class ClassroomType(models.Model):
    name = models.CharField(max_length=30, verbose_name=_("Name"))
    description = models.CharField(max_length=150,
                                   verbose_name=_("Description"))

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Classroom Type")
        verbose_name_plural = _("Classroom Types")


@python_2_unicode_compatible
class Classroom(models.Model):

    SELECTION_TYPES = (
        (5, _('High priority')),
        (4, _('Priority')),
        (3, _('Normal')),
        (2, _('Low priority')),
        (1, _('Last assigned')),
    )

    name = models.CharField(max_length=30, verbose_name=_("Name"))
    capacity = models.IntegerField(verbose_name=_("Capacity"))
    classroom_type = models.ForeignKey(ClassroomType,
                                       verbose_name=_("Classroom type"))
    selection_score = models.IntegerField(choices=SELECTION_TYPES,
                                          verbose_name=_("Selection priority"))

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Classroom")
        verbose_name_plural = _("Classrooms")


class ClassroomSchedule(models.Model):
    period = models.ForeignKey(Period)
    classroom = models.ForeignKey(Classroom)
    schedule = models.ForeignKey(Week, null=True)


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
class Profesor(models.Model):
    # tiene identificacion, nombre, email
    user = models.OneToOneField(settings.AUTH_USER_MODEL,
                                verbose_name=_("User"))
    number_hours = models.SmallIntegerField(
        verbose_name=_("Number of work hours"))

    def __str__(self):
        return self.user.get_full_name()

    class Meta:
        verbose_name = _("Profesor")
        verbose_name_plural = _("Profesors")


@python_2_unicode_compatible
class ProfesorSchedule(models.Model):
    period = models.ForeignKey(Period)
    profesor = models.ForeignKey(Profesor)
    schedule = models.ForeignKey(Week, null=True)

    def __str__(self):
        return str(self.period) + " | " + str(self.profesor)


@python_2_unicode_compatible
class Course(models.Model):
    category = models.ForeignKey(Category, verbose_name=_("Category"))
    required_courses = models.ManyToManyField("self", blank=True,
                                              verbose_name=_("Required courses"))
    name = models.CharField(max_length=300, verbose_name=_("Name"))
    content = RichTextField(verbose_name=_("Content"))

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Course")
        verbose_name_plural = _("Courses")


@python_2_unicode_compatible
class Group(models.Model):

    NORMAL = 0
    AUTO_PREENROLL = 1
    AUTO_ENROLL = 2

    COURRENCY_CHOICES = (
        ("USD", "US Dollar"),
        ("EUR", "Euro"),
        ("CRC", "Costa Rican Colon"),
    )

    FLOWS = (
        (NORMAL, _('Normal flow (manual enroll activate)')),
        (AUTO_PREENROLL,
         _("Auto pre-enroll (automatic enroll activate)")),
        (AUTO_ENROLL, _("Auto enroll (automatic enroll finished)")),
    )
    period = models.ForeignKey(Period, verbose_name=_("Period"))
    course = models.ForeignKey(Course, verbose_name=_("Course"))
    name = models.CharField(max_length=50, verbose_name=_("Name"))
    schedule = models.ForeignKey(Week, null=True, blank=True)
    # FIXME cambiar null=False
    classroom_type = models.ForeignKey(
        ClassroomType, null=True, verbose_name=_("Classroom type"))
    number_hours = models.IntegerField(default=1,
                                       validators=[
                                           MaxValueValidator(168),
                                           MinValueValidator(1)
                                       ],
                                       verbose_name=_("Number of lesson hours"))
    number_days = models.SmallIntegerField(default=1,
                                           validators=[
                                               MaxValueValidator(7),
                                               MinValueValidator(1)
                                           ],
                                           verbose_name=_(
                                               "Number of imparting days")
                                           )

    pre_enroll_start = models.DateTimeField(
        verbose_name=_("Pre enroll start hour"))
    pre_enroll_finish = models.DateTimeField(
        verbose_name=_("Pre enroll finish hour"))

    enroll_start = models.DateTimeField(verbose_name=_("Enroll start hour"))
    enroll_finish = models.DateTimeField(verbose_name=_("Enroll finish hour"))
    currency = models.CharField(max_length=3, verbose_name=_("Currency"),
                                choices=COURRENCY_CHOICES, default="CRC")
    cost = models.DecimalField(max_digits=10, decimal_places=2,
                               verbose_name=_("Course cost"))
    maximum = models.SmallIntegerField(
        verbose_name=_("Maximum number of students"))
    is_open = models.BooleanField(default=True)
    flow = models.SmallIntegerField(choices=FLOWS, default=NORMAL,
                                    verbose_name=_("Enrollment behavior"))

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
class ClassroomGroupProfesor(models.Model):
    period = models.ForeignKey(Period, verbose_name=_("Period"))
    classroom = models.ForeignKey(Classroom, verbose_name=_("Classroom"))
    profesor = models.ForeignKey(Profesor, verbose_name=_("Profesor"))
    group = models.ForeignKey(Group, verbose_name=_("Group"))
    schedule = models.ForeignKey(Week, null=True, verbose_name=_("Schedule"))

    def __str__(self):
        return str(self.group) + str(self.profesor)

    class Meta:
        verbose_name = _("Asignation")
        verbose_name_plural = _("Asignations")


@python_2_unicode_compatible
class Enroll(models.Model):
    enroll_finished = models.BooleanField(default=False,
                                          verbose_name=_("Is enroll finished?"))
    enroll_activate = models.BooleanField(default=False,
                                          verbose_name=_("Is active for enroll?"))
    group = models.ForeignKey(Group, verbose_name=_("Group"))
    student = models.ForeignKey(Student, verbose_name=_("Student"))
    enroll_date = models.DateTimeField(auto_now_add=True,
                                       verbose_name=_("Enroll date"))
    bill_created = models.BooleanField(default=False,
                                       verbose_name=_("Bill created"))  # is needed by bill sistem

    def __str__(self):
        return self.student.username + " -- " + smart_text(self.group)

    class Meta:
        verbose_name = _("Enrollment")
        verbose_name_plural = _("Enrollments")


@python_2_unicode_compatible
class MenuItem(models.Model):
    TYPES = (
        (0, _("Internal")),
        (1, _("Page")),
        (2, _("Do not used "))
    )
    name = models.CharField(max_length=50, verbose_name=_("Name"))
    type = models.SmallIntegerField(choices=TYPES, default=0,
                                    verbose_name=_("Type"))
    description = models.CharField(max_length=50,
                                   verbose_name=_("Description"))
    require_authentication = models.BooleanField(default=False,
                                                 verbose_name=_("Authentication is required"))
    order = models.SmallIntegerField(verbose_name=_("Menu order"))
    parent = models.ForeignKey('self', null=True, blank=True,
                               verbose_name=_("Page parent"))
    publicated = models.BooleanField(default=True,
                                     verbose_name=_("Publicated"))
    is_index = models.BooleanField(default=False,
                                   verbose_name=_("Index page"))

    def get_title_menu(self, request):
        name = MenuTranslations.objects.filter(
            menu=self, language=request.LANGUAGE_CODE)
        if not name:
            name = MenuTranslations.objects.filter(
                menu=self, language=settings.LANGUAGE_CODE)

        if not name:
            name = self.description
        else:
            name = name[0].name

        return name

    def __str__(self):
        return self.description

    class Meta:
        verbose_name = _("Menu Item")
        verbose_name_plural = _("Menu Items")


@python_2_unicode_compatible
class MenuTranslations(models.Model):
    language = models.CharField(max_length=3,
                                choices=settings.LANGUAGES,
                                default=settings.LANGUAGE_CODE,
                                verbose_name=_("Language"))
    name = models.CharField(max_length=50, verbose_name=_("Description"))
    menu = models.ForeignKey(MenuItem, null=True)

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class Page(models.Model):
    slug = models.SlugField()

    def __str__(self):
        return self.slug

    class Meta:
        verbose_name = _("Page")
        verbose_name_plural = _("Pages")


@python_2_unicode_compatible
class MultilingualContent(models.Model):
    language = models.CharField(max_length=3,
                                choices=settings.LANGUAGES,
                                default=settings.LANGUAGE_CODE,
                                verbose_name=_("Language"))
    title = models.CharField(max_length=300, null=True, blank=True)
    content = RichTextField(verbose_name=_("Content"))
    page = models.ForeignKey(Page)

    def __str__(self):
        return self.language
