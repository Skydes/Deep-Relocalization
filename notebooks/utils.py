import matplotlib.pyplot as plt


def plot_imgs(imgs, titles=None, cmap='brg', ylabel='', normalize=True, ax=None,
              r=(0, 1), dpi=100):
    n = len(imgs)
    if not isinstance(cmap, list):
        cmap = [cmap]*n
    if ax is None:
        _, ax = plt.subplots(1, n, figsize=(6*n, 6), dpi=dpi)
        if n == 1:
            ax = [ax]
    else:
        if not isinstance(ax, list):
            ax = [ax]
        assert len(ax) == len(imgs)
    for i in range(n):
        if len(imgs[i].shape) == 3:
            if imgs[i].shape[-1] == 3:
                imgs[i] = imgs[i][..., ::-1]  # BGR to RGB
            elif imgs[i].shape[-1] == 1:
                imgs[i] = imgs[i][..., 0]
        if len(imgs[i].shape) == 2 and cmap[i] == 'brg':
            cmap[i] = 'gray'
        ax[i].imshow(imgs[i], cmap=plt.get_cmap(cmap[i]),
                     vmin=None if normalize else r[0],
                     vmax=None if normalize else r[1])
        if titles:
            ax[i].set_title(titles[i])
        ax[i].get_yaxis().set_ticks([])
        ax[i].get_xaxis().set_ticks([])
        for spine in ax[i].spines.values():  # remove frame
            spine.set_visible(False)
    ax[0].set_ylabel(ylabel)
    plt.tight_layout()
