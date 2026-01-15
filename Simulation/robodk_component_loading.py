from robolink import *      # RoboDK API
from robodk import *        # Math toolbox
import os, time

# Connect to RoboDK
RDK = Robolink()

# Define folder path containing STL files
STL_FOLDER = "/home/sai/cham/DIT/2nd_sem/case study intelligent system/project_casestudy/Integration-and-Comparison-of-vision-models-for-smart-inspection-cell/Simulation/gear_master_files"

# Define the reference frame for placement (e.g., Conveyor frame)
FRAME_NAME = "Conveyor_Frame"
frame_ref = RDK.Item(FRAME_NAME, ITEM_TYPE_FRAME)

# Define starting position (x, y, z)
start_pose = transl(0, 0, 0)
x_step = 200  # Distance (mm) between each part along conveyor

# Loop through all STL files in the folder
stl_files = sorted([f for f in os.listdir(STL_FOLDER) if f.endswith(".stl")])

for i, file_name in enumerate(stl_files):
    full_path = os.path.join(STL_FOLDER, file_name)
    print(f"Loading {file_name} into RoboDK...")

    # Load the STL file as a 3D object
    gear_obj = RDK.AddFile(full_path, parent=frame_ref)

    if gear_obj.Valid():
        # Calculate position offset for each gear
        new_pose = start_pose * transl(i * x_step, 0, 0)
        gear_obj.setPose(new_pose)

        print(f"Placed {file_name} at position {i * x_step} mm on conveyor.")
    else:
        print(f"Failed to load {file_name}")

    # Wait a few seconds before loading next part (simulate conveyor timing)
    time.sleep(3)  # 3-second interval between parts

print("✅ All STL parts loaded successfully!")
