# Road Safety CLI

Command-line interface for the Road Safety Intervention AI system.

## Installation

```bash
pip install -e .
```

## Configuration

Set your API URL and key:

```bash
road-safety config set api_url http://localhost:8000
road-safety config set api_key your_api_key_here
```

## Usage

### Search for interventions

```bash
road-safety search query "faded stop sign on highway"
```

### Interactive mode

```bash
road-safety interactive start
```

### Show version

```bash
road-safety version
```

### Configuration management

```bash
# Show all config
road-safety config show

# Set a value
road-safety config set api_url http://localhost:8000

# Get a value
road-safety config get api_url
```

## Examples

```bash
# Basic search
road-safety search query "damaged speed breaker"

# Search with filters
road-safety search query "faded marking" --category "Road Marking" --speed-min 50 --speed-max 100

# JSON output
road-safety search query "missing sign" --format json

# Interactive mode
road-safety interactive start
```
