import torch
from torch import nn
from torch.autograd import Variable
from scipy.special import expit

import SimpleITK as sitk
import numpy as np

from ....preprocess.extract_lungs import extract_lungs
from ....preprocess.gtr123_preprocess import lum_trans, resample

""""
Detector model from team gtr123
Code adapted from https://github.com/lfz/DSB2017
"""

config = {}
config['anchors'] = [10.0, 30.0, 60.]
config['channel'] = 1
config['crop_size'] = [128, 128, 128]
config['stride'] = 4
config['max_stride'] = 16
config['num_neg'] = 800
config['th_neg'] = 0.02
config['th_pos_train'] = 0.5
config['th_pos_val'] = 1
config['num_hard'] = 2
config['bound_size'] = 12
config['reso'] = 1
config['sizelim'] = 6.  # mm
config['sizelim2'] = 30
config['sizelim3'] = 40
config['aug_scale'] = True
config['r_rand_crop'] = 0.3
config['pad_value'] = 170

__all__ = ["Net", "lum_trans", "resample", "GetPBB", "SplitComb"]


class PostRes(nn.Module):
    """ """
    def __init__(self, n_in, n_out, stride=1):
        super(PostRes, self).__init__()
        self.conv1 = nn.Conv3d(n_in, n_out, kernel_size=3, stride=stride, padding=1)
        self.bn1 = nn.BatchNorm3d(n_out)
        self.relu = nn.ReLU(inplace=True)
        self.conv2 = nn.Conv3d(n_out, n_out, kernel_size=3, padding=1)
        self.bn2 = nn.BatchNorm3d(n_out)

        if stride != 1 or n_out != n_in:
            self.shortcut = nn.Sequential(
                nn.Conv3d(n_in, n_out, kernel_size=1, stride=stride),
                nn.BatchNorm3d(n_out))
        else:
            self.shortcut = None

    def forward(self, x):
        """

        Args:
          x:

        Returns:

        """
        residual = x
        if self.shortcut is not None:
            residual = self.shortcut(x)
        out = self.conv1(x)
        out = self.bn1(out)
        out = self.relu(out)
        out = self.conv2(out)
        out = self.bn2(out)

        out += residual
        out = self.relu(out)
        return out


