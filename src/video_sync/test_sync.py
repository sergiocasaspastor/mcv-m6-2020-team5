import cv2
import numpy as np
from dataset_video import dataset_video


def get_starting_video_offsets(filename):
    
    offsets = []
    with open(filename,"r") as offset_file:
        lines = offset_file.readlines()
        for line in lines:
            cam_name, cam_offset = line.split()
            cam_offset = cam_offset.replace(".","") # numbers have the thousand dot
            offsets.append(int(cam_offset))
    return offsets


def main():
    
    video_path_list = []
    video_path_list.append("../datasets/AIC20_track3_MTMC/AIC20_track3/train/S01/c001/vdo.avi")
    video_path_list.append("../datasets/AIC20_track3_MTMC/AIC20_track3/train/S01/c002/vdo.avi")
    video_path_list.append("../datasets/AIC20_track3_MTMC/AIC20_track3/train/S01/c003/vdo.avi")
    video_path_list.append("../datasets/AIC20_track3_MTMC/AIC20_track3/train/S01/c004/vdo.avi")
    video_path_list.append("../datasets/AIC20_track3_MTMC/AIC20_track3/train/S01/c005/vdo.avi")
    
    video_offset_list = np.array(get_starting_video_offsets("../datasets/AIC20_track3_MTMC/AIC20_track3/cam_timestamp/S01.txt"))
    
    minval = np.max(video_offset_list[1:])
    # video_offset_list = video_offset_list - minval
    video_offset_list[0] = 4000
    
    video_list = []
    for path,offset in zip(video_path_list,video_offset_list):
        video_list.append(dataset_video(path,offset))
    
    

    while(all([vid.video_capture.isOpened() for vid in video_list])):
        
        frames = []
        images_correct = True
        for vid in video_list:
            ret, frame = vid.video_capture.read()
            frames.append(frame)
            images_correct *= ret
        
        for i,frame in enumerate(frames):
            frame = cv2.resize(frame,(480,270))
            cv2.imshow(str(i),frame)
        cv2.waitKey()

    



if __name__ == "__main__":
    main()