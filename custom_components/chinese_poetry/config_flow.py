"""Config flow for Chinese Poetry integration."""
import logging
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult

from .const import DOMAIN, DEFAULT_SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)

class ChinesePoetryConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Chinese Poetry."""

    VERSION = 1

    async def async_step_user(self, user_input=None) -> FlowResult:
        """Handle the initial step."""
        if user_input is None:
            return self.async_show_form(
                step_id="user",
                data_schema=vol.Schema({
                    vol.Optional("scan_interval", default=DEFAULT_SCAN_INTERVAL): vol.All(
                        vol.Coerce(int), vol.Range(min=1)
                    ),
                }),
            )

        await self.async_set_unique_id(DOMAIN)
        self._abort_if_unique_id_configured()

        return self.async_create_entry(
            title="古诗词",
            data=user_input,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get the options flow for this handler."""
        return ChinesePoetryOptionsFlowHandler(config_entry)


class ChinesePoetryOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options."""

    def __init__(self, config_entry):
        """Initialize options flow."""
        self._config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        options = {
            vol.Optional(
                "scan_interval",
                default=self.config_entry.options.get(
                    "scan_interval", self.config_entry.data.get("scan_interval", DEFAULT_SCAN_INTERVAL)
                ),
            ): vol.All(vol.Coerce(int), vol.Range(min=1)),
        }

        return self.async_show_form(step_id="init", data_schema=vol.Schema(options))
