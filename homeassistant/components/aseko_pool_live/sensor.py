"""Support for Aseko Pool Live sensors."""

from __future__ import annotations

from dataclasses import dataclass

from aioaseko import Unit, Variable

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONCENTRATION_KILOGRAMS_PER_CUBIC_METER,
    CONCENTRATION_MILLIGRAMS_PER_LITER,
    UnitOfElectricPotential,
    UnitOfLength,
    UnitOfRate,
    UnitOfTemperature,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import AsekoDataUpdateCoordinator
from .entity import AsekoEntity


@dataclass(frozen=True, kw_only=True)
class AsekoSensorEntityDescription(SensorEntityDescription):
    """Describes an Aseko binary sensor entity."""


UNIT_SENSORS = {
    "airTemp": AsekoSensorEntityDescription(
        key="air_temperature",
        translation_key="air_temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    ),
    "waterTemp": AsekoSensorEntityDescription(
        key="water_temperature",
        translation_key="water_temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    ),
    "ph": AsekoSensorEntityDescription(
        key="ph",
        translation_key="ph",
        device_class=SensorDeviceClass.PH,
    ),
    "rx": AsekoSensorEntityDescription(
        key="redox",
        translation_key="redox",
        device_class=SensorDeviceClass.VOLTAGE,
        native_unit_of_measurement=UnitOfElectricPotential.MILLIVOLT,
        icon="mdi:test-tube",
    ),
    "electrodePower": AsekoSensorEntityDescription(
        key="electrolyzer",
        translation_key="electrolyzer",
        device_class=SensorDeviceClass.GAS_PRODUCTION,
        native_unit_of_measurement=UnitOfRate.GRAM_PER_HOUR,
        icon="mdi:lightning-bolt",
    ),
    "clf": AsekoSensorEntityDescription(
        key="free_chlorine",
        translation_key="free_chlorine",
        native_unit_of_measurement=CONCENTRATION_MILLIGRAMS_PER_LITER,
        icon="mdi:test-tube",
    ),
    "salinity": AsekoSensorEntityDescription(
        key="salinity",
        translation_key="salinity",
        native_unit_of_measurement=CONCENTRATION_KILOGRAMS_PER_CUBIC_METER,
    ),
    "waterLevel": AsekoSensorEntityDescription(
        key="water_level",
        translation_key="water_level",
        device_class=SensorDeviceClass.DISTANCE,
        native_unit_of_measurement=UnitOfLength.CENTIMETERS,
        icon="mdi:waves",
    ),
}


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Aseko Pool Live sensors."""
    data: list[tuple[Unit, AsekoDataUpdateCoordinator]] = hass.data[DOMAIN][
        config_entry.entry_id
    ]

    async_add_entities(
        VariableSensorEntity(unit, variable, coordinator)
        for unit, coordinator in data
        for variable in unit.variables
    )


class VariableSensorEntity(AsekoEntity, SensorEntity):
    """Representation of a unit variable sensor entity."""

    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(
        self, unit: Unit, variable: Variable, coordinator: AsekoDataUpdateCoordinator
    ) -> None:
        """Initialize the variable sensor."""
        super().__init__(unit, coordinator)
        self._variable = variable

        entity_description = UNIT_SENSORS.get(self._variable.type)
        if entity_description is not None:
            self.entity_description = entity_description
        else:
            self._attr_name = self._variable.name
            self._attr_native_unit_of_measurement = self._variable.unit

        self._attr_unique_id = f"{self._unit.serial_number}{self._variable.type}"

    @property
    def native_value(self) -> int | None:
        """Return the state of the sensor."""
        variable = self.coordinator.data[self._variable.type]
        return variable.current_value
