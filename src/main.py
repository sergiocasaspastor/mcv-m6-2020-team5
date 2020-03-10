# -*- coding: utf-8 -*-
"""
Created on Sat Feb 29 16:03:07 2020

@author: Group 5
"""
import cv2
import detectors as dts

from detectors.gt_modifications import obtain_gt, obtain_gt_without_static
from detectors.backgrounds import BGSTModule
from metrics.mAP import getMetricsClass
from metrics.graphs import LinePlot, iouFrame
import numpy as np

from display import print_func

from config import general as gconf

SOURCE = "../datasets/AICity_data/train/S03/c010/vdo.avi"

detectors = {"gt_noise":dts.gt_predict,
             "yolo": dts.yolo_predict,
             "ssd":  dts.ssd_predict,
             "rcnn": dts.rcnn_predict}

def main():
    INIT_AT = 535 # where to init computing IoU and mAP, after training the background
    # STOP_AT = 30*2.5+INIT_AT
    STOP_AT = -1
    RHO = 0 #If different than 0 then adaptive
    ALPHA = 4 #Try for different values (2.5 should be good)
    DELETE_STATIC_OBJECTS = gconf.gtruth.static # True: deletes static objects from ground truth

    DETECTOR = "gauss_black_rem"
    det_backgrounds = ["color_gauss_black_rem","gauss_black_rem", "MOG", "MOG2", "CNT", "GMG", "LSBP", "GSOC", "Subsense", "Lobster"]
    
    COLOR_SPACE = ['BGR','RGB','BGRA','RGBA','XYZ','YCBCR','HSV','LAB','LUV','HLS','YUV']
    cspace = COLOR_SPACE[0]
    
    SINGLE_CHANNEL = ['GRAY','HUE','L','Y','SATURATION'] #Añadir más
    schannel = SINGLE_CHANNEL[0]
    if(gconf.VISUALIZE):
        w_name = 'display'
        cv2.namedWindow(w_name, cv2.WINDOW_AUTOSIZE)
    bgsg_module = None
    
    # cap.set(cv2.CAP_PROP_POS_FRAMES,1450)
    out_cap = None
    
    iterate_list = range(4,5)
    for alpha_apply in iterate_list:
        cap = cv2.VideoCapture(SOURCE)
        if(DETECTOR in det_backgrounds):
            if (DETECTOR == "color_gauss_black_rem"):
                bgsg_module = BGSTModule(bs_type = DETECTOR, rho = RHO, alpha = ALPHA, init_at = INIT_AT, color_space = cspace)
            elif (DETECTOR == "gauss_black_rem"):
                bgsg_module = BGSTModule(bs_type = DETECTOR, rho = RHO, alpha = alpha_apply, init_at = INIT_AT, color_space = schannel)
            else:
                bgsg_module = BGSTModule(bs_type = DETECTOR, rho = RHO, alpha = ALPHA, init_at = INIT_AT)
            f = bgsg_module.get_contours
            for d in det_backgrounds:
                detectors[d] = f
                
        

        

        if DELETE_STATIC_OBJECTS:
            gt_frames = obtain_gt_without_static()
        else:
            gt_frames = obtain_gt()
            
        i = 0
        avg_precision = []
        iou_history = []
        iou_plot = LinePlot(gconf.plots.iou.name,
                            max_val=gconf.plots.iou.max_val,
                            save_plots=gconf.plots.iou.save)
        # mAP_plot = LinePlot("mAP_frame",max_val=350)
        detect_func = detectors[DETECTOR]
        
        while(cap.isOpened() and (STOP_AT == -1 or i <= STOP_AT)):
            # Capture frame-by-frame
            ret, frame = cap.read()
            if ret == True:
                #predict over the frame
                print("Frame: ", i)
                # rects = detect_func(frame)
                
                #Retrack over the frame
                
                #Classify the result
                dt_rects = detect_func(frame)

                #Obtain GT
                
                #Compute the metrics
                avg_precision_frame, iou_frame = getMetricsClass(dt_rects, gt_frames[str(i)], nclasses=1)
                if i > INIT_AT:
                    avg_precision.append(avg_precision_frame)
                    iou_history.append(iou_frame)
                    iou_plot.update(iou_frame)
                #Print Graph


                

                # if i > 1000:
                #     break
                    # iouFrame(iou_history)
                # iou_plot.update(iou_frame)

                # mAP_plot.update(avg_precision_frame)
                
                #Print Results
                ## prepare data
                gt_rects = gt_frames[str(i)]
                bgseg = None if bgsg_module is None else bgsg_module.get_bgseg()
                orig_bgseg = None if bgsg_module is None else bgsg_module.get_orig_bgseg()

                frame = print_func(frame.copy(), gt_rects, dt_rects, bgseg, orig_bgseg, gconf.pout)
                # cv2.imshow('Frame',frame)
                if i > INIT_AT:
                    
                    cv2.putText(frame,f"alpha={alpha_apply}",(50,50), cv2.FONT_HERSHEY_SIMPLEX, 2,(255,255,255),6,cv2.LINE_AA)
                    if(gconf.video.stack_iou):
                        iou_plot.build_frame(frame)
                    if(gconf.video.save_video):
                        if(out_cap is None):
                            if(gconf.video.stack_iou):
                                fshape = iou_plot.last_img.shape
                            else:
                                fshape = frame.shape
                            out_cap = cv2.VideoWriter(gconf.video.fname, cv2.VideoWriter_fourcc(*"MJPG"), 30, (fshape[1],fshape[0]))
                        f_out = frame 
                        if(gconf.video.stack_iou):
                            f_out = iou_plot.last_img
                        out_cap.write(f_out.astype('uint8'))
                    cv2.imshow(w_name, f_out)
                
                # Press Q on keyboard to  exit
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                i+=1
            # Break the loop
            else:
                break
        print("mIoU for all the video: ", np.mean(iou_history))
        print("mAP for all the video: ", np.mean(avg_precision))
        cap.release()
    out_cap.release()
    
    
if __name__ == "__main__":
    main()
    
