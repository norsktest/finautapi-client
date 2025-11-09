# Appname Mapping Guide

When working with UserStatus API, you need to use the correct `appname` code (not ordning ID or URL).

## Complete Appname Reference

| Appname | Full Norwegian Name | Short Name | Abbreviation | Sort Order |
|---------|-------------------|------------|--------------|------------|
| `afr` | Autorisasjonsordningen for finansielle rådgivere | Sparing & investering | S&I | 1 |
| `krd` | Autorisasjonsordningen i kreditt | Kreditt | KRD | 2 |
| `gos` | Godkjenningsordningen for selgere og rådgivere i skadeforsikring | Skadeforsikring | SF | 3 |
| `aip` | Autorisasjonsordningen i personforsikring | Personforsikring | PF | 4 |
| `sfn` | Skadeforsikring Næringsliv | Skadeforsikring Næring | SFN | 5 |
| `pfn` | Personforsikring Næringsliv | Personforsikring Næring | PFN | 6 |
| `inf` | Informasjonsgivere | Informasjonsgivere | INF | 7 |
| `ukr` | Autorisasjonsordningen i usikret kreditt | Usikret Kreditt | UKR | 7 |
| `ink` | Inkasso | Inkasso | INK | 8 |
| `dig` | Digitale Løsninger | Digitale Løsninger | DIG | 9 |
| `fin` | Generelle brukere | Generelle brukere | FIN | 10 |
| `rob` | Autorisasjonsordning for råbotrådgivere | Robotrådgivere | ROB | 0 |
| `n2` | Nivå 2 | N2 | N2 | 0 |
| `n3` | Nivå 3 | Åpne tester | NIVÅ 3 | 0 |

## Most Common Appnames

- **`afr`** - Financial advisors (Sparing & investering)
- **`krd`** - Credit authorization (Kreditt)
- **`gos`** - Insurance sales (Skadeforsikring)
- **`aip`** - Personal insurance (Personforsikring)

## Status Types by Appname

Each appname can have these status values:
- `{appname}new` - Not authorized (e.g., `afrnew`, `krdnew`)
- `{appname}ok` - Authorized (e.g., `afrok`, `krdok`)
- `hvilende` - Inactive/Resting (works for all appnames)
- `utmeldt` - Withdrawn (works for all appnames)
- `reauth` - Being reauthorized
- `tlnew` - Test leader not approved
- `tlok` - Test leader approved
- `paused` - Status error

## API Notes

- The `appname` field has a maximum length of 10 characters
- When creating status through the API, you can only set `hvilende` or `utmeldt`
- Active statuses (`{appname}ok`) are set through other processes (certification completion, etc.)
- The `appname` is NOT a URL - it's a short code

## Example Usage

```python
# Set user as inactive in AFR (financial advisors)
client.userstatus.set_inactive(
    user_id=123,
    appname="afr",  # NOT a URL, just the code
    status_date="2024-01-01",
    comment="Temporary leave",
    status_set_by_id=1
)

# Withdraw user from KRD (credit)
client.userstatus.set_withdrawn(
    user_id=123,
    appname="krd",  # Short code for credit authorization
    status_date="2024-01-01",
    comment="User requested withdrawal",
    status_set_by_id=1
)

# Set user as inactive in GOS (insurance)
client.userstatus.set_inactive(
    user_id=123,
    appname="gos",  # Insurance sales authorization
    status_date="2024-01-01",
    comment="Maternity leave",
    status_set_by_id=1
)
```