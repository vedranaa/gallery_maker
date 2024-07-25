'''
Make an html file for an image gallery.

'''

import os
import sys
import argparse

# MAIN FUNCTIONS
def make_gallery(photos_folder, nr_columns=4, clickable=True, 
                 filename='gallery.html',
                 window_title='Gallery', gallery_title='MY GALLERY', 
                 footer_text='Made by gallery-maker.py.'):
    
    ''' 
    Make an html file for an folder of images.
    
        photos_folder: string, a path to the folder containing photos. String 
            photos_folder is normally without '/' at the end, and then the htlm 
            document is made in the top folder where photos_folder is placed. If 
            photos_folder has '/' at the end, html document is placed inside the 
            photos_folder.
         nr_columns: integer 1, 2, 3, or 4. Number of columns for the image grid.
         clickable: boolean. Whether clicking on the image yields a true-size
            preview of the image. This is useful when images are (natively)
            large and details can't be seen in scaled previews used for the 
            image grid.
        filename: string. Filename with html extension. Don't include the path.
            The path is extracted from photos_folder.
        window_title: string. Shorter text used in browser tabs.
        gallery_title: string. The title of the gallery displayed in html page.
        footer_text: The text placed below the gallery. No footer if empty.

    '''

    #  Get hold of images.
    top_folder, foldername = os.path.split(photos_folder)
    extensions = ['.jpeg', '.jpg', '.png', '.gif']
    files = os.listdir(photos_folder)
    files = sorted(files)
    images = [f for f in files if os.path.splitext(f)[1].lower() in extensions]
    if len(images)==0:
        print('No images found! Aborting.')
        return
    paths = [os.path.join(foldername,  i) for i in images]

    #  Make components.
    pre = make_pre(nr_columns, clickable, window_title, gallery_title)
    photo_grid = make_photo_grid(paths, nr_columns, clickable)
    modal, script = make_click_support(clickable)
    footer = make_footer(footer_text)
    seq1, seq2 = make_seq()

    lines =  pre + photo_grid + modal + footer + seq1 + script + seq2
    
    #  Save the file.
    #  TODO: Check whether file already exists and abort if yes.
    filepath = os.path.join(top_folder, filename)
    with open(filepath, 'w') as f:
        f.write('\n'.join(lines) + '\n')


def fix_images(folder_in, folder_out, max_size=2000, 
               from_ext = ['.jpeg', '.jpg', '.png', '.gif'], to_ext='.png', 
               name_as='image'):
    '''
    Processes all images in folder_in and saves in folder_out.

        folder_in: a path to a folder containing images.
        folder_out: a path to a folder where images are to be saved. Needs to be 
            made beforehand (outside this function).
        max_size: int or None. Maximal size of (any) image side.
        from_ext: list of strings or a single string. Extensions considered. 
        to_ext: string or None. Extension used when saving. If None, the 
            original extension is used. 
        name_as: string or None. The root of the image names if images are to be 
            renamed. If None, the original name is used.
        
        TODO Test whether all extensions to and from are supported
    '''

    import PIL.Image
    PIL.Image.MAX_IMAGE_PIXELS = None

    # Support from only one ext to be considered given as string
    if type(from_ext) is str:
        from_ext = [from_ext]
    
    from_ext = [e.lower() for e in from_ext]

    if '.pdf' in from_ext:
        from pdf2image import convert_from_path
        
    if '.heic' in from_ext:
        from pillow_heif import register_heif_opener
        register_heif_opener()
        
    files = os.listdir(folder_in)
    images = [f for f in files if os.path.splitext(f)[1].lower() in from_ext]

    print('*****')
    print('from_ext:', from_ext)
    print('images:', images)
    print('*****')

    images = sorted(images)

    if len(images)==0:
        print('No images found!')

    for nr, image in enumerate(images):

        print(f'Processing image nr {nr}: {image}')
        name, ext = os.path.splitext(os.path.split(image)[1])

        I = safe_load_image(os.path.join(folder_in, image), ext)
        if I is None:
            continue
        if max_size is not None:
            s = I.size
            I = I.resize([int(max_size * x / max(s)) for x in s])
            print(f'  Resized from {s} to {I.size}')
        if name_as is not None:
            print(f'  Name {name} changed to ', end='')
            name = name_as + str(nr).rjust(len(str(len(images))), '0')
            print(name)
        
        if to_ext is not None:
            if ext != to_ext:
                print(f'  Extension {ext} changed to ', end='')
                ext = to_ext
                print(ext)
        else:
            if ext == '.pdf' or ext == '.heic':
                print(f'  Extension {ext} changed to ', end='')
                ext = '.jpg'
                print(ext)

        safe_save_image(I, os.path.join(folder_out, name), ext)

