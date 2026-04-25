from __future__ import annotations

import datetime
from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

_ROTATION = ["Restavfall", "Pappersförpackningar", "Plastförpackningar"]

_BASE_WEEK = 18
_BASE_YEAR = 2026


def _weeks_since_base(year: int, week: int) -> int:
    base_days = datetime.date.fromisocalendar(_BASE_YEAR, _BASE_WEEK, 1)
    target_days = datetime.date.fromisocalendar(year, week, 1)
    return (target_days - base_days).days // 7


def _bins_for_week(year: int, week: int) -> list[str]:
    offset = _weeks_since_base(year, week)
    if offset < 0 or offset % 2 != 0:
        return []
    rotation_index = (offset // 2) % len(_ROTATION)
    return ["Matavfall", _ROTATION[rotation_index]]


def _collection_date(year: int, week: int) -> datetime.date:
    return datetime.date.fromisocalendar(year, week, 5)


def _next_collection_for_bin(bin_name: str, from_date: datetime.date) -> datetime.date:
    year = from_date.isocalendar()[0]
    week = from_date.isocalendar()[1]

    for _ in range(60):
        if bin_name in _bins_for_week(year, week):
            date = _collection_date(year, week)
            if date >= from_date:
                return date
        week += 1
        if week > 52:
            last_week = datetime.date(year, 12, 28).isocalendar()[1]
            if week > last_week:
                week = 1
                year += 1

    raise ValueError(f"Could not find next collection for {bin_name}")


def _next_collections(from_date: datetime.date) -> dict[str, datetime.date]:
    bins = ["Matavfall", "Restavfall", "Pappersförpackningar", "Plastförpackningar"]
    return {b: _next_collection_for_bin(b, from_date) for b in bins}


def _format_date_sv(date: datetime.date) -> str:
    months = [
        "jan", "feb", "mar", "apr", "maj", "jun",
        "jul", "aug", "sep", "okt", "nov", "dec",
    ]
    return f"{date.day} {months[date.month - 1]}"


async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    async_add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    bins = ["Matavfall", "Restavfall", "Pappersförpackningar", "Plastförpackningar"]
    entities: list[SensorEntity] = [FEVBinSensor(b) for b in bins]
    entities.append(FEVNextCollectionSensor())
    async_add_entities(entities, update_before_add=True)


class FEVBinSensor(SensorEntity):
    _attr_icon = "mdi:trash-can-outline"

    def __init__(self, bin_name: str) -> None:
        self._bin_name = bin_name
        self._attr_name = f"Sopkärl {bin_name}"
        self._attr_unique_id = f"fev_bin_{bin_name.lower().replace('å', 'a').replace('ä', 'a').replace('ö', 'o').replace(' ', '_')}"
        self._next_date: datetime.date | None = None

    def update(self) -> None:
        today = datetime.date.today()
        self._next_date = _next_collection_for_bin(self._bin_name, today)

    @property
    def native_value(self) -> str | None:
        if self._next_date is None:
            return None
        return self._next_date.isoformat()

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        if self._next_date is None:
            return {}
        today = datetime.date.today()
        days_left = (self._next_date - today).days
        return {
            "days_until": days_left,
            "date_formatted": _format_date_sv(self._next_date),
            "bin": self._bin_name,
        }


class FEVNextCollectionSensor(SensorEntity):
    _attr_name = "Nästa tömning"
    _attr_unique_id = "fev_next_collection"
    _attr_icon = "mdi:calendar-clock"

    _attr_native_unit_of_measurement = "dagar"

    def __init__(self) -> None:
        self._days_until: int | None = None
        self._attrs: dict[str, Any] = {}

    def update(self) -> None:
        today = datetime.date.today()
        collections = _next_collections(today)

        earliest_date = min(collections.values())
        earliest_bins = [b for b, d in collections.items() if d == earliest_date]
        days_left = (earliest_date - today).days

        if len(earliest_bins) == 1:
            bin_str = earliest_bins[0]
        else:
            bin_str = " + ".join(earliest_bins)

        date_str = _format_date_sv(earliest_date)

        if days_left == 0:
            description = f"Idag: {bin_str}"
        elif days_left == 1:
            description = f"Imorgon: {bin_str} ({date_str})"
        else:
            description = f"{bin_str} om {days_left} dagar ({date_str})"

        self._days_until = days_left
        self._attrs = {
            "description": description,
            "date": earliest_date.isoformat(),
            "date_formatted": date_str,
            "bins": earliest_bins,
            "all_collections": {b: d.isoformat() for b, d in collections.items()},
        }

    @property
    def native_value(self) -> int | None:
        return self._days_until

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        return self._attrs
