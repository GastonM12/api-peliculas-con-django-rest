from django.urls import path,include
from rest_framework_simplejwt.views import TokenObtainPairView,TokenRefreshView
from rest_framework.routers import DefaultRouter
from user.views import RateViews
app_name = "user"

router = DefaultRouter()
router.register(r"rate",RateViews,basename="rate")
#Estas son las vistas que necesitamos para obtener el token para JWT
urlpatterns = [
path("token/",TokenObtainPairView.as_view(),name=("token_obtain_pair")),
path("token/refresh",TokenRefreshView.as_view(),name=("token_refresh")),
path("",include(router.urls))
]