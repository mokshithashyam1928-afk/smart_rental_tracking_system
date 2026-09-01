"""
Recommendations views (Phase 2) for asset reallocations.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from common.permissions import CanViewAnalytics, CanManageRentals
from common.responses import APIResponse
from apps.forecasting.models import Recommendation
from .serializers import (
    RecommendationSerializer,
    RecommendationActionSerializer,
    RecommendationGenerateSerializer
)
from .services import RecommendationService


class RecommendationViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for reviewing and acting on asset reallocation recommendations."""
    queryset = Recommendation.objects.select_related(
        'equipment', 'source_site', 'target_site'
    ).all()
    serializer_class = RecommendationSerializer
    permission_classes = [IsAuthenticated, CanViewAnalytics]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['status', 'equipment', 'source_site', 'target_site']
    ordering_fields = ['score', 'created_at', 'predicted_target_demand']
    ordering = ['-score', '-created_at']

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, CanManageRentals])
    def accept(self, request, pk=None):
        """Accept a reallocation recommendation and execute asset transfer."""
        serializer = RecommendationActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        notes = serializer.validated_data.get('notes', '')

        try:
            rec = RecommendationService.accept_recommendation(
                recommendation_id=pk,
                user=request.user,
                notes=notes
            )
            return APIResponse.success(
                data=RecommendationSerializer(rec).data,
                message=f'Recommendation accepted. Asset {rec.equipment.equipment_id} successfully reallocated to {rec.target_site.name}.'
            )
        except Recommendation.DoesNotExist:
            return APIResponse.error(
                code='NOT_FOUND',
                message='Recommendation not found',
                status_code=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, CanManageRentals])
    def dismiss(self, request, pk=None):
        """Dismiss a recommendation."""
        serializer = RecommendationActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        notes = serializer.validated_data.get('notes', '')

        try:
            rec = RecommendationService.dismiss_recommendation(
                recommendation_id=pk,
                user=request.user,
                notes=notes
            )
            return APIResponse.success(
                data=RecommendationSerializer(rec).data,
                message='Recommendation dismissed successfully.'
            )
        except Recommendation.DoesNotExist:
            return APIResponse.error(
                code='NOT_FOUND',
                message='Recommendation not found',
                status_code=status.HTTP_404_NOT_FOUND
            )

    @action(detail=False, methods=['post'])
    def generate(self, request):
        """Trigger generation of new smart asset reallocation recommendations."""
        recs = RecommendationService.generate_recommendations()
        return APIResponse.success(
            data=RecommendationSerializer(recs, many=True).data,
            message=f'Generated {len(recs)} optimization recommendations.'
        )
