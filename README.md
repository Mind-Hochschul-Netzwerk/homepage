# Website für das Mind-Hochschul-Netzwerk

Die Website wird auf Basis von [Wagtail](https://wagtail.org/) entwickelt.

## Entwicklungsstand

- Es gibt einen Docker-Container mit der Wagtail-Instanz, der sich in die bestehende Umgebung von Traefik, Authelia und LDAP integriert.
- Jeder Aufruf der Wagtail-Site triggert eine Authentifizierung gegen Authelia.
- Username und Gruppen bekommt Wagtail von Authelia.

## Todos

- Design, Struktur und Inhalte einbauen
- URLs anpassen
