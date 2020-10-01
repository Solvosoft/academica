import random


SHOW_LABEL_DATASET = """
function(tooltipItem, chart){
    return chart.datasets[tooltipItem.datasetIndex]['label']
}
"""


class StrObj:
    def __init__(self, text):
        self.text=text

    def __str__(self):
        return self.text
    def __repr__(self):
        return self.text




class ChartBuilder:
    iterative_color = False
    # Generic Chart builder
    def create_chart(self, chart_type, chart_data, girar_datos=False, reporte_especial=False):
        if chart_type == 'bar':
            return self.bar_builder(chart_data)
        if chart_type == 'line':
            return self.line_builder(chart_data)
        if chart_type == 'pie':
            return self.pie_builder(chart_data, girar_datos=girar_datos, reporte_especial=reporte_especial)
        if chart_type == 'doughnut':
            return self.doughnut_builder(chart_data, girar_datos=girar_datos, reporte_especial=reporte_especial)
        if chart_type == 'barstacked':
            return self.barstacked_builder(chart_data)

    def get_random_color(self):
        r = random.randint(0, 255)
        g = random.randint(0, 255)
        b = random.randint(0, 255)
        color = 'rgba(' + str(r) + ', ' + str(g) + ', ' + str(b) + ', 1)'
        return color

    def get_backgroud_color(self, dataset, color=None):
        if color is not None:
            return color
        if self.iterative_color and hasattr(dataset, '__iter__'):
            color = [self.get_random_color() for x in dataset]
        else:
            color = self.get_random_color()
        return color


    def get_scale_dict(self, axis_titles):
        return {
                'xAxes': [{
                    'scaleLabel': {
                        'display': 'true',
                        'labelString': axis_titles[0]
                    }
                }],
                'yAxes': [{
                    'scaleLabel': {
                        'display': 'true',
                        'labelString': axis_titles[1]
                    }
                }]
        }
    def build_graphic(self, data, graph_type, color=None, borderWidth=1, borderColor="rgba(255,255,255,0.4)" ):
        datasets = data['datasets']
        dataset_list = datasets[1]['dataset']
        axis_titles = data['axis_titles']
        chart_datasets = []

        index = 0
        try:
            for dataset in datasets[1]['dataset_labels']:
                colorr = self.get_backgroud_color(dataset, color)
                chart_datasets.append({
                    'label': dataset,
                    'backgroundColor': colorr,
                    'borderColor': borderColor,
                    'borderWidth': borderWidth,
                    'data': dataset_list[index]

                    })
                index += 1
            data = {
                'labels': list(data['labels']),
                'datasets': chart_datasets
            }
            chart = {
                'type': graph_type,
                'data': data,
                'options': {
                    'responsive': 'true',
                    'maintainAspectRatio': 'false',
                    'legend': {
                        'position': 'top',
                        },
                    'title': {
                        'display': 'true',
                        'text': datasets[0]
                    },

                    'scales': self.get_scale_dict(axis_titles)
                }
            }

            return chart
        except Exception as e:
            return  {'error': 'No Data Found!'}

    # Bar Chart Builder
    def bar_builder(self, data):
        return self.build_graphic(data, 'bar')

    # Pie Chart Builder
    def pie_builder(self, data, girar_datos=False, reporte_especial=False):
        new_data={}

        if len(data['datasets'][1]['dataset']) == 0:
            return {'error': 'No Data Found!'}
        else:

            new_data.update(data)
            if girar_datos:
                new_data['labels'] = data['datasets'][1]['dataset_labels']
                self.iterative_color = True
                if not reporte_especial:
                    new_data['datasets'][1]['dataset_labels'] = data['labels']
                    color = self.get_backgroud_color(new_data['labels'])
                else:
                    color = self.get_backgroud_color(data['labels'])
                new_data['datasets'][1]['dataset'] = self.reverse_list(data['datasets'][1]['dataset'])
            else:
                self.iterative_color = True
                color = self.get_backgroud_color(data['labels'])
            dev= self.build_graphic(new_data, 'pie', color=color, borderWidth=2)
            dev['options']['tooltips'] = {'callbacks': {'beforeLabel': StrObj(SHOW_LABEL_DATASET)}}
            if reporte_especial:
                 dev['data']['labels'] = data['labels']
            dev['options']['hover']= {'mode': 'nearest', 'intersect': 'true'}
            del dev['options']['scales']
            return dev

    def reverse_list(self, data):
        dev = []

        for pos in range(len(data[0])):
            interlist = []
            for elem in data:
                interlist.append(elem[pos])
            dev.append(interlist)
        return dev

    # Line Chart Builder
    def line_builder(self, data):

        labels = []

        if len(data['datasets'][1]['dataset']) == 0:
            return {'error': 'No Data Found!'}
        else:
            if len(data['datasets'][1]['dataset'][0]) == 1:
                labels = data['labels']
                data['labels'] = data['datasets'][1]['dataset_labels']
                data['datasets'][1]['dataset_labels'] = labels

            dev = self.build_graphic(data, 'line')

            if len(data['datasets'][1]['dataset'][0]) == 1:
                dev['data']['datasets'][0]['data'] = [x[0] for x in data['datasets'][1]['dataset']]

            for dataset in dev['data']['datasets']:
                dataset.update({ 'fill': 'false'})
                dataset['borderColor'] = dataset['backgroundColor']
                del dataset['borderWidth']

            return dev

    # Doughnut Chart Builder
    def doughnut_builder(self, data, girar_datos=False, reporte_especial=False):
        new_data = {}

        if len(data['datasets'][1]['dataset']) == 0:
            return {'error': 'No Data Found!'}
        else:
            new_data.update(data)
            if girar_datos:
                new_data['labels'] = data['datasets'][1]['dataset_labels']
                self.iterative_color = True
                if not reporte_especial:
                    new_data['datasets'][1]['dataset_labels'] = data['labels']
                    color = self.get_backgroud_color(new_data['labels'])
                else:
                    color = self.get_backgroud_color(data['labels'])
                new_data['datasets'][1]['dataset'] = self.reverse_list(data['datasets'][1]['dataset'])
            else:
                self.iterative_color = True
                color = self.get_backgroud_color(data['labels'])
            dev = self.build_graphic(new_data, 'doughnut', color=color, borderWidth=2)
            dev['options']['tooltips'] = {'callbacks': {'beforeLabel': StrObj(SHOW_LABEL_DATASET)}}
            if reporte_especial:
                dev['data']['labels'] = data['labels']
            dev['options']['hover']= {'mode': 'nearest', 'intersect': 'true'}
            del dev['options']['scales']
            return dev

    def barstacked_builder(self, chart_data):
        for dataset in chart_data['datasets'][1]['dataset']:
            color = self.get_backgroud_color(dataset)
            dataset.update({'backgroundColor': color,
                            'borderColor': color,
                            'borderWidth': 1})

        axis_titles = chart_data['axis_titles']
        chart = {
            'type': 'bar',
            'data': {
                'labels': list(chart_data['labels']),
                'datasets': chart_data['datasets'][1]['dataset']
            },
            'options': {
                'responsive': 'true',
                'maintainAspectRatio': 'false',
                'legend': {
                    'position': 'top',
                },
                'title': {
                    'display': 'true',
                    'text': chart_data['datasets'][0]
                },
                'tooltips': {
                    'mode': 'nearest',
                    'intersect': 'true'
                },
                'scales': {

                    'xAxes': [{
                        'stacked': 'true',
                        'scaleLabel': {
                            'display': 'true',
                            'labelString': axis_titles[0]

                        }
                    }],

                    'yAxes': [{'stacked': 'true',
                        'scaleLabel': {
                            'display': 'true',
                            'labelString': axis_titles[1]
                        }
                    }]
                }
            }
        }
        return chart