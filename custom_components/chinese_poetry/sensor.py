"""Sensor platform for Chinese Poetry integration."""
import logging
import os
import random
from datetime import timedelta
import pandas as pd

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.util import slugify

from .const import (
    DOMAIN,
    DEFAULT_SCAN_INTERVAL,
    ATTR_TITLE,
    ATTR_DYNASTY,
    ATTR_AUTHOR,
    ATTR_CONTENT1,
    ATTR_CONTENT2,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Chinese Poetry sensor."""
    scan_interval = config_entry.options.get(
        "scan_interval", 
        config_entry.data.get("scan_interval", DEFAULT_SCAN_INTERVAL)
    )
    
    # 创建传感器实体
    sensor = ChinesePoetry(hass, scan_interval)
    async_add_entities([sensor], True)


class ChinesePoetry(SensorEntity):
    """Representation of a Chinese Poetry sensor."""

    def __init__(self, hass, scan_interval):
        """Initialize the sensor."""
        self.hass = hass
        self.entity_id = "sensor.chinese_poetry"
        self._name = "古诗词"
        self._state = None
        self._available = True
        self._attrs = {}
        self._scan_interval = scan_interval
        self._excel_path = os.path.join(os.path.dirname(__file__), "古诗词.xlsx")
        self._poetry_data = None
        self._unsub_interval = None

    async def async_added_to_hass(self) -> None:
        """Handle entity which will be added."""
        await super().async_added_to_hass()
        
        # 首次加载数据
        await self.hass.async_add_executor_job(self._load_excel_data)
        
        # 设置定时更新
        self._unsub_interval = async_track_time_interval(
            self.hass,
            self._interval_update,
            timedelta(hours=self._scan_interval)
        )

    async def async_will_remove_from_hass(self) -> None:
        """Handle entity removal from Home Assistant."""
        # 取消定时更新
        if self._unsub_interval:
            self._unsub_interval()
            self._unsub_interval = None

    async def _interval_update(self, _=None) -> None:
        """Update state at intervals."""
        await self.async_update()

    async def async_update(self) -> None:
        """Update the sensor state."""
        await self.hass.async_add_executor_job(self._update)

    def _load_excel_data(self):
        """Load data from Excel file."""
        try:
            self._poetry_data = pd.read_excel(self._excel_path)
            _LOGGER.info(f"成功加载古诗词数据，共 {len(self._poetry_data)} 条")
        except Exception as e:
            _LOGGER.error(f"加载古诗词数据失败: {e}")
            self._available = False
            self._poetry_data = None

    def _update(self):
        """Update the sensor state."""
        if self._poetry_data is None or len(self._poetry_data) == 0:
            self._load_excel_data()
            if self._poetry_data is None or len(self._poetry_data) == 0:
                self._available = False
                return

        try:
            # 随机选择一行
            if len(self._poetry_data) > 0:
                random_row = self._poetry_data.iloc[random.randint(0, len(self._poetry_data) - 1)]
                
                # 提取数据
                title = random_row.get("标题", "未知")
                dynasty = random_row.get("朝代", "未知")
                author = random_row.get("作者", "未知")
                content1 = random_row.get("正文1", "")
                content2 = random_row.get("正文2", "")
                
                # 更新状态和属性
                self._state = title
                self._attrs = {
                    ATTR_TITLE: title,
                    ATTR_DYNASTY: dynasty,
                    ATTR_AUTHOR: author,
                    ATTR_CONTENT1: content1,
                    ATTR_CONTENT2: content2,
                }
                self._available = True
                
                _LOGGER.debug(f"更新古诗词: {title} - {author}")
            else:
                _LOGGER.warning("古诗词数据为空")
                self._available = False
        except Exception as e:
            _LOGGER.error(f"更新古诗词失败: {e}")
            self._available = False

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def unique_id(self):
        """Return a unique ID."""
        return "sensor.chinese_poetry"

    @property
    def available(self):
        """Return True if entity is available."""
        return self._available

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        return self._attrs

    @property
    def icon(self):
        """Return the icon to use in the frontend."""
        return "mdi:book-open-page-variant"