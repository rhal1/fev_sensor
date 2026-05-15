# FEV Sensor – Sopkärl tömningsschema

Custom integration för Home Assistant som spårar när sopkärlen töms.

## Installation

1. Kopiera `fev_sensor/` till `config/custom_components/fev_sensor/`
2. Lägg till i `configuration.yaml`:
```yaml
sensor:
  - platform: fev_sensor
```
3. Starta om Home Assistant.

## Sensorer

| Entitet | State | Beskrivning |
|---|---|---|
| `sensor.sopkarl_matavfall` | datum (ISO) | Nästa tömning av Matavfall |
| `sensor.sopkarl_restavfall` | datum (ISO) | Nästa tömning av Restavfall |
| `sensor.sopkarl_pappersforpackningar` | datum (ISO) | Nästa tömning av Pappersförpackningar |
| `sensor.sopkarl_plastforpackningar` | datum (ISO) | Nästa tömning av Plastförpackningar |
| `sensor.nasta_tomning` | antal dagar | Närmaste tömning bland alla kärl |

Alla sensorer har attributen `days_until`, `date_formatted` och `bin`/`bins`.  
`sensor.nasta_tomning` har även `description` (läsbar text) och `all_collections`.

## Schema

Hämtning sker på **fredagar**, varannan vecka med roterande kärl (startpunkt v18 2026):
- v18: Matavfall + Restavfall
- v20: Matavfall + Pappersförpackningar
- v22: Matavfall + Plastförpackningar
- v24: Matavfall + Restavfall (upprepar)

## Automation

För att enkelt använda detta i en automation, sätt: 

```yaml
action: # Notification entity
metadata: {}
data:
  title: Soptömning
  message: '{{ state_attr(''sensor.nasta_tomning'', ''description'') }}'
```
