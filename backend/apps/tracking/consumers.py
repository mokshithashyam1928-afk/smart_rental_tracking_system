"""
WebSocket consumers for real-time tracking updates.
"""
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from apps.telemetry.models import EquipmentLiveState


class EquipmentLiveStateConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for equipment live state updates."""
    
    async def connect(self):
        """Handle WebSocket connection."""
        self.user = self.scope['user']
        
        # Check if user is authenticated
        if not self.user.is_authenticated:
            await self.close()
            return
        
        # Extract equipment_id from URL if provided
        self.equipment_id = self.scope['url_route'].get('kwargs', {}).get('equipment_id')
        
        if self.equipment_id:
            self.room_name = f'equipment_{self.equipment_id}'
        else:
            self.room_name = 'equipment_all'
        
        # Join channel group
        await self.channel_layer.group_add(self.room_name, self.channel_name)
        await self.accept()
        
        # Send initial state if equipment_id is specified
        if self.equipment_id:
            live_state = await self.get_equipment_state(self.equipment_id)
            if live_state:
                await self.send(text_data=json.dumps({
                    'type': 'equipment.update',
                    'data': live_state
                }))
    
    async def disconnect(self, close_code):
        """Handle WebSocket disconnection."""
        if hasattr(self, 'room_name'):
            await self.channel_layer.group_discard(self.room_name, self.channel_name)
    
    async def equipment_update(self, event):
        """Handle equipment update message."""
        await self.send(text_data=json.dumps({
            'type': 'equipment.update',
            'data': event['data']
        }))
    
    @database_sync_to_async
    def get_equipment_state(self, equipment_id):
        """Get current state of equipment."""
        try:
            live_state = EquipmentLiveState.objects.select_related('equipment', 'operator').get(
                equipment__equipment_id=equipment_id
            )
            return {
                'equipment_id': live_state.equipment.equipment_id,
                'status': live_state.status,
                'last_seen': live_state.last_seen.isoformat() if live_state.last_seen else None,
                'latitude': live_state.latitude,
                'longitude': live_state.longitude,
                'engine_hours': live_state.engine_hours,
                'idle_hours': live_state.idle_hours,
                'fuel_level': live_state.fuel_level,
                'speed': live_state.speed,
                'operator_id': live_state.operator.employee_id if live_state.operator else None,
            }
        except EquipmentLiveState.DoesNotExist:
            return None