def safe_load_image(path, ext):
    if ext.lower() == '.pdf':
        try:
            return convert_from_path(path)[0] # Takes only first page
        except:
            print(f'  Loading failed for {path} with extension {ext}.')
            return 
    try:
        return PIL.Image.open(path)
    except:
        print(f'  Loading failed for {path} with extension {ext}.')
        

def safe_save_image(I, path, ext):   
    try:
        I.save(path + ext)
        return
    except:
        print(f'  Native saving failed for {path} with extension {ext}.')
    try:
        I.convert('RGB').save(path + ext)
        print(f'  Succeded saving as {ext} after removing alpha.')
        return
    except:
        print(f'  Removing alpha failed for {path} with extension {ext}.') 
    try:
        I.convert('RGB').save(path + '.jpg')
        print(f'  Succeded saving as jpg after removing alpha.')
        return   
    except:
        print(f'  Removing alpha failed for {path} with extension jpg.')
    try:
        I.save(path + '.png')
        print(f'  Succeded saving as png.')
        return
    except:
        print(f'  Saving failed for {path}. Skipping!!!!!!!!')


# HELPING FUNCTIONS

def make_photo_grid(paths, nr_columns, clickable):

    # Distribute images in columns.
    # TODO: consider image aspect ratio when distributing to columns.
    min_nr = len(paths)//nr_columns  # at least so many per column
    rest = len(paths) % nr_columns  # to be placed in first x columns
    steps = [min_nr + (i<rest) for i in range(nr_columns)]

    # Make columns.
    lines = ['  <!-- Photo grid -->', 
             '  <div class="w3-row-padding w3-grayscale-min">']
    for i in range(nr_columns):
        k = sum(steps[:i])  # index of first image in this column
        column = make_column(paths[k : k + steps[i]], nr_columns, clickable)
        lines = lines + [''] + column
    lines = lines + ['', '  </div>', '']

    return lines


def make_column(paths, nr_columns, clickable):

    split = {1: 'block', 2:'half', 3: 'third', 4:'quarter'}[nr_columns]
    click = 'onclick="onClick(this)" ' if clickable else ''

    pre = f'   <div class="w3-{split}">'
    seq = '   </div>'
    elements = [f'      <img src="{p}" style="width:100%" {click}alt="">' 
                for p in paths]
    column = [pre] + elements + [seq]

    return column


def make_click_support(clickable):

    modal = ['  <!-- Modal for full size images on click-->',
        '  <div id="modal01" class="w3-modal w3-black" style="padding-top:0" '
                'onclick="this.style.display=\'none\'">',
        '    <span class="w3-button w3-black w3-xlarge '
                'w3-display-topright">×</span>',
        '    <div class="w3-modal-content w3-animate-zoom w3-center '
                'w3-transparent w3-padding-64">',
        '      <img id="img01" class="w3-image">',
        '    </div>',
        '  </div>',
        ''] * clickable
    script = ['<script>',
        '// Modal Image Gallery',
        'function onClick(element) {',
        '  document.getElementById("img01").src = element.src;',
        '  document.getElementById("modal01").style.display = "block";',
        '}',
        '</script>',
        ''] * clickable

    return modal, script


def make_footer(footer_text):

    footer = ['  <!-- Footer -->',
        '  <footer class="w3-container w3-padding-32 w3-light-gray">',
        '    <div class="w3-row-padding">',
        f'      <p>{footer_text}</p>',
        '    </div>',
        '  </footer>',
        ''] * bool(footer_text)

    return footer


