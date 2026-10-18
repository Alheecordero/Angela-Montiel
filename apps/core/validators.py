"""Validadores de marca aplicados a los textos visibles del sitio.

Reglas del capítulo 2.1 de las especificaciones. Se usan en los modelos para
que el gestor de contenidos rechace textos que incumplen las reglas antes de
publicarlos.
"""

import re

from django.core.exceptions import ValidationError

PATRON_ANGELA_SIN_TILDE = re.compile(r"\bAngela\b")
PATRON_CORCHETES = re.compile(r"\[[^\]]*\]")
PATRON_INICIA_LEGAL = re.compile(r"inicia\s*legal", re.IGNORECASE)


def sin_dos_puntos(value):
    if value and ":" in str(value):
        raise ValidationError(
            "Ningún texto visible del sitio usa dos puntos. Reescribe la frase sin ese signo.",
            code="dos_puntos",
        )


def angela_con_tilde(value):
    if value and PATRON_ANGELA_SIN_TILDE.search(str(value)):
        raise ValidationError(
            "El nombre siempre se escribe Ángela, con tilde.",
            code="angela_sin_tilde",
        )


def sin_corchetes(value):
    if value and PATRON_CORCHETES.search(str(value)):
        raise ValidationError(
            "Los textos entre corchetes son espacios del prototipo y no deben publicarse.",
            code="corchetes",
        )


def sin_inicia_legal(value):
    if value and PATRON_INICIA_LEGAL.search(str(value)):
        raise ValidationError(
            "El sitio no puede mencionar ni enlazar a Inicia Legal.",
            code="inicia_legal",
        )


TEXTO_VISIBLE = [sin_dos_puntos, angela_con_tilde, sin_corchetes, sin_inicia_legal]
"""Conjunto para títulos, bajadas, etiquetas, botones y textos cortos."""

TEXTO_LARGO = [angela_con_tilde, sin_corchetes, sin_inicia_legal]
"""Conjunto para cuerpos de texto enriquecido, donde los dos puntos se revisan
con el comando revisar_sitio porque pueden aparecer dentro de citas legales."""
