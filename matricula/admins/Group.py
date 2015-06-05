'''
Created on 4/6/2015

@author: luisza
'''
from matricula.views.utils import get_active_period
from matricula.models import Enroll, Group
from django.utils.translation import ugettext_lazy as _
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.core.mail import send_mail
from django.conf import settings


class ActionsGroup:
    '''
    classdocs
    '''

    def action_copy_last_period(self, request, queryset):
        period = get_active_period()
        groups = []
        for group in queryset:
            group.pk = None
            group.period = period
            groups.append(group)

        self.model.objects.bulk_create(groups)

    def action_open_group(self, request, queryset):
        enrolls = Enroll.objects.filter(group__in=queryset)
        enrolls.update(enroll_activate=True)

    action_open_group.short_description = _("Open group")
    action_copy_last_period.short_description = _("Copy in the last period") 


class ViewsGroup:

    def get_message(self, message, message_type, extas=None):
        extras = extas or {}

        if 'inner-fragments' not in extras:
            extras['inner-fragments'] = {}

        extras['inner-fragments']['#message'] = '<div \
                class="alert alert-%(mtype)s" role="alert">%(message)s</div>' % {
                      'message': message,
                      'mtype': message_type
                    }

        return extras

    def get_email_message_open(self, *args, **kargs):
        return "Go to academica and enroll you"

    def get_email_message_close(self, *args, **kargs):

        val = args[0]
        return "Attention: %(group)s was closed" % val

    def student_list(self, request, pk):
        group = get_object_or_404(Group, pk=pk)
        enrolls = group.enroll_set.all()
        if request.GET.get('enroll', '0') == '1':
            print (request.GET.get('enroll', '0'))
            enrolls = enrolls.filter(enroll_finished=True)
        context = dict(
           # Include common variables for rendering the admin template.
           self.admin_site.each_context(request),
           group=group,
           title=_('Student List'),
           enrolls=enrolls
        )

        return TemplateResponse(request, "student_list.html", context)

    def open_group(self, request, pk):
        try:
            group = Group.objects.get(pk=pk)
        except:
            return self.get_message(_("Group Not Found"), 'warning')
        enrolls = Enroll.objects.filter(group=group)
        enrolls.update(enroll_activate=True)

        if request.GET.get('sendemail', '0') == '1':
            send_mail(_('%s is open now') % (str(group),),
                      self.get_email_message_open({'group': group}),
                      settings.DEFAULT_FROM_EMAIL,
                      [enroll.student.email for enroll in enrolls],
                      fail_silently=False
                      )
        message = self.get_message(_("This Group is open now"), 'success')
        message['inner-fragments']['#status'] = '<span class="glyphicon glyphicon-eye-open" aria-hidden="true"></span>'
        return message

    def close_group(self, request, pk):
        try:
            group = Group.objects.get(pk=pk)
        except:
            return self.get_message(_("Group Not Found"), 'warning')
        enrolls = Enroll.objects.filter(group=group)
        enrolls.update(enroll_activate=False)

        if request.GET.get('sendemail', '0') == '1':
            send_mail(_('%s was closed') % (str(group),),
                      self.get_email_message_close({'group': group}),
                      settings.DEFAULT_FROM_EMAIL,
                      [enroll.student.email for enroll in enrolls],
                      fail_silently=False
                      )
        message = self.get_message(_("This Group was closed"), 'success')
        message['inner-fragments']['#status'] = '<span class="glyphicon glyphicon-eye-close" aria-hidden="true"></span>'
        return message