def make_pre(nr_columns, clickable, window_title, gallery_title):

    split = {1: 'block', 2:'half', 3: 'third', 4:'quarter'}[nr_columns]
    
    header = ['<!-- Top menu on small screens -->',
        '<header class="w3-container w3-top w3-light-gray w3-padding-16">',
        '  <span class="w3-left  w3-xlarge w3-padding">' + gallery_title + '</span>',
        '</header>',
        ''] * bool(gallery_title)

    pre = (['<!DOCTYPE html>',
        '<html>'] +
        ['<title>' + window_title + '</title>'] * bool(window_title)  + 
        ['<meta charset="UTF-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1">',
        '<link rel="stylesheet" href="https://www.w3schools.com/w3css/4/w3.css">',
        '<link rel="stylesheet" href="https://fonts.googleapis.com/css?family=Raleway">',
        '<style>',
        'body,h1,h2,h3,h4,h5 {font-family: "Raleway", sans-serif}',
        '.w3-' + split + ' img{margin-bottom: 10px' + '; cursor: pointer' * clickable + '}'] +
        ['.w3-' + split + ' img:hover{opacity: 0.6; transition: 0.3s}'] * clickable + 
        ['</style>',
        '',
        '<body class="w3-light-grey">',
        ''] +
        header +
        ['<!-- !PAGE CONTENT! -->',
        '<div class="w3-main w3-content" style="max-width:1600px;margin-top:83px">',
        ''])

    return pre


def make_seq():
    seq1 = ['<!-- End page content -->',
        '</div>',
        '']
    seq2 = ['</body>',
        '</html>',
        '']
    
    return seq1, seq2


def main():

    parser = argparse.ArgumentParser(description='Make an html file for an image gallery.')
    parser.add_argument('--photos_folder', type=str, default=None, help='Path to folder containing images.')
    parser.add_argument('--nr_columns', type=int, default=4) 
    parser.add_argument('--clickable', default=True)
    parser.add_argument('--filename', default='gallery.html')
    parser.add_argument('--window_title', default='Gallery')
    parser.add_argument('--gallery_title', default='MY GALLERY')
    parser.add_argument('--footer_text', default='Made by <a href="https://github.com/vedranaa/gallery_maker">gallery_maker.py</a>.')

    parser.add_argument('--from_ext', type=str, default=None, help='String with list of extensions to be converted.')
    parser.add_argument('--max_size', type=int, default=None, help='Maximal size of (any) image side.')
    parser.add_argument('--to_ext', type=str, default=None, help='Extension used when saving.')
    parser.add_argument('--name_as', type=str, default=None, help='The root of the image names if images are to be renamed.')
    args = parser.parse_args()

    if args.photos_folder is None:
        folders = [f for f in os.listdir() if os.path.isdir(f)]
        if folders:
            args.photos_folder = folders[0]
        else:
            args.photos_folder = os.getcwd() + '/'
        print(f'No photos_folder given, using {args.photos_folder}.')

    if any([args.from_ext, args.to_ext, args.max_size, args.name_as]):
        top_folder, _ = os.path.split(args.photos_folder)
        
        folder_out = os.path.join(top_folder, '_processed_')
        if not os.path.exists(folder_out):
            os.mkdir(folder_out)
        else:
            print(f'Processing required and folder {folder_out} already exists. Aborting.')
            sys.exit()
        
        if args.from_ext is None:
            args.from_ext = ['.jpeg', '.jpg', '.png', '.gif']
        else:
            args.from_ext = args.from_ext.split()
        
        if args.to_ext is not None:
            args.to_ext = '.jpg'
        
        print(f'Processing images in {args.photos_folder} and saving in {folder_out}.')
        fix_images(args.photos_folder, folder_out, 
                    max_size=args.max_size, 
                    from_ext=args.from_ext, 
                    to_ext=args.to_ext, 
                    name_as=args.name_as)
        args.photos_folder = folder_out


    print(f'Making gallery from {args.photos_folder}.')
    make_gallery(args.photos_folder, 
                 args.nr_columns, 
                 args.clickable, 
                 args.filename,  
                 args.window_title, 
                 args.gallery_title, 
                 args.footer_text)


if __name__ == '__main__':
    '''  May be used from command-line. '''
    main()
