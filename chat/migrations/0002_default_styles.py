from django.db import migrations


def seed_styles(apps, schema_editor):
    StyleTemplate = apps.get_model("chat", "StyleTemplate")
    templates = [
        {
            "name": "asistente_creativo",
            "title": "Asistente Creativo",
            "description": "Perfecto para escritura y generación de ideas innovadoras.",
            "system_prompt": (
                "Eres un escritor creativo profesional. Responde con imaginación, metáforas y pensamiento lateral. "
                "Sé original en cada respuesta."
            ),
        },
        {
            "name": "analista_tecnico",
            "title": "Analista Técnico",
            "description": "Enfoque lógico y estructurado para problemas complejos.",
            "system_prompt": (
                "Eres un ingeniero de sistemas. Analiza todo de forma metódica. Usa razonamiento lógico, estructura "
                "jerárquica y evita divagaciones."
            ),
        },
        {
            "name": "mentor_producto",
            "title": "Mentor de Producto",
            "description": "Ayuda a definir estrategias de producto y priorización.",
            "system_prompt": (
                "Actúas como mentor senior de producto. Haz preguntas aclaratorias, prioriza impacto de negocio y "
                "propone roadmaps accionables."
            ),
        },
    ]

    for template in templates:
        StyleTemplate.objects.get_or_create(name=template["name"], defaults=template)


def unseed_styles(apps, schema_editor):
    StyleTemplate = apps.get_model("chat", "StyleTemplate")
    StyleTemplate.objects.filter(name__in=["asistente_creativo", "analista_tecnico", "mentor_producto"]).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("chat", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_styles, unseed_styles),
    ]
