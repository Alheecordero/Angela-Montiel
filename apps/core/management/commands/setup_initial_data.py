from django.core.management.base import BaseCommand

from apps.core.models import AboutSection, SiteSettings


class Command(BaseCommand):
    help = "Crea datos iniciales del sitio para Angela Montiel"

    def handle(self, *args, **options):
        SiteSettings.objects.update_or_create(
            pk=1,
            defaults={
                "site_name": "Angela Montiel",
                "tagline": "Abogada · Santiago, Chile",
                "hero_title": "Estrategia legal para negocios que quieren crecer con respaldo",
                "hero_subtitle": (
                    "Asesoría jurídica clara y personalizada para empresas, emprendedores y marcas "
                    "que necesitan seguridad legal para avanzar con confianza."
                ),
                "hero_cta_text": "Agendar una reunión",
                "hero_cta_url": "/contacto/",
                "email": "contacto@angelamontiel.cl",
                "phone": "+56 9 0000 0000",
                "city": "Santiago, Chile",
                "footer_text": (
                    "Abogada en Chile. Asesoría legal profesional y contenido de interés jurídico."
                ),
                "meta_description": (
                    "Angela Montiel, abogada en Chile. Asesoría legal, artículos y videos de interés jurídico."
                ),
            },
        )

        AboutSection.objects.update_or_create(
            pk=1,
            defaults={
                "headline": "Sobre mí",
                "bio": (
                    "Soy abogada con experiencia en el ejercicio profesional en Chile, "
                    "comprometida con brindar asesoría legal clara, ética y orientada a las "
                    "necesidades de cada cliente. Mi objetivo es acompañar a las personas en "
                    "sus procesos jurídicos con profesionalismo y cercanía."
                ),
                "university": "Universidad de Chile",
                "bar_association": "Colegio de Abogados de Chile",
                "specialties": "Asesoría corporativa, Contratos, E-commerce, Protección de datos, Propiedad intelectual",
                "years_experience": 10,
            },
        )

        self.stdout.write(self.style.SUCCESS("Datos iniciales creados correctamente."))
