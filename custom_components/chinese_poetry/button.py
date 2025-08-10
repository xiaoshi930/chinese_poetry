"""Button platform for Chinese Poetry integration."""
import logging
import datetime

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers import entity_registry as er

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Chinese Poetry button."""
    button = ChinesePoetryButton(hass)
    async_add_entities([button], True)


class ChinesePoetryButton(ButtonEntity):
    """Representation of a Chinese Poetry button."""

    def __init__(self, hass):
        """Initialize the button."""
        self.hass = hass
        self.entity_id = "button.chinese_poetry_update"
        self._name = "古诗词刷新"
        self._attr_available = True
        self._attr_device_info = {
            "identifiers": {(DOMAIN, "chinese_poetry_device")},
            "name": "古诗词",
            "manufacturer": "Chinese Poetry"
        }

    @property
    def name(self):
        """Return the name of the button."""
        return self._name

    @property
    def unique_id(self):
        """Return a unique ID."""
        return "button.chinese_poetry_update"

    @property
    def icon(self):
        """Return the icon to use in the frontend."""
        return "mdi:refresh"

    async def async_press(self, force_update: bool = True) -> None:
        """Handle the button press."""
        # 查找并更新传感器实体
        sensor_entity_id = "sensor.chinese_poetry"
        _LOGGER.debug(f"尝试更新传感器实体: {sensor_entity_id}, force_update={force_update}")
        
        # 获取传感器实体
        sensor_entity = self.hass.states.get(sensor_entity_id)
        if sensor_entity is None:
            _LOGGER.error(f"未找到传感器实体: {sensor_entity_id}")
            return
        
        # 获取上次更新时间
        last_updated = sensor_entity.last_updated
        if last_updated is None:
            _LOGGER.debug("无上次更新时间记录，强制更新")
        else:
            from homeassistant.util import dt as dt_util
            now = dt_util.now()
            time_since_last_update = (now - last_updated).total_seconds() / 3600
            _LOGGER.debug(f"距离上次更新已过去: {time_since_last_update} 小时")
            
            # 如果未强制更新且时间间隔小于1小时，则跳过
            if not force_update and time_since_last_update < 1:
                _LOGGER.debug(f"跳过更新: 距离上次更新仅过去 {time_since_last_update} 小时，设定间隔为 1 小时")
                return
        
        try:
            # 获取传感器实体并调用强制更新方法
            sensor_entity = self.hass.states.get(sensor_entity_id)
            if sensor_entity is not None:
                sensor = self.hass.data[DOMAIN]["sensor"]
                await sensor.force_update()
                _LOGGER.debug("成功触发古诗词强制更新")
            else:
                _LOGGER.error(f"未找到传感器实体: {sensor_entity_id}")
        except Exception as e:
            _LOGGER.error(f"更新传感器失败: {e}")
