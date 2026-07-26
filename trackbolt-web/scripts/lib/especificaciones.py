"""Extrae especificaciones tecnicas de la descripcion libre del ERP.

Cada campo puede quedar en None: es preferible no mostrar un dato a mostrarlo mal.
Toda medida encontrada pasa por un validador; si no es plausible, se descarta.
"""
import re

# Diametros metricos normalizados (ISO). Sirven para desambiguar '24X76' (metrico)
# de '1 X 5' (pulgadas) cuando la descripcion no dice ni MM ni trae fraccion.
DIAMETROS_METRICOS = {3, 4, 5, 6, 7, 8, 9, 10, 12, 14, 16, 18, 20, 22, 24, 27, 30, 33, 36, 39, 42, 45, 48}

# Denominadores validos de una fraccion en pulgadas, del mas largo al mas corto y
# sin digito detras. Descarta '250/350' y '416/420', que son modelos de vehiculo.
_DEN = r"(?:64|32|16|8|4|2)(?!\d)"
# La parte entera de una fraccion compuesta va de 1 a 2 digitos: asi '304 5/32'
# se lee como 5/32 y no como 304 y 5/32.
_FRAC = (rf"(?<!\d)(?:\d{{1,2}}\s*[.,\-]\s*\d{{1,2}}\s*/\s*{_DEN}"
         rf"|\d{{1,2}}\s+\d{{1,2}}\s*/\s*{_DEN}"
         rf"|\d{{1,3}}\s*/\s*{_DEN})")
_ENT = r"(?<!\d)\d{1,3}"

# Marca de vehiculo o maquina -> nombre para mostrar. El ERP escribe 'MERCEDEZ',
# 'HIUNDAY' y 'JHON DEER', asi que el patron cubre las variantes reales del archivo.
MARCAS_VEHICULO = [
    (r"MERCEDE[SZ]", "Mercedes-Benz"),
    (r"\bFORD\b", "Ford"),
    (r"SCANIA", "Scania"),
    (r"VOLKW|VOLKSWAGEN", "Volkswagen"),
    (r"TOYOTA|HY?LUX|HILUX", "Toyota"),
    (r"MAS+EY", "Massey Ferguson"),
    (r"\bINTER\b|INTERNATIONAL", "International"),
    (r"\bNKR\b|\bNPR\b|ISUZU", "Isuzu"),
    (r"VOLVO", "Volvo"),
    (r"\bFIAT\b", "Fiat"),
    (r"HIUNDAY|HYUNDAI", "Hyundai"),
    (r"AGRAL+E", "Agrale"),
    (r"IVECO", "Iveco"),
    (r"J[OH]H?N\s*DEER", "John Deere"),
    (r"\bCAT\b|CATERPILLAR", "Caterpillar"),
    (r"KOMATSU", "Komatsu"),
    (r"CHEVROLET|\bGM\b", "Chevrolet / GM"),
    (r"NISSAN", "Nissan"),
    (r"\bHINO\b", "Hino"),
    (r"KENWORTH", "Kenworth"),
    (r"FREIGHTLINER", "Freightliner"),
    (r"MITSUBISHI|CANTER", "Mitsubishi"),
    (r"DAIHATSU", "Daihatsu"),
    (r"VALTRA", "Valtra"),
    (r"NEW\s*HOLLAND", "New Holland"),
    (r"\bTHOMAS\b", "Thomas"),
    (r"\bJAC\b", "JAC"),
    (r"FOTON", "Foton"),
    (r"\bDAF\b", "DAF"),
    (r"RENAULT", "Renault"),
    (r"\bDODGE\b", "Dodge"),
]
_MARCAS = [(re.compile(p), n) for p, n in MARCAS_VEHICULO]

# Numeros de parte de fabricante de maquinaria: 6Y0846 (CAT), 20Y3211210 (Komatsu).
_OEM = re.compile(r"\b\d[A-Z]\d{4}\b|\b\d{2}[A-Z]\d{6,8}\b")
_REF_SATA = re.compile(r"\bST\d{4,6}[A-Z]{0,2}\b|\b\d-\d{5}\b")
_TIENE_FRACCION = re.compile(rf"\b{_FRAC}")

