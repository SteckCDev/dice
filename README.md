# 🎲 Dice Remastered

## Deploy
### ...
### Run Postgres and Redis containers
```shell
docker-compose -f docker-compose.yml --env-file .dev.env up -d
```
### ...

## Abbreviations and aliases
### Common
1. **TG** - *telegram*
2. **SMSR** - *SMS receiving service that accepts money transfers*
3. **TTL** - *time to live, common name for any time limit*
### Game modes
1. **PVB** - *player versus bot in private chat*
2. **PVP** - *player versus player in private chat*
3. **PVPC** - *player versus player in group chat*
4. **PVPF** - *player versus fake player in auto-generated fake game*
### Transactions
1. **BTC** - *bitcoin*
2. **BTC wallet** - *bitcoin wallet address of any type: Legacy, SegWit, Native SegWit and Taproot*
3. **Card details** - *16-digit bank card number*
