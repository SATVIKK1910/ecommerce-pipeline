#!/bin/bash
set -e
echo "=== Step 1: Generate Data ==="
python src/generate_data.py --customers 1000 --orders 5000 --seed 42 --out_dir data

echo "=== Step 2: Load into Postgres ==="
python src/load_data.py

echo "=== Step 3: Feature Pipeline ==="
python src/feature_pipeline.py

echo "=== Step 4: Train Model ==="
python src/train.py

echo "=== Pipeline Complete ==="
