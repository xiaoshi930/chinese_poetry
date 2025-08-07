"""Button platform for Chinese Poetry integration."""
import logging

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

    async def async_press(self) -> None:
        """Handle the button press."""
        # 查找并更新传感器实体
        sensor_entity_id = "sensor.chinese_poetry"
        
        # 直接通过服务调用更新实体
        await self.hass.services.async_call(
            "homeassistant", "update_entity", {"entity_id": sensor_entity_id}
        )
        _LOGGER.debug("通过按钮触发古诗词更新")