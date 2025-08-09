[readme_crear_api_con_django_y_django_rest_framework.md](https://github.com/user-attachments/files/21702332/readme_crear_api_con_django_y_django_rest_framework.md)
# Movie API — Guía paso a paso (Django + Django REST Framework)

Este README explica, paso a paso, cómo crear una API REST con **Django** y **Django REST Framework (DRF)**. Incluye configuración del proyecto, modelos, serializadores, vistas, rutas, documentación con **drf-yasg** (Swagger) y autenticación JWT (SimpleJWT).

> Esta guía está pensada para reproducir la estructura y las funcionalidades básicas de la API de ejemplo (películas + calificaciones). Está en español y es práctica — podés copiar/pegar los fragmentos.

---

## Requisitos previos

- Python 3.8+ (recomendado 3.11)
- pip o conda
- Git (opcional)

Instalá las dependencias en un entorno virtual:

```bash
python -m venv .venv
source .venv/bin/activate   # Linux / macOS
.venv\Scripts\activate     # Windows (PowerShell o cmd)

pip install --upgrade pip
pip install django djangorestframework drf-yasg djangorestframework-simplejwt
```

(Agregá `psycopg2-binary` si usás PostgreSQL u otras dependencias según tu DB.)

---

## 1. Crear proyecto y apps

```bash
django-admin startproject movies_api .
python manage.py startapp movie
python manage.py startapp user
```

---

## 2. Configurar `settings.py`

En `movies_api/settings.py`:

- Agregar apps a `INSTALLED_APPS`:

```py
INSTALLED_APPS = [
    # apps Django
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # terceros
    'rest_framework',
    'drf_yasg',

    # tuyos
    'movie',
    'user',
]
```

- Configurar DRF (ejemplo mínimo y JWT):

```py
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
}
```

- (Opcional) Si vas a usar modelo de usuario personalizado, definí `AUTH_USER_MODEL` **antes** de hacer migraciones.

---

## 3. Modelos (ejemplos)

`movie/models.py` (ejemplo `Movies`):

```py
from django.db import models

class Movies(models.Model):
    titulo = models.CharField(max_length=200)
    release_date = models.DateField()
    duration = models.IntegerField(help_text='Duración en minutos')
    synopsis = models.TextField(blank=True)

    def __str__(self):
        return self.titulo
```

`user/models.py` (ejemplo `RateMovie`):

```py
from django.db import models
from django.conf import settings
from movie.models import Movies

class RateMovie(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movies, on_delete=models.CASCADE)
    rating = models.IntegerField()  # validar entre 1 y 5 en serializer
    comment = models.CharField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.movie} ({self.rating})"
```

---

## 4. Serializers

`movie/serializers.py`:

```py
from rest_framework import serializers
from movie.models import Movies

class MovieModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movies
        fields = '__all__'
```

`user/serializers.py`:

```py
from rest_framework import serializers
from user.models import RateMovie

class RateMovieSerializer(serializers.ModelSerializer):
    # user read_only porque se asigna desde request.user
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = RateMovie
        fields = ['id', 'user', 'movie', 'rating', 'comment', 'created_at']
```

> Nota: si en algún punto usás `serializers.Serializer` y llamás `.save()` sin implementar `create()` / `update()`, aparecerá `NotImplementedError`. Para persistir modelos usá `ModelSerializer` o implementá `create()`.

---

## 5. Vistas

Ejemplo `movie/views.py` con `APIView`:

```py
from drf_yasg.utils import swagger_auto_schema
from rest_framework.views import APIView
from rest_framework.response import Response
from movie.models import Movies
from movie.serializers import MovieModelSerializer
from rest_framework import status

class MoviesView(APIView):

    @swagger_auto_schema(responses={200: MovieModelSerializer(many=True)})
    def get(self, request):
        movies = Movies.objects.all()
        serializer = MovieModelSerializer(movies, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(request_body=MovieModelSerializer, responses={201: MovieModelSerializer})
    def post(self, request):
        serializer = MovieModelSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(request_body=MovieModelSerializer)
    def put(self, request, pk=None):
        try:
            movie = Movies.objects.get(pk=pk)
        except Movies.DoesNotExist:
            return Response({'detail': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = MovieModelSerializer(movie, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
```

Ejemplo `user/views.py` con `ViewSet` (calificaciones):

```py
from drf_yasg.utils import swagger_auto_schema
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from user.models import RateMovie
from user.serializers import RateMovieSerializer
from rest_framework import status

class RateViews(ViewSet):
    serializer_class = RateMovieSerializer

    def list(self, request):
        user_rates = RateMovie.objects.filter(user_id=request.user.id)
        serializer = RateMovieSerializer(user_rates, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(request_body=RateMovieSerializer)
    def create(self, request):
        # asignar user autenticado (no confiar en el body)
        serializer = RateMovieSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
```

---

## 6. URLs y Swagger (documentación)

Archivo principal `movies_api/urls.py`:

```py
from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="Movie API",
        default_version='v1',
        description="API de ejemplo con Django + DRF",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='swagger-ui'),
    path('admin/', admin.site.urls),
    path('movie/', include('movie.urls')),
    path('user/', include('user.urls')),
]
```

`movie/urls.py`:

```py
from django.urls import path
from movie.views import MoviesView

app_name = 'movie'

urlpatterns = [
    path('', MoviesView.as_view(), name='movies'),
    path('<int:pk>/', MoviesView.as_view(), name='movie-detail'),
]
```

`user/urls.py` (ViewSet + JWT):

```py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from user.views import RateViews
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

router = DefaultRouter()
router.register(r'rates', RateViews, basename='rates')

urlpatterns = [
    path('', include(router.urls)),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
```

> Si querés que Swagger muestre mejor la documentación del endpoint `/user/token/` podés crear una clase que extienda `TokenObtainPairView` y usar `@swagger_auto_schema` para documentar `request_body` y `responses`.

---

## 7. Migraciones, superuser y runserver

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Abrí `http://127.0.0.1:8000/swagger/` para ver la documentación.

---

## 8. Ejemplos de requests (curl)

Obtener lista de películas:

```bash
curl -X GET http://127.0.0.1:8000/movie/
```

Crear película (POST):

```bash
curl -X POST http://127.0.0.1:8000/movie/ \
 -H "Content-Type: application/json" \
 -d '{"titulo":"Mi peli","release_date":"2025-01-01","duration":120,"synopsis":"..."}'
```

Obtener token (JWT):

```bash
curl -X POST http://127.0.0.1:8000/user/token/ \
 -H "Content-Type: application/json" \
 -d '{"username":"admin","password":"tu_password"}'
```

Usar token en header `Authorization: Bearer <access_token>` para endpoints protegidos.

Crear calificación (ejemplo):

```bash
curl -X POST http://127.0.0.1:8000/user/rates/ \
 -H "Content-Type: application/json" \
 -H "Authorization: Bearer <access_token>" \
 -d '{"movie": 1, "rating": 5, "comment": "Muy buena"}'
```

---

## 9. Errores comunes y soluciones rápidas

- `` → Estás usando `request.data(...)` en vez de `request.data.get(...)` o `request.data['campo']`.
- `` → Estás usando `serializers.Serializer` y llamás `.save()`; implementá `create()` o usá `ModelSerializer`.
- **Views basadas en ViewSet no responden POST** → Si usás `ViewSet`, registralo con un `router` (DefaultRouter) en `urls.py`.
- **Swagger no muestra endpoints** → Verificá que las URLs estén registradas en el `urlpatterns` del proyecto y que el schema\_view incluya las apps (normalmente con `include(...)`).
- **JWT endpoints no documentados** → Extendé `TokenObtainPairView` y agregá `@swagger_auto_schema` para documentar `request_body` y `responses`.

---

## 10. Buenas prácticas y siguientes pasos

- Usá `ModelSerializer` siempre que representes modelos.
- Validá rangos (p. ej. rating entre 1 y 5) dentro del serializer (`validate_rating`).
- Agregá versionado de la API (`/api/v1/...`) si la API va a crecer.
- Escribí tests con `rest_framework.test.APITestCase`.
- Considerá dockerizar y crear un `docker-compose` para reproducibilidad.

---

## Licencia y autor

Esta guía es libre para uso y modificación. Si querés, adapto el README con ejemplos reales de tu proyecto (rutas exactas, nombres de modelos, etc.).

---

¿Querés que genere también un `README.md` esp