# Designaciones de norma y sufijos que parecen medidas pero no lo son.
_RUIDO = [
    re.compile(r"\bF-?4\d{2}\b"),          # arandela estructural F-436
    re.compile(r"\bA-?193\b|\bA-?325\b|\bA-?490\b|\bASTM\b|\bDIN\b|\bISO\b"),
    re.compile(r"\b\d{1,2}H\b"),           # tuerca 2H, 6H, 13H
    re.compile(r"\b\d{3,4}\s*(?:PC|PZ|PCS)\b"),
    re.compile(r"\b6\s*PT\b|\b12\s*PT\b"),
    re.compile(r"ESTRIAS?\s*[\d\"/.,]*"),  # ESTRIA 23 es el numero de estrias
    re.compile(r"\bGALS?\b|\bGALC\b|\bIRIZ\b|\bSOLO\b|\bRF\b|\bZB\b|\bRO\b"),
    re.compile(r"\bUNC\b|\bUNF\b|\bMULA\b|\bNIQUEL\b|\bTIPO\b|\bAJOVER\b"),
    re.compile(r"\b30[46]\b|\b316\b|\bA[24]\b"),   # designacion de inoxidable
    re.compile(r"(?:N[ºo°]|#)\s*\d{1,2}"),           # calibre Nº10, #14
]
_PARENTESIS = re.compile(r"\(([^)]*)\)")
# Se conserva el contenido del parentesis si es un paso de rosca o una fraccion.
_UTIL_EN_PARENTESIS = re.compile(rf"^\s*(?:\d[.,]\d{{1,2}}|{_FRAC})\s*\"?\s*$")


def _num(t):
    return float(str(t).replace(",", "."))


def valor_pulgadas(texto):
    """'1.1/2' -> 1.5 | '21/2' -> 2.5 | '3/8' -> 0.375 | '1 -1/4' -> 1.25"""
    t = re.sub(r"\s+", "", str(texto)).replace('"', "").replace(",", ".")
    m = re.fullmatch(r"(\d+)[.\-](\d+)/(\d+)", t)
    if m:
        entero, num, den = int(m.group(1)), int(m.group(2)), int(m.group(3))
        return entero + num / den if den else None
    m = re.fullmatch(r"(\d+)/(\d+)", t)
    if m:
        num, den = int(m.group(1)), int(m.group(2))
        if den == 0:
            return None
        if num >= den and len(str(num)) > 1:
            # '21/2' es '2.1/2' mal escrito en el ERP
            entero, resto = int(str(num)[:-1]), int(str(num)[-1])
            if resto < den:
                return entero + resto / den
        return num / den
    m = re.fullmatch(r"(\d+)(?:[.](\d+))?", t)
    if m:
        return _num(m.group(0))
    return None


def formato_pulgadas(texto):
    """Normaliza la fraccion para mostrarla: '1.1/2' -> '1-1/2\"'"""
    t = re.sub(r"\s+", "", str(texto)).replace('"', "").replace(",", ".")
    t = re.sub(r"^(\d+)[.](\d+/\d+)$", r"\1-\2", t)
    m = re.fullmatch(r"(\d+)/(\d+)", t)
    if m and int(m.group(1)) >= int(m.group(2)) and len(m.group(1)) > 1:
        t = f"{m.group(1)[:-1]}-{m.group(1)[-1]}/{m.group(2)}"
    return t + '"'


def _quitar_ruido(d):
    """Elimina normas y comentarios; conserva los parentesis que son un paso de rosca."""
    def _par(m):
        return f" {m.group(1)} " if _UTIL_EN_PARENTESIS.match(m.group(1)) else " "
    d = _PARENTESIS.sub(_par, d)
    for patron in _RUIDO:
        d = patron.sub(" ", d)
    return d


def detectar_sistema(desc):
    d = desc.upper()
    fraccion = bool(_TIENE_FRACCION.search(d))
    if re.search(r"\bUNC\b|\bUNF\b|PULGADA", d):
        return "pulgadas"
    metrico = r"\bMM\b|\dMM\b|\bMM\d|MILIMETRIC|\bPASO\b|\bM[-\s]?\d{1,2}\b"
    if re.search(metrico, d) and not fraccion:
        return "metrico"
    if fraccion:
        return "pulgadas"
    if re.search(metrico, d):
        return "metrico"
    return None


def _valida_mm(dia, paso, largo):
    if dia is not None and not (2 <= dia <= 64):
        return False
    if paso is not None and not (0.3 <= paso <= 6.5):
        return False
    if largo is not None and not (4 <= largo <= 600):
        return False
    # Un largo mucho menor que el diametro no es un largo: suele ser el numero
    # de estrias o un codigo de modelo ('PERNO INTER 22 X 5').
    if dia is not None and largo is not None and largo < dia * 0.35:
        return False
    return True


