"""
Smart asset reallocation optimizer matching under-utilized equipment with high-demand sites.
"""


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

        # Index forecasts by (site_code, equipment_type)
        demand_map = {}
        for f in demand_forecasts:
            key = (f.get('site_code'), f.get('equipment_type'))
            demand_map[key] = f.get('predicted_demand', 0.0)

        # Identify surplus idle/available machines
        for eq in equipment_inventory:
            if eq.get('status') in ['AVAILABLE', 'IDLE']:
                source_site = eq.get('site_code')
                eq_type = eq.get('equipment_type')

                # Find highest demand alternative site for this equipment type
                best_target = None
                highest_demand = 0.0

                for s in sites:
                    if s.get('site_code') != source_site:
                        d = demand_map.get((s.get('site_code'), eq_type), 0.0)
                        if d > highest_demand:
                            highest_demand = d
                            best_target = s

                if best_target and highest_demand > 2.0:
                    score = min(0.95, round(0.55 + (highest_demand * 0.08), 2))
                    recommendations.append({
                        'equipment_id': eq.get('equipment_id'),
                        'equipment_type': eq_type,
                        'source_site_code': source_site,
                        'target_site_code': best_target.get('site_code'),
                        'target_site_name': best_target.get('name'),
                        'predicted_target_demand': highest_demand,
                        'score': score,
                        'reason': f"Reallocate surplus {eq_type} from {source_site} to {best_target.get('name')} to satisfy forecasted demand spike ({highest_demand:.1f} units)."
                    })

        return recommendations
