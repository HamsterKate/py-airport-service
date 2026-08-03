from rest_framework.routers import DefaultRouter

from airport.views import (
    AirplaneTypeViewSet,
    CrewViewSet,
    AirportViewSet,
    AirplaneViewSet,
    RouteViewSet,
    FlightViewSet,
    OrderViewSet,
)

router = DefaultRouter()

router.register("airplane-types", AirplaneTypeViewSet)
router.register("crews", CrewViewSet)
router.register("airports", AirportViewSet)
router.register("airplanes", AirplaneViewSet)
router.register("routes", RouteViewSet)
router.register("flights", FlightViewSet)
router.register("orders", OrderViewSet)

urlpatterns = router.urls
