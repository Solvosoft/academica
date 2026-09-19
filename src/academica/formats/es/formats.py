# Formatos propios del sitio (reemplazan los del locale "es" de Django).
DATE_FORMAT = 'd/m/Y'
SHORT_DATE_FORMAT = 'd/m/Y'
DATETIME_FORMAT = 'd/m/Y H:i'
SHORT_DATETIME_FORMAT = 'd/m/Y H:i'
DATE_INPUT_FORMATS = ['%d/%m/%Y', '%Y-%m-%d', '%d/%m/%y']
DATETIME_INPUT_FORMATS = [
    '%d/%m/%Y %H:%M',
    '%m/%d/%Y %H:%M',
    '%Y-%m-%d %H:%M',
    '%d/%m/%y %H:%M',
    '%Y/%m/%d %H:%M %A',
]