# Candidatos metricos, del mas especifico al mas generico.
# Cada entrada es (regex, funcion que arma el diccionario de medidas).
_MM_CANDIDATOS = [
    # ESPARRAGO MILIMETRICO 8 1.25X1.25 X 70
    (re.compile(r"(?<![\d.,])(\d{1,2})\s+(\d[.,]\d{1,2})\s*[Xx]\s*(\d[.,]\d{1,2})\s*[Xx]\s*(\d{1,3})(?![\d.,])"),
     lambda m: {"dia": _num(m[1]), "paso": _num(m[2]), "paso2": _num(m[3]), "largo": _num(m[4])}),
    # TOR HEX MM 10.9 PASO 2.00 16 X 270
    (re.compile(r"PASO\s*(?:FINO\s*)?(\d[.,]\d{1,2})\s+M?\s?(\d{1,2})\s*[Xx]\s*(\d{1,3})(?![\d.,])"),
     lambda m: {"paso": _num(m[1]), "dia": _num(m[2]), "largo": _num(m[3])}),
    # TORNILLO HEX MM CL10.9 RP 14 X 2.00 X 90   |   PERNO FORD M14X1,50X70
    (re.compile(r"(?<![\d.,/])M?\s?(\d{1,2})\s*[Xx]\s*(\d[.,]\d{1,2})\s*[Xx]\s*(\d{1,3}(?:[.,]\d)?)(?![\d])"),
     lambda m: {"dia": _num(m[1]), "paso": _num(m[2]), "largo": _num(m[3])}),
    # TOR CAB CILIN JISS 3-0.50 X 50   |   TORNILLO HEX MM CL8.8 RT 14 - 2.00 X 40
    (re.compile(r"(?<![\d.,/])(\d{1,2})\s*-\s*(\d[.,]\d{1,2})\s*[Xx]\s*(\d{1,3})(?![\d.,])"),
     lambda m: {"dia": _num(m[1]), "paso": _num(m[2]), "largo": _num(m[3])}),
    # TUERCA CUADRADA ZTA 20 -1.50
    (re.compile(r"(?<![\d.,/])(\d{1,2})\s*-\s*(\d[.,]\d{1,2})(?![\d.,]*[Xx])"),
     lambda m: {"dia": _num(m[1]), "paso": _num(m[2])}),
    # TORNILLO ZAPATA 20 X 60 PASO 1.5   |   PERNO MERCEDES 22 X 130 (1.50)
    (re.compile(r"(?<![\d.,/])(\d{1,2})\s*[Xx]\s*(\d{1,3})\s*(?:PASO\s*|P\.?\s+)(\d[.,]?\d{0,2})"),
     lambda m: {"dia": _num(m[1]), "largo": _num(m[2]), "paso": _num(m[3])}),
    # TUERCA HEXAGONAL MM 16 PASO 2.0   |   TUERCA HEX FLANGE BICRO 14M P 1.50
    (re.compile(r"(?<![\d.,/])M?\s?(\d{1,2})\s?M?\s+(?:PASO|P\.?)\s*(\d[.,]\d{1,2})"),
     lambda m: {"dia": _num(m[1]), "paso": _num(m[2])}),
    # TUERCA DE SEG FLANGE STOVER PASO 1.50 M20   |   TUERCA DE SEG NYLON MM PASO 3.00 24
    (re.compile(r"(?:PASO|P\.?)\s*(?:FINO\s*)?(\d[.,]\d{1,2})\s+M?\s?(\d{1,2})(?![\d.,])"),
     lambda m: {"paso": _num(m[1]), "dia": _num(m[2])}),
    # TUERCA HEX ALTA M12 X 1.50
    (re.compile(r"\bM\s?(\d{1,2})\s*[Xx]\s*(\d[.,]\d{1,2})(?![\d.,]*[Xx])"),
     lambda m: {"dia": _num(m[1]), "paso": _num(m[2])}),
    # VARILLA ROSCADA NEGRA POR METRO MM 16 X 2.00  (diametro por paso, sin largo)
    (re.compile(r"(?<![\d.,/])(\d{1,2})\s*[Xx]\s*(\d[.,]\d{1,2})(?![\d.,]*[Xx])"),
     lambda m: {"dia": _num(m[1]), "paso": _num(m[2])}),
    # TOR ZAPATA 12.9 24X120
    (re.compile(r"(?<![\d.,/])(\d{1,2})\s*[Xx]\s*(\d{1,3})(?![\d.,/])"),
     lambda m: {"dia": _num(m[1]), "largo": _num(m[2])}),
    # TORNILLO HEX MM CL10.9 RP 24 X .00 X 120   (paso escrito mal en el ERP)
    (re.compile(r"(?<![\d.,/])(\d{1,2})\s*[Xx]\s*[\d.,]*\s*[Xx]\s*(\d{1,3})(?![\d.,])"),
     lambda m: {"dia": _num(m[1]), "largo": _num(m[2])}),
    # TUERCA ESPECIAL PERNO ALTA 1.50 12   (paso y luego diametro, sin la palabra PASO)
    (re.compile(r"(?<![\d.,])(\d[.,]\d{2})\s+(\d{1,2})(?![\d.,])"),
     lambda m: {"paso": _num(m[1]), "dia": _num(m[2])}),
    # TUERCA HEX INOX M 14   |   TUERCA DE SEG NYLON M4   |   TUERCA HEX BICRO M-4
    (re.compile(r"\bM[-\s]?(\d{1,2})(?![\d.,])"),
     lambda m: {"dia": _num(m[1])}),
    # TUERCA CONICA MM PASO 1.50 16M
    (re.compile(r"(?<![\d.,])(\d{1,2})\s?M\b"),
     lambda m: {"dia": _num(m[1])}),
    # PIN SEGUER EXTERNO 41MM   |   ARAN DE COBRE PARA SELLO MM8
    (re.compile(r"(?<![\d.,])(\d{1,2})\s*MM\b|\bMM\s?(\d{1,2})\b"),
     lambda m: {"dia": _num(m[1] or m[2])}),
]

