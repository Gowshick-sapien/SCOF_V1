# SCOF Consensus Engine (CD²F)

The Consensus-Driven Collaborative Decision Framework (CD²F) arbitration engine.

## Usage

Run tests:
```bash
pytest tests/
```

Run CLI against fixture:
```bash
python -m src.main --fixture fixtures/agreement_case.json
```

Run server:
```bash
uvicorn src.main:app --host 0.0.0.0 --port 8020
```
