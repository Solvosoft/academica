from djgentelella.chartjs import LineChart, VerticalBarChart
from djgentelella.groute import register_lookups
from django.db.models import Count, Q
from matricula.models import Enroll, Group, Period
from django.utils.translation import gettext as _


default_colors = ["229, 158, 64", "240, 180, 150", "0, 168, 150", "207, 130, 182", "2, 128, 144", "1, 148, 147",
          "240, 112, 96", "153, 235, 168", "241, 179, 167", "242, 137, 76", "175, 151, 195",
          "161, 178, 200",
          "245, 216, 144", "216, 15, 53", "233, 175, 97", "4, 115, 143", "162, 237, 133", "226, 148, 72",
          "5, 102, 141", "241, 125, 90", "236, 194, 128", "220, 239, 133", "242, 157, 175", "187, 141, 189",
          "238, 186, 140", "238, 16, 58", "2, 195, 154", "121, 219, 172", "239, 98, 104", "231, 167, 81"]


class BaseChart:
    colors = default_colors

    def get_color(self):
        self.index = (self.index + 1) % len(self.colors)
        color_list = self.colors[self.index]
        color = 'rgb(' + color_list + ')'
        return color

    def get_labels(self):
        return [i.name for i in Period.objects.all().order_by('-id')[:10]]

    def get_datasets(self):
        self.index = 0
        return [{'label': 'Stairway',
                'backgroundColor': self.get_color(),
                'borderColor': self.get_color(),
                'borderWidth': 1,
                'data': [1,2,3,4,5,6,7]
                },
                {'label': 'Fibonacci',
                 'backgroundColor': self.get_color(),
                 'borderColor': self.get_color(),
                 'borderWidth': 1,
                 'data': [0,1,1,2,3,5,8]
                 },
                {'label': 'Base 2',
                 'backgroundColor': self.get_color(),
                 'borderColor': self.get_color(),
                 'borderWidth': 1,
                 'data': [1, 2, 4, 8, 16, 32, 64]
                 },
        ]

@register_lookups(prefix="vencimientoanual", basename="vencimientoanual")
class VencimientosMes(BaseChart, VerticalBarChart):
    def get_title(self):
        return {'display': True,
                'text': _('Courses')
                }

    def get_datasets(self):
        self.index = 3
        return [{'label': _('Number of courses by period'),
                'backgroundColor': self.get_color(),
                'borderColor': self.get_color(),
                'borderWidth': 1,
                'data': self.extact_data()
                },
        ]

    def get_scales(self):
        return {'xAxes': [{'stacked': True, }], 'yAxes': [{"beginAtZero":True, 'stacked': True}]}

    def extact_data(self):
        filtres = {'m%s'%m: Count('pk', filter=Q(period__name=m)) for m in self.get_labels()}
        queryset = Group.objects.filter(period__name__in=self.get_labels()).aggregate(
            **filtres
        )
        return [queryset['m%s'%m] or 0 for m in self.get_labels()]


@register_lookups(prefix="pagoanual", basename="pagoanual")
class PagoFacturasMes(BaseChart, LineChart):

    def get_title(self):
        return {'display': True,
                'text': _('Courses by period')
                }

    def get_scales(self):
        return {'xAxes': [{'stacked': True, }], 'yAxes': [{"beginAtZero":True, 'stacked': True}]}

    def get_labels(self):
        return [i.name for i in Group.objects.all().order_by('-id')[:10]]

    def get_datasets(self):
        self.index = 6
        return [{'label': x,
                'backgroundColor': self.get_color(),
                'borderColor': self.get_color(),
                'borderWidth': 1,
                'data': self.extact_data()
                } for x in ['total']
        ]

    def extact_data(self):
        filtres = {'m%s'%m: Count('pk', filter=Q(group__name=m)) for m in self.get_labels()}
        queryset = Enroll.objects.filter(rejected=False).aggregate(
            **filtres
        )
        return [queryset['m%s'%m] or 0 for m in self.get_labels()]
