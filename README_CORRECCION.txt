Corrección aplicada:
- Se corrigió la descarga del GeoJSON municipal de México.
- Antes intentaba URLs inexistentes que devolvían HTTP 404.
- Ahora usa MunicipiosMexico.json del repositorio angelnmara/geojson.

Uso:
1. Copia app.py dentro de C:\Users\EQUIPO\Desktop\Web Vales\
2. Ejecuta: streamlit run app.py

Nota:
El GeoJSON municipal pesa aprox. 34 MB. La primera carga puede tardar.
El script lo guardará como mexico_municipios.geojson en tu carpeta Web Vales.
