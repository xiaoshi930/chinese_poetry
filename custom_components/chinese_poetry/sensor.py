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
    
    _LOGGER.info(f"古诗词集成设置，配置的更新间隔: {scan_interval} 小时")
    
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
        _LOGGER.info(f"古诗词传感器初始化，设置更新间隔: {self._scan_interval} 小时")
        self._excel_path = os.path.join(os.path.dirname(__file__), "古诗词.xlsx")
        self._poetry_data = None
        self._unsub_interval = None
        self._last_update = None  # 添加上次更新时间记录

    async def async_added_to_hass(self) -> None:
        """Handle entity which will be added."""
        await super().async_added_to_hass()
        
        # 首次加载数据
        await self.hass.async_add_executor_job(self._load_excel_data)
        
        # 记录首次加载时间
        self._last_update = pd.Timestamp.now()
        
        # 设置定时更新 - 确保使用小时作为单位
        update_interval = timedelta(hours=self._scan_interval)
        _LOGGER.info(f"古诗词传感器设置更新间隔: {self._scan_interval} 小时 (实际间隔: {update_interval})")
        
        self._unsub_interval = async_track_time_interval(
            self.hass,
            self._interval_update,
            update_interval
        )

    async def async_will_remove_from_hass(self) -> None:
        """Handle entity removal from Home Assistant."""
        # 取消定时更新
        if self._unsub_interval:
            self._unsub_interval()
            self._unsub_interval = None

    async def _interval_update(self, _=None) -> None:
        """Update state at intervals."""
        # 检查是否到达更新时间
        current_time = pd.Timestamp.now()
        if self._last_update is not None:
            elapsed_time = current_time - self._last_update
            elapsed_hours = elapsed_time.total_seconds() / 3600
            
            if elapsed_hours >= self._scan_interval:
                _LOGGER.info(f"定时更新触发：已过 {elapsed_hours:.2f} 小时，执行更新")
                await self.async_update()
            else:
                _LOGGER.debug(f"定时更新跳过：距离上次更新仅过去 {elapsed_hours:.2f} 小时，设定间隔为 {self._scan_interval} 小时")

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
        # 检查是否需要更新
        current_time = pd.Timestamp.now()
        if self._last_update is not None:
            elapsed_time = current_time - self._last_update
            elapsed_hours = elapsed_time.total_seconds() / 3600
            
            # 如果距离上次更新不足设定的时间间隔，则跳过更新
            if elapsed_hours < self._scan_interval:
                _LOGGER.debug(f"跳过更新：距离上次更新仅过去 {elapsed_hours:.2f} 小时，设定间隔为 {self._scan_interval} 小时")
                return
        
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
                
                # 记录更新时间
                self._last_update = current_time
                
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
