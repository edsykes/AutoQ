import json
import sys

from .generator import WorldConfig, generate_world

if __name__ == "__main__":
    seed = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    json.dump(generate_world(WorldConfig(seed=seed)).to_dict(), sys.stdout, indent=1)
