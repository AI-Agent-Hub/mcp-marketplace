# Tools Schema

## Claude Format

doc: https://docs.anthropic.com/en/docs/agents-and-tools/tool-use/overview

## Schema
```
      {
        "name": "get_weather",
        "description": "Get the current weather in a given location",
        "input_schema": {
          "type": "object",
          "properties": {
            "location": {
              "type": "string",
              "description": "The city and state, e.g. San Francisco, CA"
            }
          },
          "required": ["location"]
        }
      }
```

```
{
            'name': 'get_historical_crypto_prices',
            'description': 'Gets historical prices for a crypto currency.\n\n    Args:\n        ticker: Ticker symbol of the crypto currency (e.g. BTC-USD). The list of available crypto tickers can be retrieved via the get_available_crypto_tickers tool.\n        start_date: Start date of the price data (e.g. 2020-01-01)\n        end_date: End date of the price data (e.g. 2020-12-31)\n        interval: Interval of the price data (e.g. minute, hour, day, week, month)\n        interval_multiplier: Multiplier of the interval (e.g. 1, 2, 3)\n    ',
            'inputSchema': {
                'properties': {
                    'ticker': {
                        'title': 'Ticker',
                        'type': 'string'
                    },
                    'start_date': {
                        'title': 'Start Date',
                        'type': 'string'
                    },
                    'end_date': {
                        'title': 'End Date',
                        'type': 'string'
                    },
                    'interval': {
                        'default': 'day',
                        'title': 'Interval',
                        'type': 'string'
                    },
                    'interval_multiplier': {
                        'default': 1,
                        'title': 'Interval Multiplier',
                        'type': 'integer'
                    }
                },
                'required': ['ticker', 'start_date', 'end_date'],
                'title': 'get_historical_crypto_pricesArguments',
                'type': 'object'
            }
        }, {
            'name': 'get_current_crypto_price',
            'description': 'Get the current / latest price of a crypto currency.\n\n    Args:\n        ticker: Ticker symbol of the crypto currency (e.g. BTC-USD). The list of available crypto tickers can be retrieved via the get_available_crypto_tickers tool.\n    ',
            'inputSchema': {
                'properties': {
                    'ticker': {
                        'title': 'Ticker',
                        'type': 'string'
                    }
                },
                'required': ['ticker'],
                'title': 'get_current_crypto_priceArguments',
                'type': 'object'
            }
        }, {
            'name': 'get_sec_filings',
            'description': 'Get all SEC filings for a company.\n\n    Args:\n        ticker: Ticker symbol of the company (e.g. AAPL, GOOGL)\n        limit: Number of SEC filings to return (default: 10)\n        filing_type: Type of SEC filing (e.g. 10-K, 10-Q, 8-K)\n    ',
            'inputSchema': {
                'properties': {
                    'ticker': {
                        'title': 'Ticker',
                        'type': 'string'
                    },
                    'limit': {
                        'default': 10,
                        'title': 'Limit',
                        'type': 'integer'
                    },
                    'filing_type': {
                        'anyOf': [{
                            'type': 'string'
                        }, {
                            'type': 'null'
                        }],
                        'default': None,
                        'title': 'Filing Type'
                    }
                },
                'required': ['ticker'],
                'title': 'get_sec_filingsArguments',
                'type': 'object'
            }
```

