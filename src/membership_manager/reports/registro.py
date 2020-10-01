from membership_manager.reports import reportes

REPORTES_DISPONIBLES = {
    'report_1': reportes.Reporte_Membresia_Pais,
    'report_2': reportes.Reporte_Membresia_Moneda,
    'report_3': reportes.Reporte_Membresia_Servicios,
    'report_4': reportes.Reporte_Factura_Pagada_Moneda,
}
REPORTES_TITULOS = {
    'report_1': 'Membresías por país.',
    'report_2': 'Membresías según moneda.',
    'report_3': 'Membresías según servicio.',
    'report_4': 'Facturas pagadas según moneda.',
}