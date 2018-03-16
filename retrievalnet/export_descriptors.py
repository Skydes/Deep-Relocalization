import numpy as np
import cv2
import os
import argparse
import yaml
from os import path as osp
from tqdm import tqdm

from retrievalnet.models import get_model
from retrievalnet.settings import EXPER_PATH, DATA_PATH
from retrievalnet.datasets.utils.nclt_undistort import Undistort

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('config', type=str)
    parser.add_argument('export_name', type=str)
    args = parser.parse_args()

    export_name = args.export_name
    with open(args.config, 'r') as f:
        config = yaml.load(f)
    seq = config['data']['seq']
    cam = config['data']['camera']

    root = osp.join(DATA_PATH, 'datasets/nclt')
    im_root = osp.join(root, '{}/lb3/Cam{}/'.format(seq, cam))
    dumap_file = osp.join(root, 'undistort_maps/U2D_Cam{}_1616X1232.txt'.format(cam))
    im_poses = np.loadtxt(osp.join(root, 'pose_{}.csv'.format(seq)),
                          dtype={'names': ('time', 'pose_x', 'pose_y'),
                                 'formats': (np.int, np.float, np.float)},
                          delimiter=',', skiprows=1)
    timestamps = im_poses['time']

    output_dir = osp.join(EXPER_PATH,
                          'outputs/{}/{}/'.format(export_name, seq))
    if not osp.exists(output_dir):
        os.makedirs(output_dir)

    # Remove distortion mask
    d2u = Undistort(dumap_file)
    h, w = d2u.mask.shape
    x_min, x_max = [f(np.where(d2u.mask[int(h/2), :])[0]) for f in [np.min, np.max]]
    y_min, y_max = [f(np.where(d2u.mask[:, int(w/2)])[0]) for f in [np.min, np.max]]

    def imread(name, undis=True):
        im = cv2.imread(osp.join(im_root, '{}.tiff'.format(name)))
        if undis:
            im = d2u.undistort(im)[y_min:y_max, x_min:x_max, ...]
        return np.rot90(im, k=3)

    with get_model(config['model']['name'])(
            data_shape={'image': [None, None, None, 3]}, **config['model']) as net:
        net.load(osp.join(DATA_PATH, 'weights', config['weights']))

        for t in tqdm(timestamps):
            im = imread(str(t), undis=False)
            descriptor = net.predict({'image': im}, keys='descriptor')
            filepath = osp.join(output_dir, '{}.npz'.format(t))
            np.savez_compressed(filepath, descriptor=descriptor)
