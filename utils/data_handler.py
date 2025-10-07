import json
import os
from datetime import datetime
import sqlite3
from abc import ABC, abstractmethod
from gw_screen.adapters.json_adapter import JSONAdapter
from gw_screen.adapters.sqlite_adapter import SQLiteAdapter
from gw_screen.adapters.cassandra_adapter import CassandraAdapter
from gw_screen.adapters.recycle_view import RecycleView

# this is data_handler.py

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, '..', 'data')

ANON_FILE = os.path.join(DATA_DIR, 'anonymous_data.json')
USER_FILE = os.path.join(DATA_DIR, 'user_data.json')

PREDEFINED_TASKS = {
    "Food Preparation": [
        {"name": "Processing Onions per 1 kg", "weight": 1,  "joules": 130, "description": "Manual peeling of medium onions"},
        {"name": "Curdling Tofu per 1 kg", "weight": 1, "joules": 100, "description": "Preparing soy milk and coagulating"},
        {"name": "Processing Potatoes per 1 kg", "weight": 1, "joules": 150, "description": "Washing and peeling potatoes"},
        {"name": "Processing Corn Tortillas per 1 kg", "weight": 1, "joules": 1500, "description": "Collect corn, mill, and press"},
        {"name": "Processing Almonds per 1 kg", "weight": 1, "joules": 300, "description": "Collect, shell, wash and dry almonds"},
        {"name": "Processing Cherry Tomatoes per 1 kg", "weight": 1, "joules": 40, "description": "Wash, cut, and package tomatoes"},
        {"name": "Processing Cucumber per 1 kg", "weight": 1, "joules": 40, "description": "Wash, cut, and store cucumbers"},
        {"name": "Processing Rice per 1 kg", "weight": 1, "joules": 300, "description": "Sort, rinse, and cook rice"},
        {"name": "Processing Tomato Sauce per 1 kg", "weight": 1, "joules": 300, "description": "Chop, cook, press, and bottle tomatoes"},
        {"name": "Processing Mozzarella Cheese per 1 kg", "weight": 1, "joules": 753, "description": "Milk cow, prepare curds, and strain"},
        {"name": "Processing Ground Beef per 1 kg", "weight": 1, "joules": 700, "description": "Butcher, grind, and package beef"},
        {"name": "Processing Blueberries per 1 kg", "weight": 1, "joules": 50, "description": "Pick, rinse, and package"},
        {"name": "Processing Watermelon per 1 kg", "weight": 1, "joules": 20, "description": "Clean, slice, and store"},
        {"name": "Processing Strawberries per 1 kg", "weight": 1, "joules": 75, "description": "Pick, rinse, sort"},
        {"name": "Processing Peanuts per 1 kg", "weight": 1, "joules": 90, "description": "Wash, shell, roast"},
        {"name": "Processing Peaches per 1 kg", "weight": 1, "joules": 60, "description": "Pick, rinse, and trim"},
        {"name": "Processing Coffee per 1 kg", "weight": 1, "joules": 1200, "description": "Hull, roast, grind"},
        {"name": "Processing Oranges per 1 kg", "weight": 1, "joules": 70, "description": "Pick, clean, and pack"},
        {"name": "Processing Apple per 1 kg", "weight": 1, "joules": 55, "description": "Pick, rinse, and inspect"},
        {"name": "Processing Squash per 1 kg", "weight": 1, "joules": 45, "description": "Clean and trim"},
        {"name": "Processing Pumpkin per 1 kg", "weight": 1, "joules": 60, "description": "Scoop, wash, and store"},
        {"name": "Processing Eggplant per 1 kg", "weight": 1, "joules": 50, "description": "Clean, cut, store"},
        {"name": "Processing Peas per 1 kg", "weight": 1, "joules": 65, "description": "Pick and shell peas"},
        {"name": "Processing Grape per 1 kg", "weight": 1, "joules": 40, "description": "Rinse, and pack"},
        {"name": "Processing Kiwi per 1 kg", "weight": 1, "joules": 45, "description": "Pick and peel"},
        {"name": "Processing Pineapple per 1 kg", "weight": 1, "joules": 85, "description": "Trim, core, and package"},
        {"name": "Processing Blackberries per 1kg", "weight": 1, "joules": 60, "description": "Sort, clean, and package"},
        {"name": "Processing Raspberries per 1kg", "weight": 1, "joules": 65, "description": "Clean, sort, and package"},
        {"name": "Processing Feta per 1 kg", "weight": 1, "joules": 100, "description": "Curdle, press, and salt"},
        {"name": "Processing Carrots per 1 kg", "weight": 1, "joules": 60, "description": "Rinse, peel, and store"},
        {"name": "Processing Avocado per 1 kg", "weight": 1, "joules": 40, "description": "Pick, sort, and clean"},
        {"name": "Processing Tofu per 1 kg", "weight": 1, "joules": 150, "description": "Coagulate, press, and cut"},
        {"name": "Processing Cheddar per 1 kg", "weight": 1, "joules": 850, "description": "Milk, culture, cut curds, press"},
        {"name": "Processing Swiss per 1 kg", "weight": 1, "joules": 900, "description": "Milk, cook curds, age with holes"},
        {"name": "Processing Gouda per 1 kg", "weight": 1, "joules": 870, "description": "Heat curds, press, age in brine"},
        {"name": "Processing Havarti per 1 kg", "weight": 1, "joules": 880, "description": "Cultured, cut curds, washed and aged"},
        {"name": "Processing Ham per 1 kg", "weight": 1, "joules": 950, "description": "Butcher, brine, smoke or bake"},
        {"name": "Processing Ground Chicken per 1 kg", "weight": 1, "joules": 650, "description": "Butcher, de-bone, grind"},
        {"name": "Processing Cocoa per 1 kg", "weight": 1, "joules": 1100, "description": "Ferment, dry, roast, winnow, grind"},
        {"name": "Processing Olive Oil per 1 kg", "weight": 1, "joules": 1000, "description": "Crush, press, bottle"},
        {"name": "Processing Butter per 1 kg", "weight": 1, "joules": 400, "description": "Churn cream, wash, and pack"},
    ],

    "Sanitation": [
        {"name": "Washing Dishes - 10 Minutes", "joules": 250, "description": "Hand-washing in a single basin, typical household level"},
        {"name": "Washing Dishes - 30 Minutes", "joules": 650, "description": "Longer session, includes drying and stacking"},
        {"name": "Sweeping Floor - 10 Minutes", "joules": 200, "description": "Basic dust and debris collection"},
        {"name": "Mopping Floor - 10 Minutes", "joules": 300, "description": "Using mop and bucket over tile or vinyl surface"},
        {"name": "Scrubbing Floor - 10 Minutes", "joules": 350, "description": "Heavy effort on knees, soap and brush"},
        {"name": "Cleaning Bathroom - 30 Minutes", "joules": 600, "description": "Includes toilet, sink, mirror, tub"},
        {"name": "Disinfecting High-Touch Surfaces - 15 Minutes", "joules": 300, "description": "Doorknobs, switches, handrails, etc."},
        {"name": "Cleaning Windows - 20 Minutes", "joules": 350, "description": "Glass, edges, and tracks"},
        {"name": "Vacuuming Carpet - 10 Minutes", "joules": 250, "description": "Standard upright or canister vacuum"},
        {"name": "Cleaning Refrigerator - 30 Minutes", "joules": 500, "description": "Remove items, clean shelves, discard spoiled food"},
        {"name": "Taking Out Trash - 1 Bag", "joules": 180, "description": "Collect, tie, and carry to bin"},
        {"name": "Taking Out Recycling - 1 Bag", "joules": 160, "description": "Sort, flatten, and carry"},
        {"name": "Sanitizing Tools & Handles - 10 Minutes", "joules": 200, "description": "Shared or public-use items"},
        {"name": "Cleaning Walls & Baseboards - 20 Minutes", "joules": 400, "description": "Wiping down surfaces at low height"},
        {"name": "Washing Laundry - 1 Load (Manual/Hand)", "joules": 700, "description": "Soak, scrub, rinse, and wring"},
        {"name": "Washing Laundry - 1 Load (Machine)", "joules": 250, "description": "Sort, load, detergent, and start machine"},
        {"name": "Drying & Folding Laundry - 1 Load", "joules": 300, "description": "Hang dry or machine fold and sort"},
        {"name": "Organizing Storage or Closet - 30 Minutes", "joules": 450, "description": "Decluttering and cleaning spaces"},
        {"name": "Picking Up Debris (Tier 1) - per 1kg", "joules": 200, "description": "Litter, wrappers, and light debris"},
        {"name": "Picking Up Debris (Tier 2) - per 1kg", "joules": 300, "description": "Broken glass, heavy plastic, wood scraps"},
        {"name": "Picking Up Debris (Tier 3) - per 1kg", "joules": 450, "description": "Metal scraps, sharp or bulky items"},
        {"name": "Cleaning Animal Waste - 10 Minutes", "joules": 280, "description": "Scooping, bagging, and sanitizing area"},
        {"name": "Unclogging Drain or Sink - 15 Minutes", "joules": 350, "description": "Using plunger or manual tools"},
        {"name": "Cleaning Exterior Entryway - 20 Minutes", "joules": 400, "description": "Steps, porch, welcome mat"},
        {"name": "Wall Scrubbing - 30 Minutes", "joules": 600, "description": "Scrubbing walls, paint removal"},
        {"name": "Pressure Washing Surfaces - 20 Minutes", "joules": 500, "description": "Driveways, siding, or sidewalks"},
        {"name": "Clearing Drainage or Gutters - 30 Minutes", "joules": 700, "description": "Ladder work, removal of leaves and sludge"}

    ],

    "Agriculture": [
        {"name": "Tilling: Extremely Shallow (surface raking of seeds per 10 Minutes)", "joules": 100},
        {"name": "Tilling per plant: Shallow (Less than 12 cm)", "joules": 100},
        {"name": "Tilling per plant: Moderate (Over 12 cm deep less than 100 cm)", "joules": 300},
        {"name": "Tilling per plant: Deep(Over 1 meter)", "joules": 1000},
        {"name": "Tilling per plant: Machine Assisted(per 30 Minute increment)", "joules": 200},
        {"name": "Watering Garden per day", "joules": 30},
        {"name": "Watering field per 1kg of Potatoes", "joules": 65},
        {"name": "Watering field per 1kg of Beans", "joules": 250},
        {"name": "Watering field per 1kg of Corn", "joules": 300},
        {"name": "Watering field per 1kg of Bananas", "joules": 380},
        {"name": "Watering Garden per day", "joules": 30},
        {"name": "Watering Garden per day", "joules": 30},
        {"name": "Watering Garden per day", "joules": 30},
        {"name": "Harvesting Onions 1kg", "joules": 80, "description": "Dig up onions, trim tops, and wash"},
        {"name": "Harvesting Potatoes 1kg", "joules": 100, "description": "Dig and lift potatoes, wash off soil"},
        {"name": "Harvesting Blueberries 1kg", "joules": 60, "description": "Pick by hand and carry"},
        {"name": "Harvesting Strawberries 1kg", "joules": 65, "description": "Pick gently by hand, carry to crate"},
        {"name": "Harvesting Watermelon 1kg", "joules": 40, "description": "Lift, check ripeness, and cut from vine"},
        {"name": "Harvesting Peaches 1kg", "joules": 50, "description": "Climb, pick, and inspect for bruises"},
        {"name": "Harvesting Apples 1kg", "joules": 45, "description": "Pick from tree, inspect, and sort"},
        {"name": "Harvesting Oranges 1kg", "joules": 55, "description": "Pick, twist from stem, and sort"},
        {"name": "Harvesting Coffee 1kg", "joules": 500, "description": "Pick red cherries by hand from bushes"},
        {"name": "Harvesting Peanuts 1kg", "joules": 120, "description": "Pull plant, shake soil, hang to dry"},
        {"name": "Harvesting Pumpkin 1kg", "joules": 65, "description": "Cut from vine and carry to storage"},
        {"name": "Harvesting Squash 1kg", "joules": 55, "description": "Cut, lift, and transport to basket"},
        {"name": "Harvesting Eggplant 1kg", "joules": 50, "description": "Clip stem, check for firmness"},
        {"name": "Harvesting Cucumber 1kg", "joules": 50, "description": "Twist or clip, inspect, and carry"},
        {"name": "Harvesting Grape 1kg", "joules": 45, "description": "Cut clusters carefully and place in tray"},
        {"name": "Harvesting Kiwi 1kg", "joules": 60, "description": "Twist fruit from vine and place in basket"},
        {"name": "Harvesting Pineapple 1kg", "joules": 90, "description": "Cut with machete and lift carefully"},
        {"name": "Harvesting Raspberries 1kg", "joules": 65, "description": "Pick fragile berries by hand"},
        {"name": "Harvesting Blackberries 1kg", "joules": 60, "description": "Handle thorny bushes and pick carefully"},
        {"name": "Harvesting Cherry Tomatoes 1kg", "joules": 35, "description": "Pluck tomatoes and place in container"},
        {"name": "Harvesting Carrots 1kg", "joules": 75, "description": "Pull from soil, rinse, and trim leaves"},
        {"name": "Harvesting Avocado 1kg", "joules": 50, "description": "Twist off stem and place gently"},
        {"name": "Harvesting Peas 1kg", "joules": 70, "description": "Pick pods individually and gather"},
        {"name": "Harvesting Almonds 1kg", "joules": 180, "description": "Shake tree, collect, and husk"},
        {"name": "Harvesting Cocoa 1kg", "joules": 300, "description": "Cut pods from tree, scoop beans"},

    ],
    "Exercise": [
        {"name": "15 Minutes Cardio", "joules": 350, "description": "Jogging, jumping jacks, or similar"},
        {"name": "Stretching Routine - 15 Minutes", "joules": 150, "description": "Full-body flexibility sequence"},
        {"name": "100 Meter Sprint", "joules": 7500, "description": "High-intensity short-distance sprint"},
        {"name": "10 Push-ups", "joules": 50, "description": "Standard bodyweight push-ups"},
        {"name": "1 Hour Walking (Smooth Terrain)", "joules": 850, "description": "Park or flat ground walking"},
        {"name": "1 Hour Walking (Treadmill)", "joules": 500, "description": "Indoor, consistent pace"},
        {"name": "1 Hour Walking (Rugged Terrain)", "joules": 7500, "description": "Uneven surface, inclines, natural terrain"},
        {"name": "Carrying Weighted Bags (23kg) - 3 Miles", "joules": 60300, "description": "Manual transport of heavy goods"},
        {"name": "Tree Climbing - 30 Minutes", "joules": 2800, "description": "Full-body, vertical effort"},
        {"name": "Moderate Swimming - 10 Minutes", "joules": 500, "description": "Steady, continuous pace"},
        {"name": "Vigorous Swimming - 10 Minutes", "joules": 900, "description": "High-effort, lap-style swim"},
        {"name": "Digging Soil - 30 Minutes", "joules": 1600, "description": "Using shovel for garden or trench"},
        {"name": "Shoveling Snow - 20 Minutes", "joules": 1200, "description": "Manual snow removal effort"},
        {"name": "Biking - 1 Hour Leisure", "joules": 900, "description": "Flat terrain, moderate pace"},
        {"name": "Biking - 1 Hour Uphill", "joules": 2800, "description": "Intense climb and descent"},
        {"name": "Jump Rope - 15 Minutes", "joules": 750, "description": "Continuous jumping with rope"},
        {"name": "Carrying Firewood - 20 Minutes", "joules": 1900, "description": "Load and carry wood bundles"},
        {"name": "Lifting Weights - 30 Minutes", "joules": 2200, "description": "Strength training with dumbbells/barbell"},
        {"name": "Pull-ups - 10 Reps", "joules": 100, "description": "Bodyweight upper body lift"},
        {"name": "Squats - 20 Reps", "joules": 120, "description": "Bodyweight squat or resistance"},
        {"name": "Yoga - 30 Minutes", "joules": 250, "description": "Calm breathing and stretching postures"},
        {"name": "Aerobics - 30 Minutes", "joules": 600, "description": "Instructor-led or solo dance/cardio"},
        {"name": "Hiking - 1 Hour", "joules": 1800, "description": "Trail walking with elevation change"},
        {"name": "Canoeing/Kayaking - 1 Hour", "joules": 2200, "description": "Paddling through water manually"},
        {"name": "Wheelbarrow Pushing - 15 Minutes", "joules": 900, "description": "Transporting dirt or tools"},
        {"name": "Manual Lawn Mowing - 30 Minutes", "joules": 1800, "description": "Push mower, uneven lawn"},
        {"name": "Sledgehammering - 15 Minutes", "joules": 2200, "description": "Heavy manual demolition"},
        {"name": "Car Washing - 20 Minutes", "joules": 750, "description": "Manual wash and dry"},
        {"name": "Tire Flipping - 10 Minutes", "joules": 2600, "description": "Extreme strength training task"},
        {"name": "Basketball Game - 30 Minutes (Point Guard)", "joules": 1900, "description": "Half-court game with running, passing, and jumping"},
        {"name": "Basketball Game - 30 Minutes (Center)", "joules": 1500, "description": "Half-court game, mostly under the basket, less running"},
        {"name": "Soccer Match - 30 Minutes (Goalkeeper)", "joules": 800, "description": "Limited movement, guarding goal"},
        {"name": "Soccer Match - 30 Minutes (Defender)", "joules": 1600, "description": "Positioning, sprinting, intercepting"},
        {"name": "Soccer Match - 30 Minutes (Midfielder)", "joules": 2200, "description": "High movement, sprinting, passing"},
        {"name": "Soccer Match - 30 Minutes (Forward)", "joules": 2000, "description": "Attacking, sprints, shooting"},
        {"name": "American Football - 30 Minutes (Quarterback)", "joules": 600, "description": "Short bursts, throwing, limited running"},
        {"name": "American Football - 30 Minutes (Running Back)", "joules": 1400, "description": "Frequent sprints, carrying the ball"},
        {"name": "American Football - 30 Minutes (Wide Receiver)", "joules": 1200, "description": "Sprints, route running, catching"},
        {"name": "American Football - 30 Minutes (Lineman)", "joules": 800, "description": "Short explosive pushes and blocks"},
        {"name": "Tennis Match - 30 Minutes (Singles)", "joules": 1600, "description": "Full-court play, lateral movement, volleys"},
        {"name": "Tennis Match - 30 Minutes (Doubles)", "joules": 1200, "description": "Shared court, less running"},
        {"name": "Volleyball Game - 30 Minutes", "joules": 1200, "description": "Jumping, diving, and quick reactions"},
        {"name": "Baseball/Softball Game - 30 Minutes (Pitcher)", "joules": 700, "description": "Pitching and movement in the circle"},
        {"name": "Baseball/Softball Game - 30 Minutes (Catcher)", "joules": 650, "description": "Squatting, catching, throws"},
        {"name": "Baseball/Softball Game - 30 Minutes (Infielders)", "joules": 900, "description": "Running to field balls and throw"},
        {"name": "Baseball/Softball Game - 30 Minutes (Outfielders)", "joules": 1000, "description": "Chasing fly balls and running"},
        {"name": "Swimming Race - 100m Freestyle", "joules": 500, "description": "Maximum effort sprint swim"},
        {"name": "Swimming Race - 400m Freestyle", "joules": 2000, "description": "Sustained high-effort swim"},
        {"name": "Swimming Race - 1500m Freestyle", "joules": 7000, "description": "Endurance swim, moderate pace"},
        {"name": "Gymnastics - Floor Routine", "joules": 400, "description": "10 high-intensity actions"},
        {"name": "Gymnastics - Vault", "joules": 80, "description": "Single explosive effort"},
        {"name": "Gymnastics - Rings", "joules": 50, "description": "Strength holds and swings"},
        {"name": "Track Sprint - 100m", "joules": 300, "description": "Maximum intensity sprint"},
        {"name": "Track Middle Distance - 800m", "joules": 2000, "description": "Sustained effort with sprints"},
        {"name": "Track Long Distance - 10 km", "joules": 9000, "description": "Endurance run, moderate intensity"}
    ],

        "Mental and Artistic Tasks": [
        {"name": "Meditation (10 Minutes)", "joules": 60, "description": "Focus on breath or presence"},
        {"name": "Meditation (20 Minutes)", "joules": 120, "description": "Mindfulness or deep stillness"},
        {"name": "Meditation (30 Minutes)", "joules": 180, "description": "Extended conscious awareness"},
        {"name": "Journaling - 15 Minutes", "joules": 80, "description": "Reflective writing or gratitude log"},
        {"name": "Journaling - 30 Minutes", "joules": 180, "description": "Emotional processing or creative writing"},
        {"name": "Reading - 30 Minutes", "joules": 90, "description": "Fiction, non-fiction, or scripture"},
        {"name": "Reading - 1 Hour", "joules": 300},
        {"name": "Reading - 2 Hours", "joules": 700},
        {"name": "Reading - 3 Hours", "joules": 1900},
        {"name": "Reading - 4 Hours", "joules": 2900},
        {"name": "Drawing - 30 Minutes", "joules": 90},
        {"name": "Drawing - 1 Hour", "joules": 300},
        {"name": "Drawing - 2 Hours", "joules": 700},
        {"name": "Drawing - 3 Hours", "joules": 1900},
        {"name": "Drawing - 4 Hours", "joules": 2900},
        {"name": "Painting - 30 Minutes", "joules": 90},
        {"name": "Painting - 1 Hour", "joules": 300},
        {"name": "Painting - 2 Hours", "joules": 700},
        {"name": "Painting - 3 Hours", "joules": 1900},
        {"name": "Painting - 4 Hours", "joules": 2900},
        {"name": "Playing Instrument - 30 Minutes", "joules": 120, "description": "Piano, guitar, strings, etc."},
        {"name": "Playing Instrument - 1 Hour", "joules": 320},
        {"name": "Composing Music - 1 Hour", "joules": 350},
        {"name": "Coding - 1 Hour", "joules": 450, "description": "Software, logic, or creative scripting"},
        {"name": "Math/Science Study - 1 Hour", "joules": 500, "description": "Problem solving or comprehension"},
        {"name": "Philosophical Reflection - 1 Hour", "joules": 200, "description": "Contemplative thought and synthesis"},
        {"name": "Language Practice - 1 Hour", "joules": 400, "description": "Learning or speaking non-native language"},
        {"name": "Research and Note-taking - 1 Hour", "joules": 350},
        {"name": "Mind Mapping - 30 Minutes", "joules": 150, "description": "Visual brainstorming or system modeling"},
        {"name": "Therapy Session - 1 Hour", "joules": 250, "description": "Mental health support and unpacking"},
        {"name": "Guided Visualization - 20 Minutes", "joules": 100, "description": "Mental imagery with purpose"},
        {"name": "Memory Training - 20 Minutes", "joules": 150, "description": "Recitation, flashcards, pattern review"},
        {"name": "Strategic Planning - 30 Minutes", "joules": 180, "description": "Organizational or resource-focused"},
        {"name": "Modeling for Photography - 1 Hour", "joules": 450},
        {"name": "Modeling for Drawing - 1 Hour", "joules": 500},
        {"name": "Modeling for Painting - 1 Hour", "joules": 400},
        {"name": "Photography - Setup Lights, Canvas, or Props  - 1 Hour", "joules": 500},
        {"name": "Paperwork and Data Processing - 1 Hour", "joules": 300},
        {"name": "Photography - Composition and Capture - 1 Hour", "joules": 250},
        {"name": "Photography - Editing and Sharing - 1 Hour", "joules": 350},
        {"name": "Musical Instrument Practice and Composition - 1 Hour", "joules": 300},
        {"name": "Musical Recording and Producing - 1 Hour", "joules": 650},

        ],

    "Social Tasks": [
        {"name": "Active Listening (15 Minutes)", "joules": 150, "description": "Fully present, without interrupting"},
        {"name": "Active Listening (30 Minutes)", "joules": 300},
        {"name": "Conflict Resolution (Mediation, 30 Minutes)", "joules": 500, "description": "Acting as neutral third-party"},
        {"name": "Conflict Resolution (Direct, 30 Minutes)", "joules": 400, "description": "Resolving tensions with others calmly"},
        {"name": "Mentoring or Teaching - 30 Minutes", "joules": 400, "description": "Sharing knowledge or life skills"},
        {"name": "Mentoring or Teaching - 1 Hour", "joules": 750},
        {"name": "Community Meeting Participation - 1 Hour", "joules": 600, "description": "Speaking, listening, or voting"},
        {"name": "Hosting Discussion Circle - 1 Hour", "joules": 700, "description": "Facilitating group sharing"},
        {"name": "Team Collaboration - 1 Hour", "joules": 550, "description": "Working toward shared goals"},
        {"name": "Conflict De-escalation (in public)", "joules": 850, "description": "Intervening to calm potential escalation"},
        {"name": "Social Support (Companionship Visit - 1 Hour)", "joules": 450, "description": "Visiting elder, ill, or lonely person"},
        {"name": "Childcare Supervision - 1 Hour", "joules": 600, "description": "Monitoring and engaging with children"},
        {"name": "Emotional Support (Phone/Video Call - 30 Min)", "joules": 300, "description": "Compassionate conversation"},
        {"name": "Group Organizing (30 Minutes)", "joules": 350, "description": "Scheduling, coordinating people/tasks"},
        {"name": "Event Hosting (per hour)", "joules": 650, "description": "Facilitating guest comfort and flow"},
        {"name": "Welcoming New Member (30 Minutes)", "joules": 250, "description": "Introducing community values or spaces"},
        {"name": "Conflict Documentation (Written)", "joules": 300, "description": "Writing clear neutral summaries of events"},
        {"name": "Translating for Others - 30 Minutes", "joules": 500, "description": "Bridging communication across languages"},
        {"name": "Offering Mediation Services - 1 Hour", "joules": 900, "description": "Guided communication and resolution"},
        {"name": "Organizing Volunteer Effort - 1 Hour", "joules": 800, "description": "Planning collective help or outreach"},
        {"name": "Leading a Group Reflection - 1 Hour", "joules": 750, "description": "Holding space for dialogue or learning"},
        {"name": "Resource Distribution - 1 Hour", "joules": 800, "description": "Updating Database of Inventory while allocating resources"}

    ],

    "Construction & Handyman Services": [
        {"name": "Framing a Wall (per 8ft section)", "joules": 4000, "description": "Measure, cut, nail, level"},
        {"name": "Drywall Installation (per 4x8 sheet)", "joules": 2000, "description": "Lift, align, fasten, finish"},
        {"name": "Drywall Taping & Mud (per seam)", "joules": 800, "description": "Apply tape, mud, and smooth"},
        {"name": "Painting Interior Wall (per 100 sq ft)", "joules": 1500, "description": "Prep, cut, roll, and detail"},
        {"name": "Painting Exterior Wall (per 100 sq ft)", "joules": 2200, "description": "Wash, scrape, prime, and roll"},
        {"name": "Flooring Installation (laminate/tile, per 100 sq ft)", "joules": 3500, "description": "Cut, level, install"},
        {"name": "Demolition Work (1 Hour)", "joules": 4200, "description": "Tear down, remove debris, clear site"},
        {"name": "Roof Repair (1 Hour)", "joules": 5000, "description": "Climb, assess, patch, and reseal"},
        {"name": "Gutter Cleaning (per house)", "joules": 2500, "description": "Remove debris from roof drainage"},
        {"name": "Plumbing Repair (Minor – 1 Hour)", "joules": 4000, "description": "Fix leaks, replace fittings"},
        {"name": "Plumbing Install (Toilet or Sink)", "joules": 4500, "description": "Fit, seal, and test connections"},
        {"name": "Electrical Outlet Install", "joules": 3000, "description": "Cut, wire, mount, and test"},
        {"name": "Ceiling Fan Installation", "joules": 4000, "description": "Secure, wire, balance, and test"},
        {"name": "Assembling Furniture (per item)", "joules": 1500, "description": "Unbox, sort, align, and tighten"},
        {"name": "Installing Door (Interior)", "joules": 3500, "description": "Level, align, hang, adjust"},
        {"name": "Hanging Shelves (per unit)", "joules": 1000, "description": "Measure, drill, mount, anchor"},
        {"name": "Installing Baseboards (per 10ft)", "joules": 1200, "description": "Cut, miter, attach, caulk"},
        {"name": "Digging Post Holes (per 2 holes)", "joules": 3000, "description": "Dig to depth, clear debris"},
        {"name": "Concrete Mixing & Pouring (small slab)", "joules": 5000, "description": "Mix, pour, smooth, set"},
        {"name": "Fence Repair (10ft section)", "joules": 2500, "description": "Remove damaged pieces, replace slats"},
        {"name": "Window Replacement (per window)", "joules": 4200, "description": "Remove, insulate, level, secure"},
        {"name": "Tile Grouting (per 100 sq ft)", "joules": 2300, "description": "Apply grout, clean lines, seal"},
        {"name": "Installing Insulation (per 100 sq ft)", "joules": 3400, "description": "Fit, staple, seal"},
        {"name": "Installing Kitchen Sink Faucet", "joules": 3000, "description": "Detach old unit, plumb and seal new"},
        {"name": "Hanging Light Fixture", "joules": 2700, "description": "Wire safely, level, test"},
        {"name": "Installing Curtain Rods (per window)", "joules": 1000, "description": "Measure, mount, level"},
        {"name": "Yard Shed Assembly (small, prefab)", "joules": 6500, "description": "Frame, anchor, secure roof"},
        {"name": "Replacing Thermostat", "joules": 1800, "description": "Disconnect old, wire and test new"},
        {"name": "Caulking Windows/Doors (per 10ft)", "joules": 1200, "description": "Apply sealant, smooth, dry"},
    ]


}
import os
import json
import sqlite3
from datetime import datetime

