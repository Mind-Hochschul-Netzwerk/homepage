# Website für das Mind-Hochschul-Netzwerk

Die Website wird auf Basis von [Wagtail](https://wagtail.org/) entwickelt.

## Entwicklungsstand

- Es gibt einen Docker-Container mit der Wagtail-Instanz, der sich in die bestehende Umgebung von Traefik, Authelia und LDAP integriert.
- Die Pfade `/admin/` und `/django-admin/` der Wagtail-Site triggern eine Authentifizierung gegen Authelia.
- Username und Gruppen bekommt Wagtail von Authelia.
- Es gibt eine lokale Entwicklungsinstanz mit Superuser "admin", Passwort "adminweb"
- Tailwind starten mit `npx @tailwindcss/cli -i ./src/input.css -o ./mhnsite/static/css/mhnsite.css --watch`

## Todos

- Design, Struktur und Inhalte einbauen.
- Gruppen aus LDAP auf Admin- bzw. Redaktions-Rechte in Wagtail abbilden.
- HomePage umbenennen zu MHNPage
- Veranstaltungen als Typ implementieren
