import sys
import os
import shutil
from optparse import OptionParser
from mutagen import mp3, easyid3

class MP3Organizer(object):
    """Class used for organizing a bunch of mp3 files in separate directories, 
    according to a ID3 tag. 
    It creates a directory for each value taken by the tag and copies
    the corresponding mp3 files (having that tag value).
    For example, let us assume that we have 4 mp3 songs, two authored by Queen 
    and two by Rammstein, and that we want to organize the mp3 files by the 
    artist ID3 tag.
    In this case, the code will create 2 directories, one names Queen and one
    named Rammstein and will copy the corresponding mp3 files in them.
    If one file does not have the tag set, a special directory names 'unknown'
    will be created and the file will be copied there.
    Currently, the user can choose among the following tags: 'artist', 'album', 
    'year' or 'genre'.
      
    Arguments:
    - `source_dir` is the name of the root directory where the mp3 files are 
       located.
    - `dest_dir` is the name of the directory in which the mp3 files will be 
       copied (in an organized form).
    - `tag` is the name of the ID3 tag used for organization.
    """
    def __init__(self, source_dir, dest_dir, tag):
        self.source_dir = source_dir
        self.dest_dir = dest_dir
        self.tag = tag
        self.copied_files = 0
        self.copy_fails = 0
        if not os.path.exists(self.dest_dir):
            os.mkdir(self.dest_dir)
    
    def _add_file(self, mp3_file):
        """At the `mp3_file` file in the correct directory, according to the 
        tag value. The directory is created if not already existing.
        """
        short_tags = mp3.MP3(mp3_file, ID3=easyid3.EasyID3)
        tag_value = short_tags.get(self.tag, [u'unknown'])[0]
        tag_value = "_".join(tag_value.split())
        mp3_file_dest_dir = os.path.join(self.dest_dir, tag_value)
        if not os.path.exists(mp3_file_dest_dir):
            os.mkdir(mp3_file_dest_dir)
        shutil.copy(mp3_file, mp3_file_dest_dir)
        sys.stdout.write("Copied %s to %s \n" % (mp3_file, mp3_file_dest_dir))
        self.copied_files += 1
    
    def _increment_failures(self):
        """Increment the number of files which failed to copy."""
        self.copy_fails += 1
    
    @staticmethod    
    def _walk_callback(mp3_organizer, dir_name, entries):
        """Callback called while recursively iterating over the source directory
        tree structure.
        Arguments:
        - `mp3_organizer` is an MP3Organizer instance.
        - `dir_name` is the name of a directory in the source directory tree.
        - `entries` are the entries in `dir_name` (files or sub-directories).
        """
        for entry in entries:
            entry_path = os.path.abspath(os.path.join(dir_name, entry))
            if os.path.isfile(entry_path):
                (_, entry_ext) = os.path.splitext(entry_path)
                if len(entry_ext) > 0 and entry_ext.lower() == '.mp3':
                    try:
                        mp3_organizer._add_file(entry_path)
                    except Exception, e:
                        sys.stderr.write("Cannot copy file %s (reason: %s)\n" %\
                                         (entry_path, str(e)))
                        mp3_organizer._increment_failures()
                    
    def run(self):
        """Run the mp3 organizer."""
        os.path.walk(self.source_dir, MP3Organizer._walk_callback, self)
        sys.stdout.write("Copied %d files\n" % self.copied_files)
        if self.copy_fails > 0:
            sys.stdout.write("Failed to copy %d files !\n" % self.copy_fails)


def main():
    usage = "Usage: %prog [options]"
    parser = OptionParser(usage)
    parser.add_option("-s", "--source_dir", dest="source_dir",
                      help="""the source root directory (containing the MP3 
                      files to be organized)""")
    parser.add_option("-d", "--dest_directory", dest="dest_dir", 
                      help="""the destination directory (will contain the 
                      organized MP3 files)""")
    parser.add_option("-t", "--tag", dest="tag", 
                      help="""the tag used for organization (can be artist, 
                      album, year or genre)""")

    (options, args) = parser.parse_args()
    
    if not options.source_dir:
        sys.stderr.write("Source directory not specified.\n")
        sys.stderr.write("See the help (--help option).\n")
        sys.exit(1)
    
    if not options.dest_dir:
        sys.stderr.write("Destination directory not specified.\n")
        sys.stderr.write("See the help (--help option).\n")
        sys.exit(1)
        
    if not options.tag:
        sys.stderr.write("Tag not specified.\n")
        sys.stderr.write("See the help (--help option).\n")
        sys.exit(1)

    valid_tags = set(['artist', 'album', 'year', 'genre'])

    if options.tag not in valid_tags:
        sys.stderr.write("An invalid tag was specified.\n")
        sys.stderr.write("See the help (--help option).\n")
        sys.exit(1)
        
    mp3_organizer = MP3Organizer(options.source_dir, 
                                 options.dest_dir, 
                                 options.tag)
    mp3_organizer.run()


if __name__ == "__main__":
    main()
