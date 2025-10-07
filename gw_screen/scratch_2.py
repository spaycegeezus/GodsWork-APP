from dotenv import load_dotenv
import os

load_dotenv()

print("Layer 1:", os.getenv("LAYER1_PASS"))
print("Layer 2:", os.getenv("LAYER2_PASS"))
print("Pepper:", os.getenv("PEPPER_PASS"))
