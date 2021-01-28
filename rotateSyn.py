import os,sys
import numpy as np
import h5py
from scipy.misc import imread,imsave


from skimage.measure import label
import json
import cv2
from scipy.stats import linregress
from util import bfly,rotateIm

class synRotator(object):
    def __init__(self, pad_sz = 150, thres_whole = 300, thres_slice = 50, thres_dilation = 5, output_folder='./'):
        # parameter
        self.pad_sz = pad_sz
        self.thres_whole = thres_whole
        self.thres_slice = thres_slice # size on one slice
        self.thres_dilation = thres_dilation # size of mask dilation
        self.output_folder = output_folder # output folder

    def rotate(self, pred_syn, vol_im, bboxes):
        # check if the folder is done
        bid = bboxes.shape[0]-1
        save_txt = self.output_folder+'/in_%d.txt'
        save_pref = self.output_folder+'/in_%d'
        if os.path.exists(save_txt%(bid)) or os.path.exists(save_pref%(bid)+'_rot.txt'):
            continue
        save_folder = save_txt[: save_txt.rfind('/')]
        if not os.path.exists(save_folder):
            os.makedirs(save_folder)

        # storage
        syn = np.zeros((self.pad_sz*2+1, self.pad_sz*2+1), dtype=np.uint8)
        im = 128*np.ones((self.pad_sz*2+1, self.pad_sz*2+1), dtype=np.uint8)
        dilation_mask = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (self.thres_dilation, self.thres_dilation))

        # for each box
        for bid in range(bboxes.shape[0]):
            #bid=5
            bbox = bboxes[bid]
            if os.path.exists(save_txt%(bid)) or os.path.exists(save_pref%(bid)+'_rot.txt'):
                # pred_syn channels
                # 0: pre-syn, 1: post-syn, 2: all 
                pred_pre = np.array(pred_syn[0,bbox[0]:bbox[1]+1,bbox[2]:bbox[3]+1,bbox[4]:bbox[5]+1])>128
                pred_post = np.array(pred_syn[1,bbox[0]:bbox[1]+1,bbox[2]:bbox[3]+1,bbox[4]:bbox[5]+1])>128
                pred_sz = pred_all.shape
                
                do_syn = True
                # at least one slice big enough
                if np.max(np.sum(pred_pre.reshape(pred_sz[0],-1),axis=1)) < self.thres_slice \
                   or np.max(np.sum(pred_post.reshape(pred_sz[0],-1),axis=1)) < self.thres_slice:
                    # bboxesox: total num
                    do_syn = False
                else:
                    # check the largest connected component
                    pred_all = np.array(pred_syn[2,bbox[0]:bbox[1]+1,bbox[2]:bbox[3]+1,bbox[4]:bbox[5]+1])>128
                    # find largest region
                    mm = label(pred_all)
                    segIds,segCounts = np.unique(mm,return_counts=True)
                    if segIds[0]==0:
                        segCounts[0]=0
                    sid = segIds[np.argmax(segCounts)]
                    mm_max = mm==sid
                    if np.max(np.sum((pred_pre*mm_max).reshape(pred_sz[0],-1),axis=1)) < self.thres_slice \
                       or np.max(np.sum((pred_post*mm_max).reshape(pred_sz[0],-1),axis=1))<self.thres_slice:
                        do_syn = False

                if not do_syn:
                    # no synapse output
                    np.savetxt(save_txt % bid, [pred_pre.sum(),pred_post.sum()],'%d')
                    # remoe previous result 
                    if os.path.exists(save_pref % bid + '_rot.txt'):
                        os.remove(save_pref % bid + '_rot.txt')
                        os.remove(save_pref % bid + '_im.png')
                        os.remove(save_pref % bid + '_syn.png')
                else:
                    # synapse output
                    if os.path.exists(save_txt % bid):
                        os.remove(save_txt % bid)

                    # find biggest 2D slice
                    zsum = np.sum(((pred_pre + pred_post) * mm_max).reshape(pred_sz[0],-1),axis=1)
                    zid = np.argmax(zsum)
                    # output color coding: pre=128, post=255
                    pred_pre_max = (pred_pre[zid] * mm_max[zid]).astype(np.uint8)*128
                    pred_post_max = (pred_post[zid] * mm_max[zid]).astype(np.uint8)*255

                    # get center
                    pp = np.where((pred_pre_max + pred_post_max)>0)
                    # position for input
                    px = bbox[4]+int(pp[1].mean())
                    py = bbox[2]+int(pp[0].mean())
                    pz = bbox[0]+zid

                    # 1. output syn
                    syn[:] = 0
                    # position for output
                    px_out = self.pad_sz + 1 - (px - bbox[4])
                    py_out = self.pad_sz + 1 - (py - bbox[2])
                    # can exceed pad_sz
                    sz2 = syn[max(0,py_out) : max(0, py_out) + pred_sz[1], \
                              max(0,px_out) : max(0, px_out) + pred_sz[2]].shape

                    # output patch: combine pred_pre_max and pred_post_max into one picture
                    # navie approach: wrong for the overlapped region
                    # syn_patch = pred_pre_max + pred_post_max
                    # for overlap region, give it to the smaller one
                    if np.sum(pred_pre_max>0) > np.sum(pred_post_max>0):
                        syn_patch = pred_pre_max
                        syn_patch[pred_post_max>0] = pred_post_max[pred_post_max>0]
                    else:
                        syn_patch = pred_post_max
                        syn_patch[pred_pre_max>0] = pred_pre_max[pred_pre_max>0]

                    syn_patch = syn_patch[max(0,-py_out):max(0,-py_out) + pred_sz[1], 
                                      max(0,-px_out):max(0,-px_out) + pred_sz[2]]

                    syn[max(0,py_out):max(0,py_out)+tmp.shape[0], 
                        max(0,px_out):max(0,px_out)+tmp.shape[1]] = syn_patch\

                    # 2. output image
                    # load image
                    im[:] = 128
                    # zyx image
                    im_patch = im[pz, max(0, py-pad_sz): py+pad_sz+1, \
                                  max(0,px-pad_sz): px+pad_sz+1]
                    im[max(0,pad_sz-py):max(0,pad_sz-py) + im_patch.shape[0], \
                       max(0,pad_sz-px):max(0,pad_sz-px) + im_patch.shape[1]] = im_patch

                    # 3. compute rotation
                    # compute rotatation by cleft
                    # cleft: overlap for the dilated pre-/post-partner
                    cleft = np.logical_and(cv2.dilate((syn==255).astype(np.uint8), dilation_mask), \
                                           cv2.dilate((syn==128).astype(np.uint8), dilation_mask))
                    if cleft.max()==0:
                        cleft = syn>0
                    pt = np.where(cleft>0)
                    if pt[0].min()==pt[0].max():
                        w=100; w2=0
                        angle = 90
                    else:
                        if pt[1].min()==pt[1].max():
                            w=0
                            angle = 0
                        else:
                            # angle concensus
                            # pt[0]: x
                            # pt[1]: y
                            w,_,_,_,_ = linregress(pt[0],pt[1])
                            angle = np.arctan(w)/np.pi*180
                            w2,_,_,_,_ = linregress(pt[1],pt[0])
                            angle2 = np.arctan(w2)/np.pi*180
                            #if abs((angle+angle2)-90)>20:
                            # trust the small one
                            if abs(angle2) < abs(angle):
                                angle = np.sign(angle2)*(90-abs(angle2))
                                w = 1/w2

                    # pre-post direction
                    # imsave('a.png',cleft.astype(np.uint8)*255)
                    # imsave('a.png',syn.astype(np.uint8))
                    # 
                    r1 = np.where(syn==128)
                    r2 = np.where(syn==255)
                    if len(r1[0])==0:
                        r1 = r2
                    if len(r2[0])==0:
                        r2 = r1

                    if abs(w)<0.2: # vertical bar, use w
                        if abs(w)>1e-4:
                            diff = (r2[1]-w*r2[0]).mean()-(r1[1]-w*r1[0]).mean()
                        else: # almost 0
                            diff = r2[1].mean()-r1[1].mean()
                    else: # horizontal bar, use w2
                        diff = -w2*((r2[0]-w2*r2[1]).mean()-(r1[0]-w2*r1[1]).mean())
                    #print bid,w,diff
                    if diff < 0:
                        angle = angle-180
                    pt_m = np.array([pt[1].mean(),pt[0].mean()])
                    # re-center
                    imsave(save_pref%bid + '_im.png', rotateIm(im, -angle, tuple(pt_m)))
                    imsave(save_pref%bid + '_syn.png', rotateIm(syn, -angle, tuple(pt_m)))
                    np.savetxt(save_pref%bid + '_rot.txt', [-angle]+list(pt_m),'%.3f')
