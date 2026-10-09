# Sismos México — versión estática (GitHub Pages)

Misma interfaz del sistema original (`vista.html` + `std`, `std2`, `std3`), sin PHP ni PostgreSQL.
- `docs/index.html`  → panel lateral (antes vista.html)
- `docs/std.html`    → sismos por año y magnitud (antes std.php)
- `docs/std2.html`   → población por entidad (antes std2.php)
- `docs/std3.html`   → economía por entidad (antes std3.php)
- `docs/datos/`      → datos exportados de las tablas del data warehouse (scripts: exportar2.py, build.py)

Publicar: Settings → Pages → Deploy from a branch → main → /docs.