class Net(nn.Module):
    """The identification algorithm from Team grt123. Part of the winning algorithm."""

    def __init__(self):
        super(Net, self).__init__()
        # The first few layers consumes the most memory, so use simple convolution to save memory.
        # Call these layers preBlock, i.e., before the residual blocks of later layers.
        self.preBlock = nn.Sequential(
            nn.Conv3d(1, 24, kernel_size=3, padding=1),
            nn.BatchNorm3d(24),
            nn.ReLU(inplace=True),
            nn.Conv3d(24, 24, kernel_size=3, padding=1),
            nn.BatchNorm3d(24),
            nn.ReLU(inplace=True))

        # 3 poolings, each pooling downsamples the feature map by a factor 2.
        # 3 groups of blocks. The first block of each group has one pooling.
        num_blocks_forw = [2, 2, 3, 3]
        num_blocks_back = [3, 3]
        self.featureNum_forw = [24, 32, 64, 64, 64]
        self.featureNum_back = [128, 64, 64]
        for i in range(len(num_blocks_forw)):
            blocks = []
            for j in range(num_blocks_forw[i]):
                if j == 0:
                    blocks.append(PostRes(self.featureNum_forw[i], self.featureNum_forw[i + 1]))
                else:
                    blocks.append(PostRes(self.featureNum_forw[i + 1], self.featureNum_forw[i + 1]))
            setattr(self, 'forw' + str(i + 1), nn.Sequential(*blocks))

        for i in range(len(num_blocks_back)):
            blocks = []
            for j in range(num_blocks_back[i]):
                if j == 0:
                    if i == 0:
                        addition = 3
                    else:
                        addition = 0
                    blocks.append(PostRes(self.featureNum_back[i + 1] + self.featureNum_forw[i + 2] + addition,
                                          self.featureNum_back[i]))
                else:
                    blocks.append(PostRes(self.featureNum_back[i], self.featureNum_back[i]))
            setattr(self, 'back' + str(i + 2), nn.Sequential(*blocks))

        self.maxpool1 = nn.MaxPool3d(kernel_size=2, stride=2, return_indices=True)
        self.maxpool2 = nn.MaxPool3d(kernel_size=2, stride=2, return_indices=True)
        self.maxpool3 = nn.MaxPool3d(kernel_size=2, stride=2, return_indices=True)
        self.maxpool4 = nn.MaxPool3d(kernel_size=2, stride=2, return_indices=True)
        self.unmaxpool1 = nn.MaxUnpool3d(kernel_size=2, stride=2)
        self.unmaxpool2 = nn.MaxUnpool3d(kernel_size=2, stride=2)

        self.path1 = nn.Sequential(
            nn.ConvTranspose3d(64, 64, kernel_size=2, stride=2),
            nn.BatchNorm3d(64),
            nn.ReLU(inplace=True))
        self.path2 = nn.Sequential(
            nn.ConvTranspose3d(64, 64, kernel_size=2, stride=2),
            nn.BatchNorm3d(64),
            nn.ReLU(inplace=True))
        self.drop = nn.Dropout3d(p=0.2, inplace=False)
        self.output = nn.Sequential(nn.Conv3d(self.featureNum_back[0], 64, kernel_size=1),
                                    nn.ReLU(),
                                    # nn.Dropout3d(p = 0.3),
                                    nn.Conv3d(64, 5 * len(config['anchors']), kernel_size=1))

    def forward(self, x, coord):
        """

        Args:
          x:
          coord:

        Returns:

        """
        out = self.preBlock(x)  # 16
        out_pool, indices0 = self.maxpool1(out)
        out1 = self.forw1(out_pool)  # 32
        out1_pool, indices1 = self.maxpool2(out1)
        out2 = self.forw2(out1_pool)  # 64
        # out2 = self.drop(out2)
        out2_pool, indices2 = self.maxpool3(out2)
        out3 = self.forw3(out2_pool)  # 96
        out3_pool, indices3 = self.maxpool4(out3)
        out4 = self.forw4(out3_pool)  # 96
        # out4 = self.drop(out4)

        rev3 = self.path1(out4)
        comb3 = self.back3(torch.cat((rev3, out3), 1))  # 96+96
        # comb3 = self.drop(comb3)
        rev2 = self.path2(comb3)
        feat = self.back2(torch.cat((rev2, out2, coord), 1))  # 64+64
        comb2 = self.drop(feat)
        out = self.output(comb2)
        size = out.size()
        out = out.view(out.size(0), out.size(1), -1)
        # out = out.transpose(1, 4).transpose(1, 2).transpose(2, 3).contiguous()
        out = out.transpose(1, 2).contiguous().view(size[0], size[2], size[3], size[4], len(config['anchors']), 5)
        # out = out.view(-1, 5)
        return out


class GetPBB(object):
    """ """
    def __init__(self, stride=4, anchors=(10.0, 30.0, 60.)):
        self.stride = stride
        self.anchors = np.asarray(anchors)

    def __call__(self, output, thresh=-3, ismask=False):
        stride = self.stride
        anchors = self.anchors
        output = np.copy(output)
        offset = (float(stride) - 1) / 2
        output_size = output.shape
        oz = np.arange(offset, offset + stride * (output_size[0] - 1) + 1, stride)
        oh = np.arange(offset, offset + stride * (output_size[1] - 1) + 1, stride)
        ow = np.arange(offset, offset + stride * (output_size[2] - 1) + 1, stride)

        output[:, :, :, :, 1] = oz.reshape((-1, 1, 1, 1)) + output[:, :, :, :, 1] * anchors.reshape((1, 1, 1, -1))
        output[:, :, :, :, 2] = oh.reshape((1, -1, 1, 1)) + output[:, :, :, :, 2] * anchors.reshape((1, 1, 1, -1))
        output[:, :, :, :, 3] = ow.reshape((1, 1, -1, 1)) + output[:, :, :, :, 3] * anchors.reshape((1, 1, 1, -1))
        output[:, :, :, :, 4] = np.exp(output[:, :, :, :, 4]) * anchors.reshape((1, 1, 1, -1))
        mask = output[..., 0] > thresh
        xx, yy, zz, aa = np.where(mask)

        output = output[xx, yy, zz, aa]
        if ismask:
            return output, [xx, yy, zz, aa]
        else:
            return output


