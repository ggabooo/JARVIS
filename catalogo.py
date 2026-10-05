"""Indicadores y etiquetas compartidos por la interfaz y las herramientas."""

INDICADORES = {
    "inflacion": ("Inflación", "FP.CPI.TOTL.ZG", "% anual"),
    "pib": ("Producto interno bruto", "NY.GDP.MKTP.CD", "US$ corrientes"),
    "pib_per_capita": ("PIB por habitante", "NY.GDP.PCAP.CD", "US$ corrientes por habitante"),
    "desempleo": ("Desempleo", "SL.UEM.TOTL.ZS", "% de la fuerza laboral; estimación modelada OIT"),
    "deuda_publica": ("Deuda del gobierno central", "GC.DOD.TOTL.GD.ZS", "% del PIB"),
    "crecimiento_pib": ("Crecimiento del PIB", "NY.GDP.MKTP.KD.ZG", "% anual"),
    "remesas": ("Remesas personales recibidas", "BX.TRF.PWKR.DT.GD.ZS", "% del PIB"),
    "exportaciones": ("Exportaciones de bienes y servicios", "NE.EXP.GNFS.ZS", "% del PIB"),
    "importaciones": ("Importaciones de bienes y servicios", "NE.IMP.GNFS.ZS", "% del PIB"),
    "cuenta_corriente": ("Saldo en cuenta corriente", "BN.CAB.XOKA.GD.ZS", "% del PIB"),
    "inversion_extranjera": ("Inversión extranjera directa, entradas netas", "BX.KLT.DINV.WD.GD.ZS", "% del PIB"),
    "formacion_capital": ("Formación bruta de capital", "NE.GDI.TOTL.ZS", "% del PIB"),
    "ahorro_bruto": ("Ahorro bruto", "NY.GNS.ICTR.ZS", "% del PIB"),
    "gasto_educacion": ("Gasto público en educación", "SE.XPD.TOTL.GD.ZS", "% del PIB"),
    "ingresos_tributarios": ("Ingresos tributarios", "GC.TAX.TOTL.GD.ZS", "% del PIB"),
    "deuda_externa": ("Deuda externa total", "DT.DOD.DECT.GN.ZS", "% del ingreso nacional bruto"),
    "poblacion": ("Población total", "SP.POP.TOTL", "habitantes"),
    "crecimiento_poblacional": ("Crecimiento poblacional", "SP.POP.GROW", "% anual"),
    "consumo_hogares": ("Consumo de hogares e ISFLSH", "NE.CON.PRVT.ZS", "% del PIB"),
    "consumo_gobierno": ("Consumo del gobierno", "NE.CON.GOVT.ZS", "% del PIB"),
    "formacion_capital_fijo": ("Formación bruta de capital fijo", "NE.GDI.FTOT.ZS", "% del PIB"),
}

RUBROS = {
    "Producción y crecimiento": ["pib", "pib_per_capita", "crecimiento_pib"],
    "Precios y empleo": ["inflacion", "desempleo"],
    "Finanzas públicas": ["deuda_publica_imf", "deuda_publica", "ingresos_tributarios", "gasto_educacion"],
    "Sector externo": ["remesas", "exportaciones", "importaciones", "cuenta_corriente", "inversion_extranjera", "deuda_externa"],
    "Inversión y consumo": ["formacion_capital", "formacion_capital_fijo", "ahorro_bruto", "consumo_hogares", "consumo_gobierno"],
    "Población": ["poblacion", "crecimiento_poblacional"],
    "Divisas": [],
    "Criptoactivos": [],
}

PAISES = {
    "Guatemala": "GTM", "El Salvador": "SLV", "Honduras": "HND",
    "Nicaragua": "NIC", "Costa Rica": "CRI", "Panamá": "PAN",
    "México": "MEX", "Estados Unidos": "USA", "Canadá": "CAN",
    "República Dominicana": "DOM", "Colombia": "COL", "Ecuador": "ECU",
    "Perú": "PER", "Bolivia": "BOL", "Chile": "CHL", "Argentina": "ARG",
    "Brasil": "BRA", "España": "ESP", "Alemania": "DEU", "China": "CHN",
    "India": "IND", "Rusia": "RUS", "Turquía": "TUR", "Japón": "JPN",
}


def etiqueta(indicador):
    if indicador == "deuda_publica_imf":
        return "Deuda del gobierno general · FMI"
    return INDICADORES[indicador][0]
