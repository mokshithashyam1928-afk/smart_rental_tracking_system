"""
Analytics serializers for fleet utilization, fuel efficiency, idle time, and breakdowns.
"""
from rest_framework import serializers


class FleetUtilizationSerializer(serializers.Serializer):
    total_equipment = serializers.IntegerField()
    in_use = serializers.IntegerField()
    idle = serializers.IntegerField()
    available = serializers.IntegerField()
    rented = serializers.IntegerField()
    maintenance = serializers.IntegerField()
    offline = serializers.IntegerField()
    utilization_rate = serializers.FloatField()
    idle_rate = serializers.FloatField()
    period = serializers.CharField(required=False)


class IdleAnalyticsSerializer(serializers.Serializer):
    total_engine_hours = serializers.FloatField()
    total_idle_hours = serializers.FloatField()
    idle_percentage = serializers.FloatField()
    estimated_fuel_wasted_liters = serializers.FloatField()
    idle_cost_estimate_usd = serializers.FloatField()


class FuelEfficiencySerializer(serializers.Serializer):
    total_fuel_consumed_liters = serializers.FloatField()
    total_engine_hours = serializers.FloatField()
    avg_fuel_consumption_rate = serializers.FloatField()
    by_equipment_type = serializers.DictField(child=serializers.DictField())


class SiteBreakdownSerializer(serializers.Serializer):
    site_id = serializers.IntegerField()
    site_code = serializers.CharField()
    site_name = serializers.CharField()
    total_equipment = serializers.IntegerField()
    active_equipment = serializers.IntegerField()
    total_rented_hours = serializers.FloatField(required=False, default=0.0)
    total_fuel_liters = serializers.FloatField(required=False, default=0.0)
    utilization_rate = serializers.FloatField()
    active_rentals = serializers.IntegerField()


class TimeSeriesDataPointSerializer(serializers.Serializer):
    timestamp = serializers.CharField()
    utilization_rate = serializers.FloatField()
    active_units = serializers.IntegerField()
    idle_units = serializers.IntegerField()
    fuel_burned = serializers.FloatField()


class AnalyticsOverviewSerializer(serializers.Serializer):
    fleet_summary = FleetUtilizationSerializer()
    idle_summary = IdleAnalyticsSerializer()
    fuel_summary = FuelEfficiencySerializer()
    site_breakdowns = SiteBreakdownSerializer(many=True)
    time_series = TimeSeriesDataPointSerializer(many=True)
