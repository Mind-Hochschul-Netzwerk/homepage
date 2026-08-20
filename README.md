# Website für das Mind-Hochschul-Netzwerk

Die Website wird auf Basis von [Wagtail](https://wagtail.org/) entwickelt.

## Entwicklungsstand

- Es gibt einen Docker-Container mit der Wagtail-Instanz, der sich in die bestehende Umgebung von Traefik, Authelia und LDAP integriert.
- Die Pfade `/admin/` und `/django-admin/` der Wagtail-Site triggern eine Authentifizierung gegen Authelia.
- Username und Gruppen bekommt Wagtail von Authelia.
- LDAP-Gruppen werden auf Wagtail-/Django-Rechte abgebildet: `webredaktion` → Wagtail-Gruppe "Editors", `webadmin` → `is_staff`/`is_superuser` (voller Zugriff inkl. `/django-admin/`). Andere LDAP-Gruppen werden ignoriert.

## Todos

- Design, Struktur und Inhalte einbauen.
