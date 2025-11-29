import os, random, shutil
from glob import glob

random.seed(42)
src_root = "Integration-and-Comparison-of-vision-models-for-smart-inspection-cell/dataset/dataset_raw"   # folder containing gear_good, gear_dent, ...
dst_root = "Integration-and-Comparison-of-vision-models-for-smart-inspection-cell/dataset/"       # target dataset as above

splits = {"train":0.8, "val":0.1, "test":0.1}
os.makedirs(dst_root, exist_ok=True)
for s in splits: 
    os.makedirs(os.path.join(dst_root,"images",s), exist_ok=True)
    os.makedirs(os.path.join(dst_root,"labels",s), exist_ok=True)

for cls_folder in os.listdir(src_root):
    folder = os.path.join(src_root, cls_folder)
    if not os.path.isdir(folder): continue
    images = glob(os.path.join(folder, "*.png")) + glob(os.path.join(folder,"*.jpg"))
    random.shuffle(images)
    n = len(images)
    i=0
    for split,name in zip([int(splits["train"]*n), int((splits["train"]+splits["val"])*n), n],
                         ["train","val","test"]):
        chunk = images[i:split]
        for img in chunk:
            base = os.path.basename(img)
            # ensure unique names: prefix with class
            dst_img = os.path.join(dst_root,"images",name, f"{cls_folder}_{base}")
            shutil.copy2(img, dst_img)
            # if there is a label in original place, copy it too
            lbl = os.path.splitext(img)[0]+".txt"
            if os.path.exists(lbl):
                dst_lbl = os.path.join(dst_root,"labels",name, f"{cls_folder}_{os.path.basename(lbl)}")
                shutil.copy2(lbl, dst_lbl)
        i = split
