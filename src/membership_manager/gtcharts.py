from django.utils.timezone import now
from djgentelella.chartjs import LineChart, VerticalBarChart
from djgentelella.groute import register_lookups
from django.db.models import Count, Q, Sum


from membership_core.models import SystemCurrency
from membership_manager.models import MembershipRenew, Invoice

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
        return ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio',
                'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']

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
                'text': 'Vencimientos por mes'
                }

    def get_datasets(self):
        self.index = 3
        return [{'label': 'Cantidad de vencimientos',
                'backgroundColor': self.get_color(),
                'borderColor': self.get_color(),
                'borderWidth': 1,
                'data': self.extact_data()
                },
        ]

    def extact_data(self):
        filtres = {'m%d'%m: Count('pk', filter=Q(end_date__month=m)) for m in range(1,13)}
        queryset = MembershipRenew.objects.filter(end_date__year=now().year).aggregate(
            **filtres
        )
        return [queryset['m%d'%m] or 0 for m in range(1,13)]


@register_lookups(prefix="pagoanual", basename="pagoanual")
class PagoFacturasMes(BaseChart, LineChart):

    def get_title(self):
        return {'display': True,
                'text': 'Recaudación mensual'
                }

    def get_datasets(self):
        self.index = 6
        return [{'label': x.currency,
                'backgroundColor': self.get_color(),
                'borderColor': self.get_color(),
                'borderWidth': 1,
                'data': self.extact_data(x)
                } for x in SystemCurrency.objects.all()
        ]

    def extact_data(self, currency):
        filtres = {'m%d'%m: Sum('amount', filter=Q(payment_date__month=m)) for m in range(1,13)}
        queryset = Invoice.objects.filter(payment_date__year=now().year, currency=currency, status='paid').aggregate(
            **filtres
        )
        return [queryset['m%d'%m] or 0 for m in range(1,13)]
