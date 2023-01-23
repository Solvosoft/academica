# encoding: utf-8
import json
import uuid
from decimal import Decimal
from json import JSONDecodeError

from django.db import models
from django.contrib.auth.models import User, Group as AuthGroup
from django.db.models import Q
from django.utils.encoding import smart_text
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.utils.timezone import now
from django.utils.html import strip_tags

from membership_core.models import Country, SystemCurrency


class Student(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, primary_key=True, verbose_name="Usuarie *")
    organization = models.CharField(verbose_name="Organización * ", max_length=150)
    country = models.ForeignKey(Country, on_delete=models.CASCADE, default=50)
    city = models.CharField(_("City"), max_length=100, default="")
    phone_number = models.CharField("Número de teléfono * ", max_length=15, default="")
    key = models.UUIDField(default=uuid.uuid4)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    expired_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    def confirm(self, key):
        if (str(self.key) == key):
            self.user.is_active = True
            self.user.save()
            self.confirmed_at = now()
            self.save()
            return True
        return False

    def __str__(self):
        dev = self.user.username
        if self.user.get_full_name():
            dev = self.user.get_full_name()
        return dev

    @property
    def organizations(self):
        dev = []
        try:
            if self.organization != "":
                dev = json.loads(self.organization)
        except JSONDecodeError as e:
            pass
        return dev

    class Meta:
        verbose_name = _("Student")
        verbose_name_plural = _("Students")
        ordering = ['user__last_name']
        permissions = [
            ("can_recovery_pass_student", "Can recovery pass student"),
        ]


class Professor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    email = models.EmailField(blank=True, verbose_name=_("Email for students"))
    description = models.TextField(max_length=2000, null=True, blank=True, verbose_name=_("Description"))
    photo = models.FileField(upload_to="photo_profile/", null=True, blank=True, verbose_name="Foto de perfil")
    active = models.BooleanField(default=True, verbose_name="Activa")

    def __str__(self):
        dev = self.user.username
        if self.user.get_full_name():
            dev = self.user.get_full_name()
        return dev

    class Meta:
        verbose_name = _("Professor")
        verbose_name_plural = _("Professors")
        permissions = [
            ("change_profile", "Can change_profile"),
            ("view_reports", "Can view_reports")
        ]
        ordering = ['user__last_name', 'active']
    
    @property
    def get_description(self):
        dev = self.description
        dev = dev if dev is not None else "No ha sido actualizada"
        return dev


class Period(models.Model):
    name = models.CharField(max_length=50, verbose_name=_("Name")+" * ")
    start_date = models.DateField(verbose_name=_("Period start date")+" * ")
    finish_date = models.DateField(verbose_name=_("Period finish date")+" * ")

    def __str__(self):
        return self.name + ' ({} - {})'.format(self.start_date, self.finish_date)

    class Meta:
        verbose_name = _("Period")
        verbose_name_plural = _("Periods")
        ordering = ['finish_date']


