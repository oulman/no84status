# NO-84 Digipeater status update tool

## About

## Setup

1. Set up the environment

```
$ virtualenv ~/venv/psat -p python3
$ source ~/venv/psat/bin/activate
$ pip3 install -r requirements.txt
```

2. Modify the credentials.json.example file with your Twitter API keys 

```json
{
    "consumer_key": "key", 
    "consumer_secret": "secret", 
    "access_token_key": "token_key",
    "access_token_secret": "token_secret"
}
```

3. Copy it the default location (or redefine via credentials_file variable in get_updates.py)

```
sudo mkdir -p /app/no84status
sudo chown user:user /app/no84status
cp credentials.json.example /app/credentials.json
```

