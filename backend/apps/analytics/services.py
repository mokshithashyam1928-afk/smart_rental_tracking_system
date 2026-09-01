"""
Analytics service for calculating fleet metrics, idle statistics, fuel efficiency, and CSV exports.
"""
import csv
import io
from datetime import datetime, timedelta
from django.db.models import Sum, Avg, Count, Q
from django.utils import timezone
from apps.equipment.models import Equipment
from apps.telemetry.models import Telemetry, EquipmentLiveState
from apps.rentals.models import Rental
from apps.sites.models import Site


class AnalyticsService:
    """Service class for analytics calculations."""

    @staticmethod
    def get_fleet_utilization(start_date=None, end_date=None, site_id=None):
        """Calculate overall fleet utilization."""
        eq_qs = Equipment.objects.all()
        if site_id:
            eq_qs = eq_qs.filter(site_id=site_id)

        total_equipment = eq_qs.count()
        if total_equipment == 0:
            return {
                'total_equipment': 0,
                'in_use': 0,
                'idle': 0,
                'available': 0,
                'rented': 0,
                'maintenance': 0,
                'offline': 0,
                'utilization_rate': 0.0,
                'idle_rate': 0.0,
            }

        counts = eq_qs.aggregate(
            in_use=Count('id', filter=Q(status=Equipment.STATUS_IN_USE)),
            idle=Count('id', filter=Q(status=Equipment.STATUS_IDLE)),
            available=Count('id', filter=Q(status=Equipment.STATUS_AVAILABLE)),
            rented=Count('id', filter=Q(status=Equipment.STATUS_RENTED)),
            maintenance=Count('id', filter=Q(status=Equipment.STATUS_MAINTENANCE)),
            offline=Count('id', filter=Q(status=Equipment.STATUS_OFFLINE)),
        )

        in_use = counts['in_use'] or 0
        idle = counts['idle'] or 0
        available = counts['available'] or 0
        rented = counts['rented'] or 0
        maintenance = counts['maintenance'] or 0
        offline = counts['offline'] or 0

        active_productive = in_use + rented
        utilization_rate = round((active_productive / total_equipment) * 100, 2)
        idle_rate = round((idle / total_equipment) * 100, 2)

        return {
            'total_equipment': total_equipment,
            'in_use': in_use,
            'idle': idle,
            'available': available,
            'rented': rented,
            'maintenance': maintenance,
            'offline': offline,
            'utilization_rate': utilization_rate,
            'idle_rate': idle_rate,
        }

    @staticmethod
    def get_idle_analytics(start_date=None, end_date=None):
        """Calculate fleet idle hours, fuel wasted, and financial impact."""
        tel_qs = Telemetry.objects.all()
        if start_date:
            tel_qs = tel_qs.filter(timestamp__gte=start_date)
        if end_date:
            tel_qs = tel_qs.filter(timestamp__lte=end_date)

        agg = tel_qs.aggregate(
            total_engine=Sum('engine_hours'),
            total_idle=Sum('idle_hours')
        )

        # Fallback to LiveState if telemetry table aggregate is empty
        if not agg['total_engine']:
            live_agg = EquipmentLiveState.objects.aggregate(
                total_engine=Sum('engine_hours'),
                total_idle=Sum('idle_hours')
            )
            total_engine = float(live_agg['total_engine'] or 0.0)
            total_idle = float(live_agg['total_idle'] or 0.0)
        else:
            total_engine = float(agg['total_engine'] or 0.0)
            total_idle = float(agg['total_idle'] or 0.0)

        idle_pct = round((total_idle / total_engine * 100), 2) if total_engine > 0 else 0.0
        # Estimated idle fuel waste: ~3.5 Liters/hour of idle for heavy machinery
        fuel_wasted = round(total_idle * 3.5, 2)
        # Estimated diesel cost: $1.25 / Liter
        idle_cost = round(fuel_wasted * 1.25, 2)

        return {
            'total_engine_hours': round(total_engine, 2),
            'total_idle_hours': round(total_idle, 2),
            'idle_percentage': idle_pct,
            'estimated_fuel_wasted_liters': fuel_wasted,
            'idle_cost_estimate_usd': idle_cost,
        }

    @staticmethod
    def get_fuel_efficiency(start_date=None, end_date=None):
        """Calculate fuel efficiency overall and by equipment type."""
        tel_qs = Telemetry.objects.all()
        if start_date:
            tel_qs = tel_qs.filter(timestamp__gte=start_date)
        if end_date:
            tel_qs = tel_qs.filter(timestamp__lte=end_date)

        agg = tel_qs.aggregate(
            total_fuel=Sum('fuel_consumed'),
            total_engine=Sum('engine_hours')
        )

        total_fuel = float(agg['total_fuel'] or 0.0)
        total_engine = float(agg['total_engine'] or 0.0)
        avg_rate = round(total_fuel / total_engine, 2) if total_engine > 0 else 0.0

        by_type = {}
        for eq_type, label in Equipment.EQUIPMENT_TYPE_CHOICES:
            type_tel = tel_qs.filter(equipment__equipment_type=eq_type).aggregate(
                fuel=Sum('fuel_consumed'),
                hours=Sum('engine_hours')
            )
            f = float(type_tel['fuel'] or 0.0)
            h = float(type_tel['hours'] or 0.0)
            by_type[eq_type] = {
                'label': label,
                'fuel_liters': round(f, 2),
                'engine_hours': round(h, 2),
                'burn_rate_lph': round(f / h, 2) if h > 0 else 0.0
            }

        return {
            'total_fuel_consumed_liters': round(total_fuel, 2),
            'total_engine_hours': round(total_engine, 2),
            'avg_fuel_consumption_rate': avg_rate,
            'by_equipment_type': by_type,
        }

    @staticmethod
    def get_site_breakdowns():
        """Get per-site equipment count, active units, and utilization rate."""
        sites = Site.objects.all()
        results = []
        for site in sites:
            eq_count = site.equipment.count()
            active_count = site.equipment.filter(status__in=[Equipment.STATUS_IN_USE, Equipment.STATUS_RENTED]).count()
            active_rentals = Rental.objects.filter(site=site, status=Rental.STATUS_ACTIVE).count()
            rate = round((active_count / eq_count) * 100, 2) if eq_count > 0 else 0.0

            results.append({
                'site_id': site.id,
                'site_code': site.site_code,
                'site_name': site.name,
                'total_equipment': eq_count,
                'active_equipment': active_count,
                'utilization_rate': rate,
                'active_rentals': active_rentals,
            })
        return results

    @staticmethod
    def get_time_series_data(days=7):
        """Generate time-series utilization and fuel data points."""
        points = []
        now = timezone.now()
        total_eq = Equipment.objects.count() or 1

        for i in range(days, -1, -1):
            day = now - timedelta(days=i)
            day_start = day.replace(hour=0, minute=0, second=0, microsecond=0)
            day_end = day.replace(hour=23, minute=59, second=59, microsecond=999999)

            day_tel = Telemetry.objects.filter(timestamp__gte=day_start, timestamp__lte=day_end)
            distinct_in_use = day_tel.filter(speed__gt=0).values('equipment_id').distinct().count()
            distinct_idle = day_tel.filter(speed=0, idle_hours__gt=0).values('equipment_id').distinct().count()
            fuel_sum = day_tel.aggregate(f=Sum('fuel_consumed'))['f'] or 0.0

            rate = round((distinct_in_use / total_eq) * 100, 2)
            points.append({
                'timestamp': day_start.strftime('%Y-%m-%d'),
                'utilization_rate': rate,
                'active_units': distinct_in_use,
                'idle_units': distinct_idle,
                'fuel_burned': round(float(fuel_sum), 2),
            })
        return points

    @classmethod
    def get_overview(cls):
        """Combine all analytics into a comprehensive overview."""
        return {
            'fleet_summary': cls.get_fleet_utilization(),
            'idle_summary': cls.get_idle_analytics(),
            'fuel_summary': cls.get_fuel_efficiency(),
            'site_breakdowns': cls.get_site_breakdowns(),
            'time_series': cls.get_time_series_data(7),
        }

    @staticmethod
    def export_csv_report(report_type='fleet'):
        """Generate CSV string for analytics reports."""
        output = io.StringIO()
        writer = csv.writer(output)

        if report_type == 'fleet':
            writer.writerow(['Equipment ID', 'Type', 'Model', 'Site', 'Status', 'Engine Hours', 'Idle Hours', 'Fuel Level'])
            for eq in Equipment.objects.select_related('site').all():
                live = getattr(eq, 'live_state', None)
                writer.writerow([
                    eq.equipment_id,
                    eq.equipment_type,
                    eq.model,
                    eq.site.name if eq.site else 'N/A',
                    eq.status,
                    live.engine_hours if live else 0,
                    live.idle_hours if live else 0,
                    live.fuel_level if live else 0,
                ])

        elif report_type == 'rentals':
            writer.writerow(['Rental Ref', 'Equipment ID', 'Operator', 'Site', 'Status', 'Started At', 'Due At', 'Completed At'])
            for r in Rental.objects.select_related('equipment', 'operator', 'site').all():
                writer.writerow([
                    r.rental_reference,
                    r.equipment.equipment_id,
                    r.operator.name,
                    r.site.name,
                    r.status,
                    r.started_at.isoformat() if r.started_at else '',
                    r.due_at.isoformat() if r.due_at else '',
                    r.completed_at.isoformat() if r.completed_at else '',
                ])

        elif report_type == 'sites':
            writer.writerow(['Site Code', 'Site Name', 'Total Assets', 'Active Assets', 'Utilization Rate (%)'])
            for s in AnalyticsService.get_site_breakdowns():
                writer.writerow([s['site_code'], s['site_name'], s['total_equipment'], s['active_equipment'], s['utilization_rate']])

        output.seek(0)
        return output.getvalue()
