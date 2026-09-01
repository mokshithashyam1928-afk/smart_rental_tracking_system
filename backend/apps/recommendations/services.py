"""
Recommendations service for generating and acting on smart asset reallocations.
"""
from django.utils import timezone
from apps.equipment.models import Equipment
from apps.sites.models import Site
from apps.forecasting.models import Forecast, Recommendation
from apps.audit.models import AuditLog


class RecommendationService:
    """Service to generate and process equipment reallocation recommendations."""

    @staticmethod
    def generate_recommendations():
        """
        Identify sites with underutilized surplus machinery and pair with sites having higher forecast demand.
        """
        now = timezone.now()
        generated = []
        sites = list(Site.objects.filter(status='ACTIVE'))

        if len(sites) < 2:
            return generated

        # Find underutilized equipment (status AVAILABLE or IDLE at their current site)
        surplus_equipment = Equipment.objects.filter(
            status__in=[Equipment.STATUS_AVAILABLE, Equipment.STATUS_IDLE],
            site__isnull=False
        ).select_related('site')

        for eq in surplus_equipment:
            source_site = eq.site
            # Query recent forecast demand at other sites for this equipment type
            target_forecasts = Forecast.objects.filter(
                equipment_type=eq.equipment_type
            ).exclude(site=source_site).order_by('-predicted_demand')

            target_forecast = target_forecasts.first()
            if target_forecast and target_forecast.predicted_demand > 2.0:
                target_site = target_forecast.site

                # Check if an existing pending recommendation for this equipment already exists
                existing = Recommendation.objects.filter(
                    equipment=eq,
                    target_site=target_site,
                    status=Recommendation.STATUS_PENDING
                ).first()

                if not existing:
                    # Calculate recommendation score (0.0 - 1.0)
                    score = min(0.95, round(0.50 + (target_forecast.predicted_demand * 0.08), 2))
                    reason = (
                        f"Asset {eq.equipment_id} ({eq.equipment_type}) is currently {eq.status} at {source_site.name}. "
                        f"Forecast model predicts surge in demand ({target_forecast.predicted_demand:.1f} units) at {target_site.name}."
                    )
                    rec = Recommendation.objects.create(
                        equipment=eq,
                        source_site=source_site,
                        target_site=target_site,
                        reason=reason,
                        current_utilization=0.0,
                        predicted_target_demand=target_forecast.predicted_demand,
                        score=score,
                        status=Recommendation.STATUS_PENDING
                    )
                    generated.append(rec)

        return generated

    @staticmethod
    def accept_recommendation(recommendation_id, user, notes=''):
        """Accept recommendation: moves equipment to target site and marks status ACCEPTED."""
        rec = Recommendation.objects.get(id=recommendation_id)
        rec.status = Recommendation.STATUS_ACCEPTED
        rec.acted_at = timezone.now()
        rec.acted_by = getattr(user, 'email', str(user))
        rec.save()

        # Reassign equipment to target site
        eq = rec.equipment
        old_site = eq.site
        eq.site = rec.target_site
        eq.save()

        if user and getattr(user, 'is_authenticated', False):
            AuditLog.objects.create(
                actor=user,
                action=AuditLog.ACTION_UPDATE,
                entity_type='Recommendation',
                entity_id=rec.id,
                metadata={
                    'equipment_id': eq.equipment_id,
                    'old_site': old_site.name if old_site else None,
                    'new_site': rec.target_site.name,
                    'notes': notes,
                    'action': 'ACCEPT'
                }
            )
        return rec

    @staticmethod
    def dismiss_recommendation(recommendation_id, user, notes=''):
        """Dismiss a recommendation."""
        rec = Recommendation.objects.get(id=recommendation_id)
        rec.status = Recommendation.STATUS_DISMISSED
        rec.acted_at = timezone.now()
        rec.acted_by = getattr(user, 'email', str(user))
        rec.save()

        if user and getattr(user, 'is_authenticated', False):
            AuditLog.objects.create(
                actor=user,
                action=AuditLog.ACTION_UPDATE,
                entity_type='Recommendation',
                entity_id=rec.id,
                metadata={'equipment_id': rec.equipment.equipment_id, 'notes': notes, 'action': 'DISMISS'}
            )
        return rec
