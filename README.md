# gallery_maker
*Make an html file for an image gallery.*

See example html files generatied using gallery maker: [Fru Jensen](https://vedranaa.github.io/FJ/) and [posters2022](https://www2.imm.dtu.dk/courses/02506/posters2022.html).

## SETUP
Either install the package from PyPI with `pip install galmak`  
or install from source with the following steps

## DEPENDENCIES
Making gallery has no dependencies.

A helper function for image processin is included, and it requires Pillow, which may be installed using:
`python3 -m pip install Pillow`.

Converting pdf images (only onepagers supported) is requires pdf2image, which is a wrapper around poppler. Poppler may be installed using:
`conda install -c conda-forge poppler`

Converting heic images is done using pillow_heif, which may be 
installed using: `python3 -m pip install pillow-heif`

## USAGE
#### As Python module:
```python
import galmak as gm

# Without image conversion, using default settings
path = 'path/to/images'
gm.make_gallery(path)

# With image conversion, using a few custom settings
path = 'path/to/images'
folder_out = 'path/to/output'
gm.fix_images(path, folder_out, max_size=2000, to_ext='.jpg')
gm.make_gallery(folder_out)
```
Look up docstrings of `make_gallery` and `fix_images` for more details.


#### From command line. 

For default behaviour navigate to a folder with images and run 
```
gallery_maker
```
to create an html file with a gallery of the images. Images may be either directly in the folder or in one subfolder. 

For custom behaviour use the following options:
- `--photos_folder` string, a path to the folder containing photos. If ending with '/' at the end, the html document is placed inside the photos_folder. Otherwise, the html document is placed in the top folder where photos_folder is placed.
- `--nr_columns` integer 1, 2, 3, or 4. Number of columns for the image grid. Defaults to 4.
- `--clickable` boolean. Whether clicking on the image yields a true-size preview of the image. This is useful when images are (natively) large and details can't be seen in scaled previews used for the image grid. Defaults to `True`.
- `--filename` string. Filename with html extension. Don't include the path. The path is extracted from photos_folder. Defaults to 'gallery.html'.
- `--window_title` string. Shorter text used in browser tabs. Defaults to 'Gallery'.
- `--gallery_title` string. The title of the gallery displayed in html page. Defaults to 'MY GALLERY'.
- `--footer_text` string. The text placed below the gallery. Defaults to 'Made by gallery_maker.py.'.

Specifying any of the following options will trigger image conversion before creating the gallery. The converted images will be saved in a subfolder of the folder the gallery, named `_processed_`. In this case, the original images are not used in the gallery.

- `--from_ext` string. A string listing extension of the images to be converted. It should be space-separated and enclosed in quotes. Example: `--from_ext ".jpeg .jpg .png .gif"`. Defaults to `".jpeg .jpg .png .gif"`. Also supported are `.pdf` and `.heic`, but these require additional dependencies.
- `--to_ext` string or None. Extension used when saving. If None, the original extension is used. 
- `--max_size` int or None. Maximal size of (any) image side. Defaults to None which keeps original image dimension.
- `--to_ext` to specify the extension of the converted images. If None, the original extension is used as much as possible, but `jpg` is used for `pdf` and `heic` images. Defaults to None.
- `--name_as` string or None. The root of the image names if images are to be renamed. Defaults to None which keeps original image names.

Example:
```
gallery_maker --nr_columns 3 --clickable False --filename my_gallery.html --window_title "Summer photos" --gallery_title "Summer holiday" --footer_text " " --from_ext ".jpeg .heic" 
```

## SUPPORTED IMAGE FORMATS
The following image formats are supported: `jpeg`, `jpg`, `png`, `gif`, `pdf` (requires `pdf2image` and `poppler`), `heic` (requires `pillow_heif`).
  
## KNOWN ISSUES
The library for reading `heic` images seems not to be working if I use code from the command line. It works fine if I use the same code in a script. I don't know why, it has something to do with module/package loading, so it might work for you.