# Ultimo recurso: un entero suelto al final ('ARANDELA CONICA DE 18'). Solo se
# usa cuando la descripcion no trae ninguna medida con 'X', para no confundir
# el numero de estrias o un modelo con el diametro.
_MM_ENTERO_FINAL = re.compile(r"(?<![\d.,/])(\d{1,2})\s*$")
_TIENE_POR = re.compile(r"\d\s*[Xx]\s*\d")


def _medidas_metricas(d, exigir_normalizado=False):
    """exigir_normalizado descarta diametros fuera de la serie ISO, salvo que la
    coincidencia traiga un paso de rosca: un paso decimal ya prueba que es metrico."""
    candidatos = list(_MM_CANDIDATOS)
    if not _TIENE_POR.search(d):
        candidatos.append((_MM_ENTERO_FINAL, lambda m: {"dia": _num(m[1])}))
    for patron, armar in candidatos:
        for m in patron.finditer(d):
            med = armar(m)
            if not _valida_mm(med.get("dia"), med.get("paso"), med.get("largo")):
                continue
            if (exigir_normalizado and not med.get("paso")
                    and med.get("dia") not in DIAMETROS_METRICOS):
                continue
            return med
    return {}


_PULG_CANDIDATOS = [
    # ESPARRAGO MIXTO 1/2 X 1/2 X 3  -> diametro y largo son el primero y el ultimo
    re.compile(rf"({_FRAC}|{_ENT})\s*[Xx]\s*(?:{_FRAC}|{_ENT})\s*[Xx]\s*({_FRAC}|{_ENT})"),
    re.compile(rf"({_FRAC})\s*[Xx]\s*({_FRAC}|{_ENT})"),
    re.compile(rf"({_ENT})\s*[Xx]\s*({_FRAC})"),
    re.compile(rf"({_FRAC})"),
    re.compile(rf"({_ENT})\s*[Xx]\s*({_ENT})"),
    re.compile(rf"({_ENT})\s*[\s\"]*$"),
]


def _medidas_pulgadas(d):
    texto = d.strip()
    par_rechazado = False
    for indice, patron in enumerate(_PULG_CANDIDATOS):
        # Los candidatos de un solo valor van despues del indice 2; si ya hubo un
        # par valido cuyo diametro se rechazo, tomar el largo como diametro seria peor.
        if indice >= 3 and par_rechazado:
            break
        for m in patron.finditer(texto):
            dia = valor_pulgadas(m.group(1))
            if dia is None or not (0.05 <= dia <= 4):
                if m.lastindex and m.lastindex >= 2:
                    par_rechazado = True
                continue
            med = {"dia_pulg": dia, "dia_txt": formato_pulgadas(m.group(1))}
            if m.lastindex and m.lastindex >= 2:
                largo = valor_pulgadas(m.group(2))
                if largo is not None and 0.1 <= largo <= 24:
                    med["largo_pulg"] = largo
                    med["largo_txt"] = formato_pulgadas(m.group(2))
            return med
    return {}


