# robodk_spawn_scaled_steps_on_conveyor.py
# Paste into RoboDK: Program -> Add Python Program -> Run
import os, time
from robolink import Robolink
from robodk import transl

RDK = Robolink()

# -------------------- USER PARAMETERS --------------------
STEP_FOLDER = "/home/sai/RoboDK/dataset_raw/gear_master_files"   # <-- change to folder containing .stl /.step files
CONVEYOR_FRAME_NAME = "Conveyor_Frame"      # <-- name of conveyor frame in RoboDK station
INTERVAL_S = 4.0                            # seconds between spawning parts
START_X = 0.0                               # X start position (mm) in conveyor frame local coords
SPACING = 150.0                             # spacing in X (mm) between successive spawned parts
Z_ABOVE_BELT = 30.0                         # height (mm) above conveyor surface to place spawned parts
MAX_SPAWNS = 50                             # maximum number of parts to spawn (safety limit)
RANDOM_ORDER = False                        # set True to randomize file order
REMOVE_EXISTING_SPAWNED = False             # if True, remove previously spawned items at start
SCALE_FACTOR = .2                        # <-- Uniform scale to apply to each imported object
FILE_EXTS = ('.stl')  # accepted file types
# ---------------------------------------------------------

# Validate folder
if not os.path.isdir(STEP_FOLDER):
    raise FileNotFoundError("STEP_FOLDER not found: " + STEP_FOLDER)

# Find conveyor frame in RoboDK
try:
    conveyor = RDK.Item(CONVEYOR_FRAME_NAME)
except Exception as e:
    raise SystemExit("Conveyor frame '{}' not found in station. Create it and retry.".format(CONVEYOR_FRAME_NAME))

# Find files
files = [f for f in os.listdir(STEP_FOLDER) if f.lower().endswith(FILE_EXTS)]
files.sort()
if not files:
    raise SystemExit("No files with extensions {} found in: {}".format(FILE_EXTS, STEP_FOLDER))

if RANDOM_ORDER:
    import random
    random.shuffle(files)

# Optionally remove previous spawned items to start clean
if REMOVE_EXISTING_SPAWNED:
    all_items = RDK.ItemList()
    for item_name in all_items:
        if isinstance(item_name, str) and item_name.startswith("SPAWN_"):
            try:
                it = RDK.Item(item_name)
                it.Delete()
            except:
                pass

print("Spawning {} files from '{}'".format(len(files), STEP_FOLDER))

spawn_count = 0
for idx, fname in enumerate(files):
    if spawn_count >= MAX_SPAWNS:
        print("Reached MAX_SPAWNS limit ({}). Stopping.".format(MAX_SPAWNS))
        break

    full_path = os.path.join(STEP_FOLDER, fname)
    print("Loading:", full_path)

    try:
        new_obj = RDK.AddFile(full_path, conveyor)   # parent = conveyor frame
    except Exception as e:
        print("Failed to AddFile:", e)
        continue

    try:
        if new_obj.Valid():
            # Apply uniform scale immediately
            try:
                # Scale expects a vector [sx, sy, sz]
                new_obj.Scale([SCALE_FACTOR, SCALE_FACTOR, SCALE_FACTOR])
                print(f"Applied scale factor {SCALE_FACTOR} to '{fname}'")
            except Exception as e:
                print("Warning: could not apply scale:", e)

            # compute pose in conveyor local coordinates
            x_pos = START_X + spawn_count * SPACING
            local_pose = transl(x_pos, 0.0, Z_ABOVE_BELT)

            # Try to set pose relative to conveyor
            try:
                # Some RoboDK versions accept setPose relative to parent if AddFile parent was specified.
                new_obj.setPose(local_pose)
            except Exception:
                # Fallback: set absolute pose using conveyor.Pose() * local_pose
                try:
                    conv_pose = conveyor.Pose()
                    new_obj.setPose(conv_pose * local_pose)
                except Exception as e:
                    print("Warning: could not set pose relative to conveyor:", e)

            # Rename spawned item with a recognizable prefix
            try:
                base_name = os.path.splitext(fname)[0]
                spawn_name = f"SPAWN_{spawn_count:03d}_{base_name}"
                # setName might be setName or set_name depending on version; try both fallbacks
                try:
                    new_obj.setName(spawn_name)
                except Exception:
                    try:
                        new_obj.set_name(spawn_name)
                    except Exception:
                        pass
            except Exception as e:
                print("Warning: could not rename object:", e)

            print(f"Spawned '{fname}' as {spawn_name} at x={x_pos} mm")
            spawn_count += 1
        else:
            print("AddFile returned invalid object for:", fname)
    except Exception as e:
        print("Exception handling spawned object:", e)

    # Wait interval before spawning next part
    print(f"Waiting {INTERVAL_S:.1f} s before next spawn...")
    time.sleep(INTERVAL_S)

print("Spawning complete. Total spawned:", spawn_count)

