"""Adds config flow for College Football."""
from __future__ import annotations

import logging
from typing import Any, Dict, Optional

import aiohttp
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult

from .const import (
    API_ENDPOINT,
    CONF_TIMEOUT,
    CONF_TEAM_ID,
    DEFAULT_NAME,
    DEFAULT_TIMEOUT,
    DOMAIN,
    USER_AGENT,
)

JSON_FEATURES = "features"
JSON_PROPERTIES = "properties"
JSON_ID = "id"

_LOGGER = logging.getLogger(__name__)


def _get_schema(    
    hass: HomeAssistant,
    user_input: Optional[Dict[str, Any]],
    default_dict: Dict[str, Any],
    entry_id: str = None
) -> vol.Schema:
    """Gets a schema using the default_dict as a backup."""
    if user_input is None:
        user_input = {}

    def _get_default(key: str, fallback_default: Any = None) -> None:
        """Gets default value for key."""
        return user_input.get(key, default_dict.get(key, fallback_default))

    return vol.Schema(
        {
            vol.Required(CONF_TEAM_ID, default=_get_default(CONF_TEAM_ID,_get_team_list())): str,
            vol.Optional(CONF_NAME, default=_get_default(CONF_NAME, DEFAULT_NAME)): str,
            vol.Optional(CONF_TIMEOUT, default=_get_default(CONF_TIMEOUT, DEFAULT_TIMEOUT)): int,
        }
    )


def _get_team_list() -> list:
    """Return list of team acronyms"""

    team_list = [
        #### FBS SCHOOLS ####
        ## Big 12 ##
        "ttu",
        "tex",
        "wvu",
        "tcu",
        "okst",
        "ksu",
        "isu",
        "ou",
        "bay",
        "ku",
        ## ACC ##
        "bc",
        "clem",
        "duke",
        "fsu",   
        "gt",
        "lou",
        "mia",
        "unc",
        "ncst",
        "pitt",
        "syr",
        "uva",
        "vt",
        "wake",
        "nd",
        ## Big 10 ##
        "ill",
        "iu",
        "iowa",
        "md",
        "mich",
        "msu",
        "minn",
        "neb",
        "nu",
        "osu",
        "psu",
        "pur",
        "rutg",
        "wisc",
        ## PAC 12 ##
        'ariz',
        'asu',
        'cal',
        'ucla',
        'colo',
        'ore',
        'orst',
        'usc',
        'stan',
        'utah',
        'wash',
        'wsu',
        ## SEC ##
        'ala',
        'ark',
        'aub',
        'fla',
        'uga',
        'uk',
        'lsu',
        'miss',
        'miz',
        'sc',
        'ta&m',
        'van',
        ## American ##
        'tem',
        'usf',
        'tuln',
        'navy',
        'mem',
        'smu',
        'ucf',
        'cin',
        'tlsa',
        'ecu',
        'hou',
        ## Conference USA ##
        'wku',
        'mrsh',
        'odu',
        'mtsu',
        'fau',
        'clt',
        'fiu',
        'utsa',
        'uab',
        'unt',
        'utep',
        'rice',
        'usm',
        'lt',
        ## Independent ##
        'byu', 
        'army',
        'lib',
        'nmsu',
        'mass',
        'conn',
        ## Mid-American ##
        'kent',
        'm-oh',
        'ohio',
        'bgsu',
        'buff',
        'akr',
        'niu',
        'cmu',
        'tol',
        'ball',
        'emu',
        'wmu',
        ## Mountain West ##
        'usu',
        'afa',
        'bsu',
        'wyo',
        'csu',
        'unm',
        'sdsu',
        'fres',
        'nev',
        'sjsu',
        'haw',
        'unlv',
        ## Sun Belt ##
        'app',
        'gast',
        'ccu',
        'troy',
        'gaso',
        'ul',
        'txst',
        'ulm',
        'usa',
        'arst',
        #### FCS SCHOOLS ####
        ## ASUN ##
        'jvst',
        'cark',
        'eku',
        'kenn',
        'una',
        'apsu',
        ## Big Sky ##
        'cp',
        'ewu',
        'idho',
        'mont',
        'mtst',
        'nau',
        'unco',
        'prst',
        'sac',
        'ucd',
        'web',
        'idst',
        ## Big South ##
        'bry',
        'cam',
        'chso',
        'gweb',
        'ncat',
        'rmu',
        ## CAA ##
        'alb',
        'del',
        'elon',
        'hamp',
        'me',
        'monm',
        'unh',
        'uri',
        'rich',
        'stbk',
        'tow',
        'vill',
        'w&m',
        ## Ivy ##
        'brwn',
        'colu',
        'cor',
        'dart',
        'harv',
        'penn',
        'prin',
        'yale',
        ## MEAC ##
        'dsu',
        'morg',
        'norf',
        'nccu',
        'scst',
        'how',
        ## Missouri Valley ##
        'ilst',
        'inst',
        'most',
        'und',
        'ndsu',
        'uni',
        'sdak',
        'sdst',
        'siu',
        'wiu',
        'ysu',
        ## Northeast ##
        'ccsu',
        'liu',
        'mrmk',
        'shu',
        'sfpa',
        'sto',
        'wag',
        'duq',
        ## Ohio Valley ##
        'eiu',
        'lin',
        'mur',
        'semo',
        'tnst',
        'tntc',
        'utm',
        ## Patriot ##
        'buck',
        'colg',
        'for',
        'gtwn',
        'hc',
        'laf',
        'leh',
        ## Pioneer ##
        "but",
        "dav",
        "day",
        "drke",
        "mrst",
        "pres",
        "usd",
        "stthom",
        "stet",
        "val",
        "more",
        ## Southern ##
        "mer",
        "utc",
        "etsu",
        "fur",
        "sam",
        "cit",
        "vmi",
        "wcu",
        "wof",
        ## Southland ##
        "hbu",
        "uiw",
        "lam",
        "mcn",
        "nich",
        "nwst",
        "sela",
        "tamc",
        ## SWAC ##
        "alst",
        "aamu",
        "bcu",
        "jkst",
        "mvsu",
        "famu",
        "alcn",
        "uapb",
        "gram",
        "pv",
        "sou",
        "txso",
        ## WAC ##
        "shsu",
        "acu",
        "suu",
        "tar",
        "utu",
        "sfa",
        
    ]
    
    _LOGGER.debug("Team list: %s", team_list)
    return team_list


