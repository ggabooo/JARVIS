"""Las seis herramientas de JARVIS, con unidades, fechas y fuentes explícitas."""

import re
from datetime import datetime, timezone

import requests

from catalogo import INDICADORES


class JARVISTools:
    @staticmethod
    def _codigo(valor):
        valor = str(valor).strip().upper()
        if not re.fullmatch(r"[A-Z]{3}", valor):
            raise ValueError("Usa un código de tres letras, por ejemplo GTM o USD.")
        return valor

    @staticmethod
    def _get(url, params=None):
        try:
            response = requests.get(url, params=params, timeout=(5, 12))
            response.raise_for_status()
            return response.json()
        except requests.Timeout:
            return {"error": "La fuente tardó demasiado en responder. Intenta nuevamente."}
        except (requests.RequestException, ValueError):
            return {"error": "La fuente no está disponible o rechazó la consulta."}

    def consultar_tipo_cambio_api(self, moneda: str):
        moneda = self._codigo(moneda)
        resultado = self.consultar_tipo_cambio_alterno(moneda="GTQ", base=moneda)
        if "error" not in resultado:
            resultado["nota"] = "Tasa de referencia de ExchangeRate-API; no es la tasa oficial de Banguat ni una cotización bancaria."
        return resultado

    def consultar_tipo_cambio_alterno(self, moneda: str, base: str = "USD"):
        moneda, base = self._codigo(moneda), self._codigo(base)
        url = f"https://open.er-api.com/v6/latest/{base}"
        data = self._get(url)
        if isinstance(data, dict) and "error" in data:
            return data
        if not isinstance(data, dict) or data.get("result") != "success":
            return {"error": "No se pudo obtener el tipo de cambio."}
        valor = data.get("rates", {}).get(moneda)
        if valor is None:
            return {"error": f"No hay cotización para {moneda}."}
        return {
            "base": base, "moneda": moneda, "valor": valor,
            "unidad": f"{moneda} por 1 {base}",
            "fecha": data.get("time_last_update_utc"),
            "fuente": "ExchangeRate-API", "url_fuente": "https://www.exchangerate-api.com/",
            "url_datos": url,
        }

    def consultar_tipo_cambio_frankfurter(self, moneda: str, base: str = "GTQ"):
        moneda, base = self._codigo(moneda), self._codigo(base)
        url = "https://api.frankfurter.dev/v1/latest"
        data = self._get(url, {"base": base, "symbols": moneda})
        if isinstance(data, dict) and "error" in data:
            return {"error": "Frankfurter no respondió o no cubre estas monedas. Usa consultar_tipo_cambio_alterno."}
        valor = data.get("rates", {}).get(moneda) if isinstance(data, dict) else None
        if valor is None:
            return {"error": "Moneda sin cobertura en Frankfurter. Usa la otra herramienta de cambio."}
        return {
            "base": base, "moneda": moneda, "valor": valor,
            "unidad": f"{moneda} por 1 {base}", "fecha": data.get("date"),
            "fuente": "Frankfurter", "url_fuente": "https://www.frankfurter.dev/",
        }

    def consultar_indicador_macro(self, pais: str, indicador: str):
        pais = self._codigo(pais)
        indicador = str(indicador).strip().lower()
        if indicador not in INDICADORES:
            return {"error": "Indicador no disponible.", "disponibles": list(INDICADORES)}
        nombre, codigo, unidad = INDICADORES[indicador]
        url = f"https://api.worldbank.org/v2/country/{pais}/indicator/{codigo}"
        data = self._get(url, {"format": "json", "per_page": 1, "mrnev": 1})
        if isinstance(data, dict) and "error" in data:
            return data
        if not isinstance(data, list) or len(data) < 2 or not data[1]:
            return {"error": "No hay datos publicados para ese país e indicador."}
        item = data[1][0]
        if item.get("value") is None:
            return {"error": "La fuente no tiene un valor disponible."}
        return {
            "pais": item.get("country", {}).get("value", pais),
            "indicador": nombre, "codigo": codigo, "valor": item["value"],
            "unidad": unidad, "anio": item.get("date"),
            "fuente": "Banco Mundial · World Development Indicators",
            "url_fuente": f"https://data.worldbank.org/indicator/{codigo}?locations={pais}",
            "nota": "Último dato no vacío publicado. El año del dato puede ser anterior al actual.",
        }

    def consultar_deuda_publica_imf(self, pais: str):
        pais = self._codigo(pais)
        url = f"https://www.imf.org/external/datamapper/api/v1/GGXWDG_NGDP/{pais}"
        data = self._get(url)
        if isinstance(data, dict) and "error" in data:
            return data
        valores = data.get("values", {}).get("GGXWDG_NGDP", {}).get(pais, {}) if isinstance(data, dict) else {}
        actual = datetime.now(timezone.utc).year
        anios = [int(a) for a, v in valores.items() if str(a).isdigit() and int(a) <= actual and v is not None]
        if not anios:
            return {"error": "No hay un dato de deuda para el año actual o años anteriores."}
        anio = max(anios)
        return {
            "pais": pais, "indicador": "Deuda bruta del gobierno general",
            "valor": valores[str(anio)], "unidad": "% del PIB", "anio": anio,
            "fuente": "Fondo Monetario Internacional · WEO / DataMapper",
            "url_fuente": f"https://www.imf.org/external/datamapper/GGXWDG_NGDP@WEO/{pais}",
            "nota": "La serie WEO puede contener estimaciones o proyecciones. No se afirma que sea una cifra definitiva. Se excluyen años futuros. No es idéntica a la deuda del gobierno central del Banco Mundial.",
        }

    def consultar_precio_cripto(self, moneda: str):
        ids = {"bitcoin": "bitcoin", "btc": "bitcoin", "ethereum": "ethereum", "eth": "ethereum",
               "solana": "solana", "sol": "solana", "dogecoin": "dogecoin", "doge": "dogecoin"}
        nombre = ids.get(str(moneda).strip().lower())
        if not nombre:
            return {"error": "Criptoactivos disponibles: bitcoin, ethereum, solana y dogecoin."}
        url = "https://api.coingecko.com/api/v3/simple/price"
        data = self._get(url, {"ids": nombre, "vs_currencies": "usd", "include_last_updated_at": "true"})
        if isinstance(data, dict) and "error" in data:
            return data
        dato = data.get(nombre, {}) if isinstance(data, dict) else {}
        if dato.get("usd") is None:
            return {"error": "El proveedor no devolvió el precio; su API pública puede limitar consultas."}
        fecha = dato.get("last_updated_at")
        return {
            "cripto": nombre, "valor": dato["usd"], "unidad": "US$ por unidad",
            "fecha": datetime.fromtimestamp(fecha, timezone.utc).isoformat() if fecha else "No informada por la fuente",
            "fuente": "CoinGecko", "url_fuente": f"https://www.coingecko.com/en/coins/{nombre}",
        }
