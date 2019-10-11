"""
This file was generated with the customdashboard management command and
contains the class for the main dashboard.

To activate your index dashboard add the following to your settings.py::
    GRAPPELLI_INDEX_DASHBOARD = 'src.dashboard.CustomIndexDashboard'
"""

from django.utils.translation import ugettext_lazy as _
from django.urls import reverse

from grappelli.dashboard import modules, Dashboard
from grappelli.dashboard.utils import get_admin_site_name


class CustomIndexDashboard(Dashboard):
    """
    Custom index dashboard for www.
    """

    def init_with_context(self, context):
        site_name = get_admin_site_name(context)

        # append a group for "Administration" & "Applications"
        self.children.append(
                modules.ModelList(
                    _('Administration'),
                    column=1,
                    collapsible=False,
                    models=('django.contrib.*',),

        ))

        # append an app list module for "Applications"
        self.children.append(modules.ModelList(
            _('Administración del gestor de membresías'),
            collapsible=False,
            column=1,
            models=('membership_core.*', )
        ))

        # append an app list module for "Administration"
        self.children.append(modules.ModelList(
            _('Gestion de membresías'),
            column=2,
            collapsible=False,
            models=('membership_manager.*',),
        ))
        self.children.append(modules.AppList(
            _('Gestión de correo'),
            collapsible=False,
            column=3,
            models=('async_notifications.*', )
        ))