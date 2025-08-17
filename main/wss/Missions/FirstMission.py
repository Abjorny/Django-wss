from asgiref.sync import sync_to_async
from wss.models import Settings
from wss.Uart.UartController import UartControllerAsync 
import asyncio
import time

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
        timer = time.time()
        while time.time() - timer < action.time:
            await uartController.sendCommand(f"3{mission.speed + 200}{action.compos + 200}")
            await asyncio.sleep(0.05)  
        
    await uartController.sendCommand(f"3{200}{action.compos + 200}")