# Define these constants at the top of your file
ANON_FILE = "data/anonymous.json"
USER_FILE = "data/users.json"

class AdapterFactory:
    @staticmethod
    def create_adapter(backend_type, **kwargs):
        if backend_type == "json":
            from gw_screen.adapters.json_adapter import JSONAdapter
            return JSONAdapter(**kwargs)
        elif backend_type == "sql":
            from gw_screen.adapters.sqlite_adapter import SQLiteAdapter
            return SQLiteAdapter(**kwargs)
        elif backend_type == "cassandra":
            from gw_screen.adapters.cassandra_adapter import CassandraAdapter
            return CassandraAdapter(**kwargs)
        else:
            raise ValueError(f"Unknown backend type: {backend_type}")


ACCOUNTS_PATH = "accounts.json"

class DataHandler:
    def __init__(self, backend='json', **kwargs):
        self.user_id = kwargs.pop('user_id', 'default_user')
        self.backend = backend

        # Use the factory pattern consistently
        self.adapter = AdapterFactory.create_adapter(backend)
        self.ensure_files()

    def switch_backend(self, backend_type):
        """Switch backend using the factory"""
        self.adapter = AdapterFactory.create_adapter(backend_type)
        self.backend = backend_type

    def ensure_files(self):
        os.makedirs(os.path.dirname(ANON_FILE), exist_ok=True)
        os.makedirs("data/profiles", exist_ok=True)
        for file in [ANON_FILE, USER_FILE]:
            if not os.path.exists(file):
                with open(file, 'w') as f:
                    json.dump({}, f)

    def user_exists(self, user_id):
        # Check JSON profile
        json_path = f"data/profiles/{user_id}.json"
        if os.path.exists(json_path):
            return True

        # Check SQLite DB
        try:
            from gw_screen import __init__ as gw_init
            db_path = gw_init.get_db_path()
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM users WHERE username = ?", (user_id,))
            exists = cursor.fetchone()[0] > 0
            conn.close()
            return exists
        except:
            return False

    def _load_data(self, file, user_id=None):
        try:
            with open(file, 'r') as f:
                data = json.load(f)
                return self._validate_structure(data, user_id)
        except (FileNotFoundError, json.JSONDecodeError):
            return {"tasks": [], "services": []} if not user_id else {user_id: {"tasks": [], "services": []}}

    def _validate_structure(self, data, user_id=None):
        if user_id:
            if user_id not in data or not isinstance(data[user_id], dict):
                data[user_id] = {"tasks": [], "services": [], "balance": 250000}
            else:
                data[user_id].setdefault("services", [])
                data[user_id].setdefault("tasks", [])
                data[user_id].setdefault("balance", 250000)
        else:
            if not isinstance(data, dict):
                return {"tasks": [], "services": []}
            data.setdefault("services", [])
            data.setdefault("tasks", [])
        return data

    def load_all_entries(self, user_id=None):
        services = self.load_services(user_id=user_id)
        tasks = self.load_tasks(user_id=user_id)

        tagged_services = [{"type": "service", **s} for s in services]
        tagged_tasks = [{"type": "task", **t} for t in tasks]

        return tagged_services + tagged_tasks

    def _save_data(self, file, data):
        with open(file, 'w') as f:
            json.dump(data, f, indent=4)

    def save_task(self, task_data, user_id=None):
        if user_id:
            profile = self.load_user_profile(user_id)
            profile.setdefault("tasks", [])
            profile["tasks"].append(task_data)
            self.save_user_profile(user_id, profile)
        else:
            data = self._load_data(ANON_FILE)
            data.setdefault("tasks", [])
            data["tasks"].append(task_data)
            self._save_data(ANON_FILE, data)

    def save_service(self, service_data, user_id=None):
        if user_id:
            profile = self.load_user_profile(user_id)
            profile.setdefault("services", [])
            profile["services"].append(service_data)
            self.save_user_profile(user_id, profile)
        else:
            data = self._load_data(ANON_FILE)
            data.setdefault("services", [])
            data["services"].append(service_data)
            self._save_data(ANON_FILE, data)

    def load_tasks(self, user_id=None):
        if user_id:
            profile = self.load_user_profile(user_id)
            return profile.get("tasks", [])
        else:
            data = self._load_data(ANON_FILE)
            return data.get("tasks", [])

    def load_services(self, user_id=None):
        if user_id:
            profile = self.load_user_profile(user_id)
            return profile.get("services", [])
        else:
            data = self._load_data(ANON_FILE)
            return data.get("services", [])

    def load_all_services(self):
        all_services = []

        # Load anonymous services
        anon_data = self._load_data(ANON_FILE)
        all_services.extend(anon_data.get("services", []))

        # Load user-specific services
        profiles_dir = "data/profiles"
        if os.path.exists(profiles_dir):
            for filename in os.listdir(profiles_dir):
                if filename.endswith(".json"):
                    user_id = filename[:-5]
                    profile = self.load_user_profile(user_id)
                    all_services.extend(profile.get("services", []))

        return all_services

    def get_user_balance(self, user_id, default=0):
        """Return the balance for a specific user_id."""
        profile = self.load_user_profile(user_id)
        return profile.get("balance", default)

    def load_balance_from_username(self):
        username = self.username_input.text.strip()
        if username:
            # This will automatically create profile with 250,000 balance if new user
            balance = self.data_handler.get_user_balance(username)
        else:
            balance = 250000
        self.update_balance()

    def set_user_balance(self, user_id, new_balance):
        """Set the balance for a specific user_id."""
        profile = self.load_user_profile(user_id)
        profile["balance"] = new_balance
        self.save_user_profile(user_id, profile)

    def add_to_balance(self, user_id, amount):
        """Increment a user's balance by amount (can be negative)."""
        balance = self.get_user_balance(user_id)
        self.set_user_balance(user_id, balance + amount)

    def load_user_profile(self, user_id):
        os.makedirs("data/profiles", exist_ok=True)
        path = f"data/profiles/{user_id}.json"

        if not os.path.exists(path):
            profile = {
                "username": user_id,
                "bio": "",
                "anonymize": False,
                "profile_pic": "LOGO.png",
                "theme": {
                    "bg_color": [1, 1, 1, 1],
                    "text_color": [1, 1, 0, 1],
                    "bg_image": "LogoBackground.jpg"
                },
                "balance": 250000,  # This should be 250000, not 0
                "tasks": [],
                "services": []
            }
            self.save_user_profile(user_id, profile)
            return profile

        with open(path, "r") as f:
            profile = json.load(f)

        profile.setdefault("tasks", [])
        profile.setdefault("services", [])
        profile.setdefault("balance", 250000)  # And here too
        profile.setdefault("theme", {
            "bg_color": [1, 1, 1, 1],
            "text_color": [1, 1, 0, 1],
            "bg_image": "LogoBackground.jpg"
        })
        return profile

    def save_user_profile(self, user_id, profile_data):
        os.makedirs("data/profiles", exist_ok=True)
        path = f"data/profiles/{user_id}.json"
        with open(path, "w") as f:
            json.dump(profile_data, f, indent=2)

    def overwrite_services(self, new_services, user_id=None):
        if user_id:
            profile = self.load_user_profile(user_id)
            profile["services"] = new_services
            self.save_user_profile(user_id, profile)
        else:
            data = self._load_data(ANON_FILE)
            data["services"] = new_services
            self._save_data(ANON_FILE, data)

    def log_self_reported_task(self, category, description, joules, user_id=None, kilograms=0, minutes=0):
        """Log a task either to a user's profile or the anonymous file."""
        task_data = {
            "category": category,
            "description": description,
            "joules": joules,
            "weight": kilograms,
            "time or units": minutes,
            "timestamp": datetime.utcnow().isoformat()
        }

        if user_id:
            profile = self.load_user_profile(user_id)
            profile.setdefault("tasks", [])
            profile["tasks"].append(task_data)
            self.save_user_profile(user_id, profile)
        else:
            data = self._load_data(ANON_FILE)
            data.setdefault("tasks", [])
            data["tasks"].append(task_data)
            self._save_data(ANON_FILE, data)