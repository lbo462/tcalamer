# TCALAMER

- Léo BONNAIRE
- Léonard PRINCÉ
- Edgar BRUNAUD

# Start the python backend

Create a python virtual env

```shell
python -m venv venv
source venv/bin/activate
```

Install dependencies

```shell
pip install -r requirements.txt
```

# Main script

To start the main script, use `python src/main.py`

This script generates a JSON file which resumes the game.

The JSON follows the following scheme :

```json
{
  "initial_state": {
    "world": {
      "water": 5000,
      "food": 5000,
      "wood": 5000,
      "weather": 0
    },
    "wreck": {
      "buckets": 1,
      "axes": 1,
      "fishing_rods": 1
    },
    "colony": {
      "water": 15,
      "food": 15,
      "wood": 0,
      "players": [
        {
          "number": 0,
          "state": 1,
          "has_bucket": false,
          "has_axe": false,
          "has_fishing_rod": false
        }
      ]
    }
  },
  "turns": [
    {
      "day": 1,
      "actions": [
        {
          "player_id": 0,
          "action_id": 0
        }
      ],
      "night_state": {
        "world": {
          "water": 4985,
          "food": 4990,
          "wood": 5000,
          "weather": 1
        },
        "wreck": {
          "buckets": 1,
          "axes": 1,
          "fishing_rods": 1
        },
        "colony": {
          "water": 25,
          "food": 20,
          "wood": 0,
          "players": [
            {
              "number": 0,
              "state": 1,
              "has_bucket": false,
              "has_axe": false,
              "has_fishing_rod": false
            }
          ]
        }
      }
    }
  ]
}
```