def _grado(d):
    m = re.search(r"\bCL\s*(\d{1,2}[.,]\d)\b", d)
    if m:
        return f"Clase {m.group(1).replace(',', '.')}", m.group(1).replace(",", ".")
    m = re.search(r"\b(4[.,]6|5[.,]8|6[.,]8|8[.,]8|10[.,]9|12[.,]9|13[.,]9|14[.,]9)\b", d)
    if m:
        v = m.group(1).replace(",", ".")
        return f"Clase {v}", v
    m = re.search(r"\bG(?:R|RA|RADO)?\.?\s*(\d)\b", d)
    if m:
        return f"Grado {m.group(1)}", f"G{m.group(1)}"
    if re.search(r"\bB7\b", d):
        return "ASTM A193 B7", "B7"
    if re.search(r"INOX|\b304\b|\b316\b|\bA2\b|\bA4\b", d):
        return "Inoxidable A2 (304)", "INOX"
    m = re.search(r"\bCL(?:ASE)?\s*(\d{1,2})\b", d)
    if m:
        return f"Clase {m.group(1)}", m.group(1)
    return None, None


def _acabado(d, clave_grado):
    if re.search(r"INOX|\b304\b|\b316\b|\bA2\b|\bA4\b", d):
        return "Inoxidable"
    if re.search(r"BICRO", d):
        return "Bicromatado"
    if re.search(r"ZINCAD|\bZINC\b|GALVAN|\bGALS?\b|\bGALC\b", d):
        return "Zincado"
    if re.search(r"NEGR|PAVON", d):
        return "Negro"
    if re.search(r"NEOPRENO", d):
        return "Neopreno"
    if re.search(r"PLASTIC|\bPVC\b", d):
        return "Plástico"
    if clave_grado in {"10.9", "12.9", "13.9", "G8", "B7"}:
        return "Negro"
    if clave_grado in {"G2", "G5"}:
        return "Zincado"
    return None


def _cabeza(d, sublinea):
    t = (d + " " + sublinea).upper()
    if "FLANGE" in t:
        return "Flange (con arandela integrada)"
    if "BRISTOL" in t or "ALLEN" in t:
        if "AVELLAN" in t:
            return "Avellanada Bristol"
        if "BUTON" in t or "BOTON" in t:
            return "Botón Bristol"
        if "SIN CAB" in t or "PRISIONERO" in t:
            return "Sin cabeza (prisionero)"
        return "Cilíndrica Bristol"
    if "AVELLAN" in t:
        return "Avellanada"
    if "CUADRAD" in t:
        return "Cuadrada"
    if "CARRIAGE" in t or "CARRIAJE" in t or "CARIAJE" in t:
        return "Carriage (cuello cuadrado)"
    if "CUCHILLA" in t:
        return "Avellanada de cuchilla"
    if "CENTRAL" in t:
        return "Central"
    if "CILINDRIC" in t:
        return "Cilíndrica"
    if "MARIPOSA" in t:
        return "Mariposa"
    if "HEX" in t:
        return "Hexagonal"
    return None


def _rosca(d):
    serie = None
    if re.search(r"\bUNC\b", d):
        serie = "UNC (ordinaria)"
    elif re.search(r"\bUNF\b", d):
        serie = "UNF (fina)"
    elif re.search(r"PASO\s*FINO|ROSCA\s*FINA", d):
        serie = "Paso fino"
    largo = None
    if re.search(r"\bRP\b", d):
        largo = "Parcial"
    elif re.search(r"\bR[IT]\b|ROSCA\s*TOTAL", d):
        largo = "Total"
    return serie, largo


def _vehiculo(d):
    for patron, nombre in _MARCAS:
        if patron.search(d):
            return nombre
    return None