class SplitComb(object):
    """ """
    def __init__(self, side_len, max_stride, stride, margin, pad_value):
        self.side_len = side_len
        self.max_stride = max_stride
        self.stride = stride
        self.margin = margin
        self.pad_value = pad_value

    def split(self, data, side_len=None, max_stride=None, margin=None):
        """

        Args:
          data:
          side_len:  (Default value = None)
          max_stride:  (Default value = None)
          margin:  (Default value = None)

        Returns:

        """
        if side_len is None:
            side_len = self.side_len
        if max_stride is None:
            max_stride = self.max_stride
        if margin is None:
            margin = self.margin

        assert (side_len > margin)
        assert (side_len % max_stride == 0)
        assert (margin % max_stride == 0)

        splits = []
        _, z, h, w = data.shape

        nz = int(np.ceil(float(z) / side_len))
        nh = int(np.ceil(float(h) / side_len))
        nw = int(np.ceil(float(w) / side_len))

        nzhw = [nz, nh, nw]
        self.nzhw = nzhw

        pad = [[0, 0],
               [margin, nz * side_len - z + margin],
               [margin, nh * side_len - h + margin],
               [margin, nw * side_len - w + margin]]
        data = np.pad(data, pad, 'edge')

        for iz in range(nz):
            for ih in range(nh):
                for iw in range(nw):
                    sz = iz * side_len
                    ez = (iz + 1) * side_len + 2 * margin
                    sh = ih * side_len
                    eh = (ih + 1) * side_len + 2 * margin
                    sw = iw * side_len
                    ew = (iw + 1) * side_len + 2 * margin

                    split = data[np.newaxis, :, sz:ez, sh:eh, sw:ew]
                    splits.append(split)

        splits = np.concatenate(splits, 0)
        return splits, nzhw

    def combine(self, output, nzhw=None, side_len=None, stride=None, margin=None):
        """

        Args:
          output:
          nzhw:  (Default value = None)
          side_len:  (Default value = None)
          stride:  (Default value = None)
          margin:  (Default value = None)

        Returns:

        """

        if side_len is None:
            side_len = self.side_len
        if stride is None:
            stride = self.stride
        if margin is None:
            margin = self.margin
        if nzhw is None:
            nz = self.nz
            nh = self.nh
            nw = self.nw
        else:
            nz, nh, nw = nzhw
        assert (side_len % stride == 0)
        assert (margin % stride == 0)
        side_len //= stride
        margin //= stride

        splits = []
        for i in range(len(output)):
            splits.append(output[i])

        output = -1000000 * np.ones((
            nz * side_len,
            nh * side_len,
            nw * side_len,
            splits[0].shape[3],
            splits[0].shape[4]), np.float32)

        idx = 0
        for iz in range(nz):
            for ih in range(nh):
                for iw in range(nw):
                    sz = iz * side_len
                    ez = (iz + 1) * side_len
                    sh = ih * side_len
                    eh = (ih + 1) * side_len
                    sw = iw * side_len
                    ew = (iw + 1) * side_len

                    split = splits[idx][margin:margin + side_len, margin:margin + side_len, margin:margin + side_len]
                    output[sz:ez, sh:eh, sw:ew] = split
                    idx += 1

        return output


