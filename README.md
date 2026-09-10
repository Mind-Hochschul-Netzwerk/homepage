# Website für das Mind-Hochschul-Netzwerk

Die Website wird auf Basis von [Wagtail](https://wagtail.org/) entwickelt.

## Entwicklungsstand

- Es gibt einen Docker-Container mit der Wagtail-Instanz, der sich in die bestehende Umgebung von Traefik, Authelia und LDAP integriert.
- Die Pfade `/admin/` und `/django-admin/` der Wagtail-Site triggern eine Authentifizierung gegen Authelia.
- Username und Gruppen bekommt Wagtail von Authelia.
- Es gibt eine lokale Entwicklungsinstanz mit Superuser "admin", Passwort "GeheimesPasswort"
- Tailwind starten mit `npx @tailwindcss/cli -i ./src/input.css -o ./mhnsite/static/css/mhnsite.css --watch`

## Todos

- Design, Struktur und Inhalte einbauen.
- Gruppen aus LDAP auf Admin- bzw. Redaktions-Rechte in Wagtail abbilden.
- HomePage umbenennen zu MHNPage
- Veranstaltungen als Typ implementieren

## Lokale Instanz starten

- Git-Repo `website` auschecken
- `cd mhnsite`
- `uv run python manage.py migrate`
- `uv run python manage.py runserver`
- <http://127.0.0.1:8000/admin/> aufrufen
