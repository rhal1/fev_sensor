# FEV Sensor – Sopkärl tömningsschema

Custom integration för Home Assistant som spårar när sopkärlen töms.

## Installation

1. Kopiera mappen `custom_components/fev_sensor/` till din HA-instans under `config/custom_components/fev_sensor/`
2. Lägg till i `configuration.yaml`:

```yaml
sensor:
  - platform: fev_sensor
```

3. Starta om Home Assistant.

## Sensorer

| Entitet | Beskrivning |
|---|---|
| `sensor.sopkarl_matavfall` | Nästa tömning av Matavfall |
| `sensor.sopkarl_restavfall` | Nästa tömning av Restavfall |
| `sensor.sopkarl_pappersforpackningar` | Nästa tömning av Pappersförpackningar |
| `sensor.sopkarl_plastforpackningar` | Nästa tömning av Plastförpackningar |
| `sensor.nasta_tomning` | Den närmaste tömningen bland alla kärl |

## Schema

Hämtning sker normalt på **fredagar**.

- **Matavfall** töms varannan vecka (alla jämna körningsveckor)
- **Restavfall, Pappersförpackningar, Plastförpackningar** roterar varannan vecka

Roteringsmönster (startpunkt vecka 18, 2025):
- v18: Matavfall + Restavfall
- v20: Matavfall + Pappersförpackningar
- v22: Matavfall + Plastförpackningar
- v24: Matavfall + Restavfall (upprepar)

## Sensorattribut

Varje sensor har dessa extra attribut:
- `days_until` – antal dagar till nästa tömning
- `date_formatted` – datum på svenska, t.ex. `3 aug`
- `bin` / `bins` – vilket/vilka kärl som töms

`sensor.nasta_tomning` har även:
- `all_collections` – nästa datum för alla kärl (ISO-format)