@config_entries.HANDLERS.register(DOMAIN)
class CollegeFootballScoresFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for College Football."""

    VERSION = 2
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    def __init__(self):
        """Initialize."""
        self._data = {}
        self._errors = {}

    # async def async_step_import(self, user_input: dict[str, Any]) -> FlowResult:
    #     """Import a config entry."""

    #     user_input = user_input[DOMAIN]
    #     result: FlowResult = await self.async_step_user(user_input=user_input)
    #     if errors := result.get("errors"):
    #         return self.async_abort(reason=next(iter(errors.values())))
    #     return result

    async def async_step_user(self, user_input={}):
        """Handle a flow initialized by the user."""
        self._errors = {}
        self._team_list = _get_team_list()

        if user_input is not None:
            self._data.update(user_input)
            return self.async_create_entry(title=self._data[CONF_NAME], data=self._data)
        return await self._show_config_form(user_input)

    async def _show_config_form(self, user_input):
        """Show the configuration form to edit location data."""

        # Defaults
        defaults = {
            CONF_NAME: DEFAULT_NAME,
            CONF_TIMEOUT: DEFAULT_TIMEOUT,
            CONF_TEAM_ID: self._team_list,
        }

        return self.async_show_form(
            step_id="user",
            data_schema=_get_schema(self.hass, user_input, defaults),
            errors=self._errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return CollegeFootballScoresOptionsFlow(config_entry)


class CollegeFootballScoresOptionsFlow(config_entries.OptionsFlow):
    """Options flow for College Football."""

    def __init__(self, config_entry):
        """Initialize."""
        self.config = config_entry
        self._errors = {}

    async def async_step_init(self, user_input=None):
        """Manage options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)
        return await self._show_options_form(user_input)

    async def _show_options_form(self, user_input):
        """Show the configuration form to edit location data."""

        return self.async_show_form(
            step_id="init",
            data_schema=_get_schema(self.hass, user_input, self.config.data),
            errors=self._errors,
        )
