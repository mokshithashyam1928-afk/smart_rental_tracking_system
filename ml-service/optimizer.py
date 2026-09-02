"""Smart asset reallocation optimizer for forecast-aware fleet balancing."""


class AssetReallocationOptimizer:
    """Optimizes fleet distribution by generating reallocation plans."""

    @staticmethod
    def optimize_allocations(sites: list, equipment_inventory: list, demand_forecasts: list) -> list:
        """
        Pairs surplus/idle equipment from low-demand sites to high-demand sites.
        """
        recommendations = []
        if len(sites) < 2 or not equipment_inventory:
            return recommendations

        # Index strongest forecasts by (site_code, equipment_type)
        demand_map = {}
        for f in demand_forecasts:
            key = (f.get('site_code'), f.get('equipment_type'))
            weighted_demand = float(f.get('predicted_demand', 0.0)) * float(f.get('confidence', 1.0))
            demand_map[key] = max(demand_map.get(key, 0.0), weighted_demand)

        available_by_site_type = {}
        for eq in equipment_inventory:
            if eq.get('status') in ['AVAILABLE', 'IDLE']:
                key = (eq.get('site_code'), eq.get('equipment_type'))
                available_by_site_type[key] = available_by_site_type.get(key, 0) + 1

        # Identify surplus idle/available machines
        for eq in equipment_inventory:
            if eq.get('status') in ['AVAILABLE', 'IDLE']:
                source_site = eq.get('site_code')
                eq_type = eq.get('equipment_type')
                source_weighted_demand = demand_map.get((source_site, eq_type), 0.0)
                source_available = available_by_site_type.get((source_site, eq_type), 0)
                if source_available <= 1 and source_weighted_demand >= 1.5:
                    continue

                # Find highest demand alternative site for this equipment type
                best_target = None
                best_gap = 0.0

                for s in sites:
                    if s.get('site_code') != source_site:
                        target_site_code = s.get('site_code')
                        d = demand_map.get((target_site_code, eq_type), 0.0)
                        target_available = available_by_site_type.get((target_site_code, eq_type), 0)
                        gap = d - target_available
                        if gap > best_gap:
                            best_gap = gap
                            best_target = s

                if best_target and best_gap > 0.25:
                    score = min(0.95, round(0.60 + (best_gap * 0.12), 2))
                    recommendations.append({
                        'equipment_id': eq.get('equipment_id'),
                        'equipment_type': eq_type,
                        'source_site_code': source_site,
                        'target_site_code': best_target.get('site_code'),
                        'target_site_name': best_target.get('name'),
                        'predicted_target_demand': round(best_gap, 2),
                        'score': score,
                        'reason': f"Reallocate surplus {eq_type} from {source_site} to {best_target.get('name')} to cover a forecasted demand gap of {best_gap:.1f} units."
                    })
                    available_by_site_type[(source_site, eq_type)] = max(0, available_by_site_type.get((source_site, eq_type), 0) - 1)
                    target_key = (best_target.get('site_code'), eq_type)
                    available_by_site_type[target_key] = available_by_site_type.get(target_key, 0) + 1

        return recommendations
