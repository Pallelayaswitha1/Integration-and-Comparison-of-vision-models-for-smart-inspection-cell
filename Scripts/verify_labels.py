import cv2, os
from glob import glob

imglist = glob("dataset/images/val/*.png")
for img in imglist[:200]:
    base = os.path.splitext(os.path.basename(img))[0]
    lbl = f"dataset/labels/val/{base}.txt"
    im = cv2.imread(img)
    h,w = im.shape[:2]
    if os.path.exists(lbl):
        for line in open(lbl):
            cls,xc,yc,ww,hh = map(float,line.split())
            x1 = int((xc-ww/2)*w); y1 = int((yc-hh/2)*h)
            x2 = int((xc+ww/2)*w); y2 = int((yc+hh/2)*h)
            cv2.rectangle(im,(x1,y1),(x2,y2),(0,255,0),2)
            cv2.putText(im,str(int(cls)),(x1,y1-5),cv2.FONT_HERSHEY_SIMPLEX,0.5,(0,255,0),1)
    cv2.imshow("preview", im)
    if cv2.waitKey(0) & 0xFF==27:
        break
cv2.destroyAllWindows()
