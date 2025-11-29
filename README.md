<p align="center">
  <img src="https://i.imgur.com/OphYJsE.png" width="100%" alt="Banner Proyecto Integrador 2025">
</p>

![Python](https://custom-icon-badges.demolab.com/badge/Python-3.11-3776AB.svg?logo=python&logoColor=white)
![Django](https://custom-icon-badges.demolab.com/badge/Django-5.2-092E20.svg?logo=django&logoColor=white)
![SQLite](https://custom-icon-badges.demolab.com/badge/SQLite-Database-07405E.svg?logo=sqlite&logoColor=white)
![Bootstrap](https://custom-icon-badges.demolab.com/badge/Bootstrap-UI-7952B3.svg?logo=bootstrap&logoColor=white)
![GitHub](https://custom-icon-badges.demolab.com/badge/Repo-GitHub-181717.svg?logo=github&logoColor=white)
![License](https://custom-icon-badges.demolab.com/badge/License-MIT-FFCC00.svg?logo=law&logoColor=black)
![Status](https://custom-icon-badges.demolab.com/badge/Status-Activo-28A745.svg?logo=check-circle&logoColor=white)
![Version](https://custom-icon-badges.demolab.com/badge/Version-1.0.0-007BFF.svg?logo=tag&logoColor=white)
![Tests](https://custom-icon-badges.demolab.com/badge/Tests-Pasados-17A2B8.svg?logo=checklist&logoColor=white)
![Contribuidores](https://custom-icon-badges.demolab.com/badge/Contribuidores-1-6F42C1.svg?logo=people&logoColor=white)
![Entorno](https://custom-icon-badges.demolab.com/badge/Entorno-Produccion-FD7E14.svg?logo=gear&logoColor=white)


<p align="center">
  <img src="https://i.imgur.com/RVGaecC.png" width="100%" alt="Banner Proyecto Integrador 2025">
</p>

**Trust AI** es un modelo educativo diseñado para simular el comportamiento ofensivo de una IA sin filtros mediante técnicas de jailbreak, con el objetivo de estudiar riesgos, comprender vulnerabilidades en modelos de lenguaje y fortalecer defensas.
El proyecto está pensado exclusivamente para entornos controlados, laboratorios privados, investigación académica y concientización en ciberseguridad.

> ⚠️ Trust AI puede generar código malicioso educativo únicamente en formato simulado, incompleto y NO funcional.
> Esto sirve para enseñar conceptos ofensivos sin ejecutar acciones reales.
> Trust AI no contiene malware operativo, no se propaga, no ataca sistemas y no genera daño real.


 **💻 PAGINA WEB INFORMATIVA : SOON**
 
<p align="center">
  <img src="https://i.imgur.com/zDTIHyR.png" width="100%" alt="Banner Proyecto Integrador 2025">
</p>








# 📌 Características principales

- Simulación de respuestas ofensivas mediante jailbreaks

- Generación de código malicioso educativo desarmado (pseudocódigo, ejemplos no ejecutables)

- Comportamiento controlado y sin capacidad operativa

- Ideal para estudiar riesgos y bypasses en modelos de IA

- Útil para entrenar defensas, filtros y sistemas de seguridad en LLMs

- Seguro para uso académico o laboratorios locales




<p align="center">
  <img src="https://i.imgur.com/zDTIHyR.png" width="100%" alt="Banner Proyecto Integrador 2025">
</p>



# 🎯 Objetivo del proyecto

- El propósito de Trust AI es demostrar, educar y analizar cómo podría comportarse una IA sin filtros, permitiendo:

- comprender técnicas de bypass y jailbreak,

- observar ejemplos educativos de código ofensivo NO real,

- mejorar defensas y capas de seguridad en aplicaciones basadas en IA,

- entrenar a estudiantes en pensamiento ofensivo seguro,

- analizar riesgos emergentes en IA.


<p align="center">
  <img src="https://i.imgur.com/zDTIHyR.png" width="100%" alt="Banner Proyecto Integrador 2025">
</p>






# 🔒 Ética y uso responsable

> Este proyecto fue creado con responsabilidad y propósito educativo.
> No debe usarse fuera de laboratorios controlados ni con fines ofensivos reales.

**El autor no se responsabiliza por usos indebidos.
Trust AI es un proyecto educativo, seguro y no operativo.**



<p align="center">
  <img src="https://i.imgur.com/zDTIHyR.png" width="100%" alt="Banner Proyecto Integrador 2025">
</p>







## 🔸 Características clave
- **Autenticación personalizada:** inicio de sesión por correo electrónico, registro con perfil completo, edición de avatar y datos biográficos.
- **Panel inteligente:** métricas rápidas, historial anclado, acceso a plantillas y navegación fluida hacia nuevas sesiones.
- **Gestor de chats:** creación guiada en pasos con selección de estilo, modelo DeepSeek (`deepseek-chat`, `deepseek-coder`, `deepseek-reasoner`) y título.
- **Plantillas de estilo ocultas:** prompts de sistema almacenados en BD, inyectados automáticamente sin exponerlos al usuario final.
- **Integración DeepSeek:** cliente robusto con manejo de errores, trazabilidad de tokens y respuesta asincrónica en la interfaz.
- **UI responsive:** landing pública, vistas internas y formularios tematizados en rojo, negro y gris.


<p align="center">
  <img src="https://i.imgur.com/zDTIHyR.png" width="100%" alt="Banner Proyecto Integrador 2025">
</p>


## 📑 Requisitos
- Python 3.11 (o compatible con Django 5.2.7)
- Dependencias del proyecto (instalables con pip):
  ```bash
  pip install -r requirements.txt
  ```
  - `Django==5.2.7`
  - `requests` (cliente HTTP para la API)
  - `Pillow` (manejo de avatares en `ImageField`)
 

<p align="center">
  <img src="https://i.imgur.com/zDTIHyR.png" width="100%" alt="Banner Proyecto Integrador 2025">
</p>


## ⚙️ Configuración rápida
1. **Clonar y crear entorno:**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   source .venv/bin/activate  # macOS/Linux
   pip install -r requirements.txt
   ```





2. **Variables de entorno:**
   - `DEEPSEEK_API_KEY`: clave privada del panel de DeepSeek.
   - Opcional: `CSRF_TRUSTED_ORIGINS` separado por comas para exponer dominios adicionales en producción.

   En PowerShell:
   ```powershell
   setx DEEPSEEK_API_KEY "tu_clave_super_secreta"
   ```






3. **Migraciones y datos base:**
   ```bash
   python manage.py migrate
   python manage.py createsuperuser  # opcional para administrar estilos desde /admin/
   ```
   Las plantillas de estilo iniciales se cargan automáticamente mediante la migración `chat/0002_default_styles.py`.








4. **Levantar el servidor:**
   ```bash
   python manage.py runserver
   ```
   - Landing pública: `http://127.0.0.1:8000/`
   - Panel autenticado: `http://127.0.0.1:8000/app/`







<p align="center">
  <img src="https://i.imgur.com/zDTIHyR.png" width="100%" alt="Banner Proyecto Integrador 2025">
</p>


## 🧱 Estructura principal
- `accounts/`: modelo de usuario (`AUTH_USER_MODEL`), formularios, vistas y autenticación por email.
- `chat/`: modelos de plantillas, sesiones y mensajes; vistas para dashboard, historial y AJAX; cliente DeepSeek.
- `pages/`: landing page pública con branding **TRUST** en rojo.
- `templates/` y `static/`: layouts, componentes y estilos en paleta rojo/negro/gris.




<p align="center">
  <img src="https://i.imgur.com/zDTIHyR.png" width="100%" alt="Banner Proyecto Integrador 2025">
</p>


## 💡 Comprobaciones recomendadas
- Verificar dependencias: `pip install -r requirements.txt`
- Diagnóstico de Django: `python manage.py check`
- Pruebas de flujos:
  1. Registro de usuario (landing → “Crear cuenta”).
  2. Inicio de sesión y navegación al dashboard en `/app/`.
  3. Creación de chat con los tres pasos y envío de mensajes (requiere `DEEPSEEK_API_KEY` válido y conectividad).
  4. Edición de perfil y recarga de avatar para validar `Pillow`.





<p align="center">
  <img src="https://i.imgur.com/zDTIHyR.png" width="100%" alt="Banner Proyecto Integrador 2025">
</p>





























# 📜 Licencia

MIT License + cláusula educativa:

“La funcionalidad ofensiva generada por Trust AI es solo simulación educativa.
No debe modificarse para causar daño real.”

<p align="center">
  <img src="https://i.imgur.com/zDTIHyR.png" width="100%" alt="Banner Proyecto Integrador 2025">
</p>


# ⭐ Apoyá el proyecto

> Si este proyecto te sirve, te interesa o querés que siga creciendo, podés apoyarlo de forma muy simple:

**Dejá una estrella ⭐ en GitHub**

**Seguime** para ver futuros proyectos y actualizaciones
👉 **[github.com/cromop1](https://github.com/cromop1)**

Tu apoyo ayuda a que pueda seguir desarrollando herramientas educativas, simulaciones seguras y contenido para la comunidad.


