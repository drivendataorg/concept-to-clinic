"""This file contains methods that help to visualize the training cubes of annotations"""

import matplotlib.pyplot as plt
from matplotlib.widgets import Slider


def cuboid_show_slider(cuboid, axis=2, is_mask=False, **kwargs):
    """Display a 3D ndarray with a slider to move along the third dimension.

    Extra keyword arguments are passed to imshow
    (Kudos to http://nbarbey.github.io/2011/07/08/matplotlib-slider.html)

    Args:
        cuboid: three-dimensional array that should be visualized
        axis: index of the axis that should be changeable using the slider
        is_mask: whether the cuboid that should be plotting is a binary mask
    """

    # check dim
    if not cuboid.ndim == 3:
        raise ValueError("cube should be an ndarray with ndim == 3")

    # generate figure
    fig = plt.figure()
    subplot = fig.add_subplot(111)
    fig.subplots_adjust(left=0.25, bottom=0.25)

    if is_mask:
        im1 = subplot.imshow(cuboid[:, :, 0])
        fig.colorbar(im1)
    else:
        # select first image
        s = [slice(0, 1) if i == axis else slice(None) for i in range(3)]
        im = cuboid[s].squeeze()

        # display image
        image_display = subplot.imshow(im, **kwargs)

    # define slider
    axcolor = 'lightgoldenrodyellow'
    ax = fig.add_axes([0.25, 0.1, 0.65, 0.03], axisbg=axcolor)

    slider = Slider(ax, 'Axis %i index' % axis, 0, cuboid.shape[axis] - 1, valinit=0, valfmt='%i')

    def update(val):
        if is_mask:
            subplot.imshow(cuboid[:, :, int(val)])
            fig.canvas.draw()
        else:
            ind = int(slider.val)
            s = [slice(ind, ind + 1) if i == axis else slice(None)
                 for i in range(3)]
            im = cuboid[s].squeeze()
            image_display.set_data(im, **kwargs)
        fig.canvas.draw()

    slider.on_changed(update)

    plt.show()


def display_training_pair(input_cuboid, output_cuboid, axis=2, **kwargs):
    """Display both given three-dimensional input images with a slider for the third dimension.

    Args:
        input_cuboid: three-dimensional array that contains the scan
        output_cuboid: three-dimensional array that contains the segmented mask
        axis: index of the axis that should be changeable using the slider
    """

    # check dims
    if not input_cuboid.ndim == 3 or not output_cuboid.ndim == 3:
        raise ValueError("cube should be an ndarray with ndim == 3")

    # generate figure
    fig = plt.figure()
    subplot_input = fig.add_subplot(221)
    subplot_output = fig.add_subplot(222)
    fig.subplots_adjust(left=0.25, bottom=0.25)

    # select first image
    im1 = subplot_output.imshow(output_cuboid[:, :, 0])
    fig.colorbar(im1)

    s = [slice(0, 1) if i == axis else slice(None) for i in range(3)]
    im = input_cuboid[s].squeeze()
    # display image
    image_display = subplot_input.imshow(im, **kwargs)

    # define slider
    axcolor = 'lightgoldenrodyellow'
    ax = fig.add_axes([0.25, 0.1, 0.65, 0.03], axisbg=axcolor)

    slider = Slider(ax, 'Axis %i index' % axis, 0, input_cuboid.shape[axis] - 1, valinit=0, valfmt='%i')

    def update(val):
        subplot_output.imshow(output_cuboid[:, :, int(val)])

        ind = int(slider.val)
        s = [slice(ind, ind + 1) if i == axis else slice(None)
             for i in range(3)]
        im = input_cuboid[s].squeeze()
        image_display.set_data(im, **kwargs)
        fig.canvas.draw()

    slider.on_changed(update)

    plt.show()
