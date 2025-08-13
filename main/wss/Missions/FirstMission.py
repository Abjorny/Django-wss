from asgiref.sync import sync_to_async
from wss.models import Settings
from wss.Uart.UartController import UartControllerAsync 
import asyncio

uartController = UartControllerAsync()

@sync_to_async
def get_settings_data():
    settings = Settings.objects.select_related('first_mission').first()
    if not settings:
        return None
    return settings.first_mission


async def startFirstMission():
    mission = await get_settings_data()
    if not mission:
        return
    
    actions = await sync_to_async(list)(mission.actions.all())
    for action in actions:
        await uartController.sendCommand(f"3{mission.speed}{action.compos}")
        await asyncio.sleep(action.time)