class Category(models.Model):
    name = models.CharField(max_length=300, unique=True, verbose_name=_("Name")+" * ")
    description = models.TextField(verbose_name=_("Description")+ " * ")
    image = models.FileField(upload_to="categories/", verbose_name=_("Image"), blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")
        ordering = ['name']


class Course(models.Model):
    category = models.ForeignKey(
        Category, verbose_name=_("Category")+" * ", on_delete=models.CASCADE)
    name = models.CharField(max_length=300, verbose_name=_("Name")+ " * ")
    content = models.TextField(verbose_name=_("Content")+" * ")
    workload = models.IntegerField(help_text="En horas", verbose_name="Carga horaria", default=20)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Course")
        verbose_name_plural = _("Courses")
        permissions = [
            ("can_add_group_course", "Can add course to group"),
        ]
        ordering = ['name']


class Group(models.Model):
    NORMAL = 0
    AUTO_PREENROLL = 1
    AUTO_ENROLL = 2

    COURRENCY_CHOICES = (
        ("USD", "Dolar"),
        ("EUR", "Euro"),
        ("CRC", "Colon Costa Rica"),
    )

    FLOWS = (
        (NORMAL, _('Normal flow (manual enroll activate)')),
        (
            AUTO_PREENROLL,
            _("Auto pre-enroll (automatic enroll activate)")
        ),
        (
            AUTO_ENROLL, _("Auto enroll (automatic enroll finished)")
        ),
    )

    period = models.ForeignKey(
        Period, verbose_name="Periodo * ", on_delete=models.CASCADE)
    course = models.ForeignKey(
        Course, verbose_name=_("Course")+" * ", on_delete=models.CASCADE)
    name = models.CharField(max_length=50, verbose_name=_("Name")+" * ")
    schedule = models.CharField(max_length=300, verbose_name=_("Schedule"))
    pre_enroll_start = models.DateTimeField(
        verbose_name=_("Pre enroll start hour")+" * ")
    pre_enroll_finish = models.DateTimeField(
        verbose_name=_("Pre enroll finish hour")+" * ")
    enroll_start = models.DateTimeField(verbose_name=_("Enroll start hour")+" * ")
    enroll_finish = models.DateTimeField(verbose_name=_("Enroll finish hour")+" * ")
    is_paid = models.BooleanField(verbose_name="Es pagado * ", default=True)
    notified_close = models.BooleanField(verbose_name=_("Was nofified as closed"), default=False)
    notified_open = models.BooleanField(verbose_name=_("Was nofified as opened"), default=False)
    currency = models.ForeignKey(
        SystemCurrency, verbose_name=_("Currency")+" * ", on_delete=models.CASCADE,
        blank=True, null=True)
    cost = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name=_("Course cost")+ " * ")
    maximum = models.SmallIntegerField(
        verbose_name=_("Maximum number of students")+ " * ")
    is_open = models.BooleanField(
        default=True, verbose_name="¿Está abierto? * ")
    flow = models.SmallIntegerField(choices=FLOWS, default=NORMAL, verbose_name=_("Enrollment behavior")+" * ")
    professors = models.ManyToManyField(Professor, blank=True, verbose_name=_("Professors"))
    duration_hours = models.IntegerField(_("Duración en horas"), default=20)
    expedition_date = models.DateField(_("Certificate expedition date"), blank=True, null=True)
    featured = models.BooleanField(default=False, verbose_name='Mostrar en destacados')
    featured_image = models.ImageField(upload_to='feautures/', verbose_name="Imágen destacada",
                                       null=True, blank=True, help_text='Imagen de 1200x900')

    @property
    def in_preenrollment(self):
        return timezone.localtime(self.pre_enroll_start) <= timezone.localtime() <= timezone.localtime(
            self.pre_enroll_finish)

    @property
    def in_enrollment(self):
        return timezone.localtime(self.enroll_start) <= timezone.localtime() <= timezone.localtime(self.enroll_finish)

    @property
    def get_enrolls_completed(self):
        return self.enroll_set.filter(enroll_finished=True).count()

    @property
    def approved_enrrolls(self):
        return self.enroll_set.filter(enroll_finished=True,
                                      course_status="approved").count()

    @property
    def reproved_enrrolls(self):
        return self.enroll_set.filter(enroll_finished=True,
                                      course_status="reproved").count()

    @property
    def uncompleted_enrrolls(self):
        return self.enroll_set.filter(enroll_finished=True,
                                      course_status="uncompleted").count()

    @property
    def get_label_enrolls(self):
        enrolls = self.get_enrolls_completed
        dev = f'{enrolls} de {self.maximum}'
        if enrolls > self.maximum:
            dev = f'{enrolls} de {enrolls}'
        return dev

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Group")
        verbose_name_plural = _("Groups")
        permissions = [
            ("can_view_pre_enroll_group", "Can view pre-enrolled in group"),
            ("can_export_enrolled_group", "Can export students group"),
            ("can_list_students_group", "Can list students group"),
            ("can_open_group", "Can open group"),
            ("can_close_group", "Can close group"),
            ("can_view_pdf_enrolled_group", "Can view enrolled to group"),
        ]
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.is_paid:
            self.cost = 0
        super().save(*args, **kwargs)


class Enroll(models.Model):
    COURSE_STATUS = (("approved", _("Approved")),
                     ("reproved", _("Reproved")),
                     ('uncompleted', _("Not complete the course")),
                     ('never_attend', _("Without lessons attended"))
                     )

    enroll_finished = models.BooleanField(
        default=False, verbose_name=_("Is enroll finished?"))
    enroll_activate = models.BooleanField(
        default=False, verbose_name=_("Is active for enroll?"))
    paid_excluded = models.BooleanField(_("Full scholaship"), default=False)
    rejected = models.BooleanField(
        default=False, verbose_name=_("Enroll rejected?"))
    group = models.ForeignKey(
        Group, verbose_name=_("Group"), on_delete=models.CASCADE)
    student = models.ForeignKey(
        Student, verbose_name=_("Student"), on_delete=models.CASCADE)
    enroll_date = models.DateTimeField(
        auto_now_add=True, verbose_name=_("Enroll date"))
    # bill field is needed to bill system
    bill_created = models.BooleanField(
        default=False, verbose_name=_("Bill created"))
    course_status = models.CharField(max_length=20, choices=COURSE_STATUS, blank=True, null=True,
                                     verbose_name=_("Status"))
    pdf_certificate = models.FileField(upload_to="certificates/", null=True, blank=True, verbose_name=_("Certificate"))
    go_to_one_class = models.BooleanField(default=True, verbose_name=_('Go to classes'))

    def __str__(self):
        return self.student.user.username + " -- " + smart_text(self.group)

    @property
    def is_penalized(self):
        """
        enroll__go_to_one_class=False

        """

        periods = list(Period.objects.all().order_by('finish_date').values_list('pk', flat=True))[-2:]
        queryset = self.__class__.objects.filter(student=self.student).exclude(pk=self.pk)
        queryset= queryset.filter(group__period__in=periods)
        queryset=queryset.filter(
            Q(course_status__in=['uncompleted', 'never_attend'])|Q(go_to_one_class=False)
        )

        return queryset.exists()

    class Meta:
        verbose_name = _("Enrollment")
        verbose_name_plural = _("Enrollments")
        permissions = [
            ("can_view_qualifications", "Can view qualifications"),
            ("can_qualify_students", "Can qualify students"),
        ]
        ordering = ['group']

    @property
    def get_status(self):
        dev = _("Not qualified")
        if self.course_status != None:
            dev = "Aprobada"
            if self.course_status == 'reproved':
                dev = "Reprobada"
            if self.course_status == 'uncompleted':
                dev = "Desertada"
            if self.course_status == 'never_attend':
                dev = "Nunca asistió"
        return dev

    @property
    def get_paid_excluded(self):
        dev = _("No")
        if self.paid_excluded:
            dev = _("Yes")
        return dev
    
    @property
    def get_rejected(self):
        dev = _("No")
        if self.rejected:
            dev = _("Yes")
        return dev
    
    @property
    def get_paid(self):
        dev = _("No")
        bill = self.bill_set.first()
        if bill and bill.is_paid:
            dev = _("Yes")
        return dev