def split_data(imgs, split_comber, stride=4):
    """Image tends to be too big to fit on even very large memory systems. This function splits it up into manageable
    chunks.

    Args:
      imgs: param split_comber:
      stride: return: (Default value = 4)
      split_comber:

    Returns:

    """
    nz, nh, nw = imgs.shape[1:]
    pz = int(np.ceil(float(nz) / stride)) * stride
    ph = int(np.ceil(float(nh) / stride)) * stride
    pw = int(np.ceil(float(nw) / stride)) * stride
    imgs = np.pad(imgs, [[0, 0], [0, pz - nz], [0, ph - nh], [0, pw - nw]], 'constant',
                  constant_values=split_comber.pad_value)

    xx, yy, zz = np.meshgrid(np.linspace(-0.5, 0.5, imgs.shape[1] // stride),
                             np.linspace(-0.5, 0.5, imgs.shape[2] // stride),
                             np.linspace(-0.5, 0.5, imgs.shape[3] // stride), indexing='ij')
    coord = np.concatenate([xx[np.newaxis, ...], yy[np.newaxis, ...], zz[np.newaxis, :]], 0).astype('float32')
    imgs, nzhw = split_comber.split(imgs)
    coord2, nzhw2 = split_comber.split(coord,
                                       side_len=split_comber.side_len // stride,
                                       max_stride=split_comber.max_stride // stride,
                                       margin=int(split_comber.margin // stride))
    assert np.all(nzhw == nzhw2)
    imgs = (imgs.astype(np.float32) - 128) / 128
    return torch.from_numpy(imgs), torch.from_numpy(coord2), np.array(nzhw)


def iou(box0, box1):
    """

    Args:
      box0:
      box1:

    Returns:
      Intersection over union

    """

    r0 = box0[3] / 2
    s0 = box0[:3] - r0
    e0 = box0[:3] + r0

    r1 = box1[3] / 2
    s1 = box1[:3] - r1
    e1 = box1[:3] + r1

    overlap = []
    for i in range(len(s0)):
        overlap.append(max(0, min(e0[i], e1[i]) - max(s0[i], s1[i])))

    intersection = overlap[0] * overlap[1] * overlap[2]
    union = box0[3] * box0[3] * box0[3] + box1[3] * box1[3] * box1[3] - intersection
    return intersection / union


def nms(predictions, nms_th=0.05):
    """

    Args:
      predictions: Output from the neural network
      nms_th: return: (Default value = 0.05)

    Returns:

    """
    if len(predictions) == 0:
        return predictions

    predictions = predictions[np.argsort(-predictions[:, 0])]
    bboxes = [predictions[0]]
    for i in np.arange(1, len(predictions)):
        bbox = predictions[i]
        flag = 1
        for j in range(len(bboxes)):
            if iou(bbox[1:5], bboxes[j][1:5]) >= nms_th:
                flag = -1
                break
        if flag == 1:
            bboxes.append(bbox)

    bboxes = np.asarray(bboxes, np.float32)
    return bboxes


def filter_lungs(image, spacing=(1, 1, 1), fill_value=170):
    """

    Args:
      image: Image in Hu units
      spacing: Image spacing (Default value = (1,1,1)
      fill_value: Hu value to use (Default value = 170)


    Returns:
      An image volume containing only lungs as well as the boolean mask.

    """

    mask = extract_lungs(image, spacing)

    extracted = np.array(image)
    extracted[np.logical_not(mask)] = fill_value

    return extracted, mask


def predict(image_itk, model_path="src/algorithms/identify/assets/dsb2017_detector.ckpt"):
    """

    Args:
      image_itk: ITK Image in Hu units
      model_path: Path to the file containing the model state
                 (Default value = "src/algorithms/identify/assets/dsb2017_detector.ckpt")

    Returns:
      List of Nodule locations and probabilities

    """

    spacing = np.array(image_itk.GetSpacing())[::-1]
    image = sitk.GetArrayFromImage(image_itk)
    masked_image, mask = filter_lungs(image)
    # masked_image = image
    net = Net()
    net.load_state_dict(torch.load(model_path)["state_dict"])
    if torch.cuda.is_available():
        net = torch.nn.DataParallel(net).cuda()

    split_comber = SplitComb(side_len=int(144), margin=32, max_stride=16, stride=4, pad_value=170)

    # We have to use small batches until the next release of PyTorch, as bigger ones will segfault for CPU
    # split_comber = SplitComb(side_len=int(32), margin=16, max_stride=16, stride=4, pad_value=170)
    # Transform image to the 0-255 range and resample to 1x1x1mm
    imgs = lum_trans(masked_image)
    imgs = resample(imgs, spacing, np.array([1, 1, 1]), order=1)[0]
    imgs = imgs[np.newaxis, ...]

    imgT, coords, nzhw = split_data(imgs, split_comber=split_comber)
    results = []
    # Loop over the image chunks
    for img, coord in zip(imgT, coords):
        var = Variable(img[np.newaxis])
        var.volatile = True
        coord = Variable(coord[np.newaxis])
        coord.volatile = True
        resvar = net(var, coord)
        res = resvar.data.cpu().numpy()
        results.append(res)

    results = np.concatenate(results, 0)
    results = split_comber.combine(results, nzhw=nzhw)
    pbb = GetPBB()
    # First index of proposals is the propabillity. Then x, y z, and radius
    proposals, _ = pbb(results, ismask=True)

    # proposals = proposals[proposals[:,4] < 40]
    proposals = nms(proposals)
    # Filter out proposals outside the actual lung
    # prop_int = proposals[:, 1:4].astype(np.int32)
    # wrong = [imgs[0, x[0], x[1], x[2]] > 180 for x in prop_int]
    # proposals = proposals[np.logical_not(wrong)]

    # Do sigmoid to get propabillities
    proposals[:, 0] = expit(proposals[:, 0])
    # Remove really weak proposals?
    # proposals = proposals[proposals[:,0] > 0.5]

    # Rescale back to image space coordinates
    proposals[:, 1:4] /= spacing[np.newaxis]

    return [{"x": int(p[3]), "y": int(p[2]), "z": int(p[1]), "p_nodule": float(p[0])} for p in proposals]