def extraer(descripcion, sublinea="", es_herramienta=False, roscado=True):
    """Devuelve el diccionario de especificaciones de una descripcion del ERP.

    roscado=False (arandelas, pines) hace que el diametro se muestre como '20 mm'
    en vez de 'M20', porque ahi no hay rosca que designar.
    """
    d = " " + descripcion.upper() + " "
    esp = {
        "sistema": None, "diametro": None, "diametro_orden": None,
        "largo": None, "largo_orden": None, "paso": None,
        "grado": None, "grado_clave": None, "acabado": None,
        "cabeza": None, "rosca_serie": None, "rosca_largo": None,
        "numero_parte": None, "referencia_fabricante": None, "vehiculo": None,
        "medida": None,
    }

    m = _OEM.search(d)
    if m:
        esp["numero_parte"] = m.group(0)
    m = _REF_SATA.search(d)
    if m:
        esp["referencia_fabricante"] = m.group(0)

    if es_herramienta:
        return esp

    esp["grado"], esp["grado_clave"] = _grado(d)
    esp["acabado"] = _acabado(d, esp["grado_clave"])
    esp["cabeza"] = _cabeza(d, sublinea)
    esp["rosca_serie"], esp["rosca_largo"] = _rosca(d)
    esp["vehiculo"] = _vehiculo(d)

    # Se retiran numeros de parte, normas y grados antes de buscar medidas:
    # 6Y0846, F-436 y CL10.9 se leerian como diametros.
    limpia = _OEM.sub(" ", d)
    limpia = _REF_SATA.sub(" ", limpia)
    limpia = _quitar_ruido(limpia)
    limpia = re.sub(r"\bCL(?:ASE)?\s*\d{1,2}(?:[.,]\d)?\b", " ", limpia)
    limpia = re.sub(r"\b(?:4|5|6|8|10|12|13|14)[.,](?:6|8|9)\b", " ", limpia)
    limpia = re.sub(r"\bG(?:R|RA|RADO)?\.?\s*\d\b|\bB7\b", " ", limpia)

    sistema = detectar_sistema(limpia)
    if sistema == "metrico":
        med = _medidas_metricas(limpia)
    elif sistema == "pulgadas":
        med = _medidas_pulgadas(limpia)
    else:
        # Sin pistas: se acepta metrico solo si el diametro es de la serie ISO.
        med = _medidas_metricas(limpia, exigir_normalizado=True)
        if med:
            sistema = "metrico"
        else:
            med = _medidas_pulgadas(limpia)
            sistema = "pulgadas" if med else None

    esp["sistema"] = sistema
    if sistema == "metrico" and med.get("dia"):
        dia = med["dia"]
        esp["diametro"] = f"M{dia:g}" if roscado else f"{dia:g} mm"
        esp["diametro_orden"] = dia
        if med.get("largo"):
            esp["largo"] = f"{med['largo']:g} mm"
            esp["largo_orden"] = med["largo"]
        if med.get("paso"):
            esp["paso"] = f"{med['paso']:g} mm"
            if med.get("paso2") and med["paso2"] != med["paso"]:
                esp["paso"] = f"{med['paso']:g} / {med['paso2']:g} mm"
    elif sistema == "pulgadas" and med.get("dia_txt"):
        esp["diametro"] = med["dia_txt"]
        esp["diametro_orden"] = round(med["dia_pulg"] * 25.4, 2)
        if med.get("largo_txt"):
            esp["largo"] = med["largo_txt"]
            esp["largo_orden"] = round(med["largo_pulg"] * 25.4, 2)

    if esp["diametro"] and esp["largo"]:
        esp["medida"] = f"{esp['diametro']} × {esp['largo']}"
    elif esp["diametro"]:
        esp["medida"] = esp["diametro"]

    return esp


def _grado_en_frase(grado):
    if grado.startswith(("Clase", "Grado")):
        return grado[0].lower() + grado[1:]
    if grado.startswith("Inoxidable"):
        return "acero inoxidable A2"
    return grado


def nombre_comercial(base, esp):
    """'Tornillo hexagonal' + specs -> 'Tornillo hexagonal M16 × 120 mm, clase 10.9, rosca parcial'"""
    partes = [base]
    if esp.get("medida"):
        partes.append(esp["medida"])
    cola = []
    if esp.get("grado"):
        cola.append(_grado_en_frase(esp["grado"]))
    if esp.get("rosca_largo"):
        cola.append(f"rosca {esp['rosca_largo'].lower()}")
    serie = esp.get("rosca_serie")
    if serie == "UNF (fina)":
        cola.append("rosca fina UNF")
    elif serie == "Paso fino":
        cola.append("paso fino")
    nombre = " ".join(partes)
    if cola:
        nombre += ", " + ", ".join(cola)
    return nombre