class WaitingList(models.Model):
    group = models.ForeignKey(
        Group, on_delete=models.CASCADE, verbose_name=_("Group"))
    student = models.ForeignKey(
        Student, on_delete=models.CASCADE, verbose_name=_("Student"))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.group) + " " + str(self.student)

    class Meta:
        verbose_name = _("Waiting list")
        verbose_name_plural = _("Waiting lists")
        ordering = ['group', 'created_at']


class MenuItem(models.Model):
    TYPES = (
        (0, _("Internal")),
        (1, _("Page")),
        (2, "No utilizar"))
    name = models.CharField(max_length=50, verbose_name="Nombre")
    type = models.SmallIntegerField(
        choices=TYPES, default=0, verbose_name=_("Type"))
    description = models.CharField(
        max_length=50, verbose_name=_("Description"))
    require_authentication = models.BooleanField(
        default=False, verbose_name=_("Authentication is required"))
    order = models.SmallIntegerField(verbose_name=_("Menu order"))
    parent = models.ForeignKey(
        'self', null=True, blank=True, verbose_name=_("Page parent"),
        on_delete=models.CASCADE)
    publicated = models.BooleanField(
        default=True, verbose_name=_("Publicated"))
    is_index = models.BooleanField(default=False, verbose_name=_("Index page"))

    def get_title_menu(self, request):
        return self.description

    def __str__(self):
        return strip_tags(self.description)

    class Meta:
        verbose_name = _("Menu Item")
        verbose_name_plural = _("Menu Items")
        ordering = ['name']


class Page(models.Model):
    slug = models.SlugField("Slug * ")
    title = models.CharField(
        max_length=300, null=True, blank=True, verbose_name="Título")
    content = models.TextField(verbose_name=_("Content"))

    def __str__(self):
        return self.slug

    class Meta:
        verbose_name = _("Page")
        verbose_name_plural = _("Pages")
        ordering = ['title']


class Coupon(models.Model):
    DISCOUNT_CHOICES = (
        (50, "50"),
        (100, "100")
    )

    student = models.ForeignKey(Student, verbose_name=_("Student"), on_delete=models.CASCADE)
    group = models.ForeignKey(Group, verbose_name=_("Group"), on_delete=models.CASCADE, null=True, blank=False)
    discount_percentage = models.IntegerField(null=True, blank=True, choices=DISCOUNT_CHOICES,
                                              default=DISCOUNT_CHOICES[1])
    is_used = models.BooleanField(default=False, verbose_name=_("Is used?"))
    code = models.CharField(max_length=15, null=True, blank=True, unique=True, verbose_name=_("Discount code"))
    bill = models.ForeignKey("bills.Bill", verbose_name=("Bill"), null=True, blank=True, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.student} - {self.group.name} - {self.code[2:6]}"

    class Meta:
        verbose_name = _("Coupon")
        verbose_name_plural = _("Coupons")
        ordering = ['group', 'student__user__last_name']

    @classmethod
    def from_db(cls, db, field_names, values):
        instance = super().from_db(db, field_names, values)
        instance._state.adding = False
        instance._state.db = db
        instance._old_values = dict(zip(field_names, values))
        return instance

    def data_changed(self, fields):
        """
        example:
        if self.data_changed(['student', 'course', 'discount_percentage', 'is_used', 'code', 'bill']):
            print("one of the fields changed")
            
        returns true if the model saved the first time and _old_values doesnt exist
       
        :param fields:
        :return:
        """
        if hasattr(self, '_old_values'):
            if not self.pk or not self._old_values:
                return True

            for field in fields:
                if getattr(self, field) != self._old_values[field]:
                    return True
            return False
        return True


class FakeGroup(models.Model):
    name = models.CharField(_('Name'), max_length=200)
    group = models.OneToOneField(AuthGroup, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = _("Fake Group")
        verbose_name_plural = _("Fake Groups")
        ordering = ['name']
