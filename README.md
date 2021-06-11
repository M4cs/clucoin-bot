# CluCoin Discord Price Bot

## Features

- Displays Current Clu Price
- Displays 24hr gain/loss
- Updates role/nick every minute or on `-price` command

### Config

Add a file called config.yaml

```yaml
token: BOT TOKEN
```

### Running

```bash
#  Without Docker
pip install -r requirements.txt
python -m src

# With Docker
docker compose up --build
```
