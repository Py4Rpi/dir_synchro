import os
import time
import sched
import shutil
import hashlib
import logging
import argparse

from dirhash import dirhash


def pth_validate(pth):
    if os.path.isdir(pth):
        return pth
    else:
        raise argparse.ArgumentTypeError(f"INCORRECT PATH:   {pth}")


def log_pth_validate(pth):
    filename, file_extension = os.path.splitext(pth)
    if os.path.isfile(pth):
        return pth
    elif file_extension == '.log':
        return pth
    else:
        raise argparse.ArgumentTypeError(f"INCORRECT PATH OR FILE NAME:   {pth}")


parser = argparse.ArgumentParser()
parser.add_argument('input', type=pth_validate, help="Source folder path")
parser.add_argument('output', type=pth_validate, help="Replica folder path")
parser.add_argument('log', type=log_pth_validate, help="Log file path\\name.log")
parser.add_argument('interval', type=int, help="Interval between synchronization (seconds)")
args = parser.parse_args()

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s',
                    level=logging.INFO,
                    filename=args.log)

s = sched.scheduler(time.time, time.sleep)


#   DIRECTORY SYNCHRONIZATION FUNCTION

def synchronization():
    inpath = args.input
    outpath = args.output
    pthjoin = os.path.join
    pthbase = os.path.basename
    lstdr = os.listdir
    dst_pth = pthjoin(outpath, pthbase(inpath))

    def rm_tree(dst):  # DIR REMOVAL
        shutil.rmtree(dst)
        print(f"Delete {dst}\n")
        logging.info(f"Delete {dst}\n")

    def copy_tree(src, dst):  # DIR COPY
        shutil.copytree(f"{src}", f"{dst}")
        print(f'Copy {dst}\n')
        logging.info(f"Copy {dst}\n")

    if not os.path.exists(inpath):  # CHK IF SRC PATH EXISTS
        print(f'Source directory does not exist {inpath}\n')
        logging.info(f'Source directory does not exist {inpath}\n')

    elif not os.path.exists(dst_pth):

        copy_tree(inpath, dst_pth)

    elif not len(lstdr(inpath)):  # CHK IF SRC IS EMPTY

        if len(lstdr(dst_pth)):
            rm_tree(dst_pth)
            copy_tree(inpath, dst_pth)

        elif not len(lstdr(dst_pth)):
            print('Source directory is empty, nothing to sync\n')

    elif len(lstdr(inpath)):
        if not len(lstdr(dst_pth)):
            rm_tree(dst_pth)
            copy_tree(inpath, dst_pth)

        elif len(lstdr(dst_pth)):
            if dirhash(inpath, 'md5') == dirhash(dst_pth, 'md5'):  # COMPARING HASH OF SRC AND DST DIRS
                print("Directories synchronization - OK\n")


            else:  # MAIN SYNC CODE

                input_files = []
                output_files = []
                input_dirs = []
                output_dirs = []

                # COMPARE THE SUBDIRS BY OS.WALK AND MAKE THE LISTS OF TUPLES WITH RESULTS

                for in_root, in_dirs, in_files in os.walk(inpath):  # SCAN SRC DIR

                    sync_pth = pthjoin(outpath, *in_root.split("\\")[(len(inpath.split("\\")) - 1):])

                    for in_file in in_files:  # ADD SRC FILES
                        input_files.append(
                            (f"{hashlib.md5(open(f'{pthjoin(in_root, in_file)}', 'rb').read()).hexdigest()}",
                             f'{in_file}',))

                    for dir in in_dirs:  # ADD SRC DIRS

                        if len(lstdr(pthjoin(in_root, dir))):
                            input_dirs.append(((dirhash(pthjoin(in_root, dir), 'md5')), dir,))

                        else:
                            input_dirs.append(('empty', dir))  # FOR MTY DIRS

                    for out_root, out_dirs, out_files in os.walk(sync_pth):  # SCAN DST DIR

                        for out_file in out_files:  # ADD DST FILES
                            output_files.append(
                                (f"{hashlib.md5(open(f'{pthjoin(out_root, out_file)}', 'rb').read()).hexdigest()}",
                                 f'{out_file}',))

                        for out_dir in out_dirs:  # ADD DST DIRS
                            if len(lstdr(pthjoin(out_root, out_dir))):
                                output_dirs.append(((dirhash(pthjoin(out_root, out_dir), 'md5')), out_dir,))

                            else:
                                output_dirs.append(('empty', out_dir))  # FOR MTY DIRS

                        break

                    # IF FILES NOT SYNC

                    if frozenset(input_files).difference(output_files) or frozenset(output_files).difference(
                            input_files):

                        # DELETE FILES FM DST
                        for hs, nm in frozenset(output_files).difference(input_files):
                            fdst_pth = str(pthjoin(sync_pth, nm))
                            os.remove(fdst_pth)
                            print(f"Delete {fdst_pth}\n")
                            logging.info(f"Delete {fdst_pth}\n")

                        # COPY FILES TO DST
                        for hs, nm in frozenset(input_files).difference(output_files):
                            fsrc_pth = str(pthjoin(in_root, nm))
                            fdst_pth = str(pthjoin(sync_pth, nm))
                            if os.path.exists(sync_pth):
                                shutil.copy2(fsrc_pth, fdst_pth)
                                print(f"Copy {fsrc_pth} to {fdst_pth}\n")
                                logging.info(f"Copy {fsrc_pth} to {fdst_pth}\n")

                        input_files.clear()
                        output_files.clear()

                    # IF SUBDIRS NOT SYNC

                    if frozenset(input_dirs).difference(output_dirs) or frozenset(output_dirs).difference(input_dirs):
                        for hs, nm in frozenset(input_dirs).difference(output_dirs):
                            dir_same_hash_diff_name = [it for it in frozenset(output_dirs).difference(input_dirs)
                                                       if it[0] == hs and it[1] != nm]

                            # RENAME DIRS IN DST
                            if dir_same_hash_diff_name:
                                src_pth = str(pthjoin(sync_pth, dir_same_hash_diff_name[0][1]))
                                dst_pth = str(pthjoin(sync_pth, nm))
                                os.rename(src_pth, dst_pth)
                                print(f"Rename {src_pth} to {dst_pth}\n")
                                logging.info(f"Rename {src_pth} to {dst_pth}\n")

                        # DELETE DIRS IN DST
                        for hs, nm in frozenset(output_dirs).difference(input_dirs):

                            out_dir_diff_hash_diff_name = [it for it in
                                                           frozenset(input_dirs).difference(output_dirs)
                                                           if it[1] == nm]

                            if not out_dir_diff_hash_diff_name:
                                dst_pth = str(pthjoin(sync_pth, nm))

                                rm_tree(dst_pth)

                        # COPY DIR TO DST

                        for hs, nm in frozenset(input_dirs).difference(output_dirs):

                            in_dir_diff_hash_diff_name = [it for it in
                                                          frozenset(output_dirs).difference(input_dirs)
                                                          if it[0] == hs or it[1] == nm]

                            if not in_dir_diff_hash_diff_name:
                                src_pth = str(pthjoin(in_root, nm))
                                dst_pth = str(pthjoin(sync_pth, nm))

                                try:

                                    rm_tree(dst_pth)

                                except:
                                    pass
                                copy_tree(src_pth, dst_pth)

                        input_dirs.clear()
                        output_dirs.clear()

                        continue


                    # ALL DIRS AND FILES SYNC OK

                    else:
                        input_files.clear()
                        output_files.clear()
                        input_dirs.clear()
                        output_dirs.clear()
                        print("Directories synchronization - OK\n")

                        break


if __name__ == "__main__":
    print("\nDirectories synchronization running\n"
          f"Input: {args.input}\n"
          f"Output: {args.output}\n"
          f"Log file: {args.log}\n\n")

    logging.info(f"Directories synchronization running.\n"
                 f"Input: {args.input},\n"
                 f"Output: {args.output},\n"
                 f"Log file: {args.log}.\n")

    try:
        while True:
            s.enter(args.interval, 0, synchronization)  # SCHEDULER
            s.run()

    except KeyboardInterrupt:  # STOP EXEC BY CTRL+C
        print("Directories synchronization terminated by Ctrl+C\n")
        logging.info("Directories synchronization terminated by Ctrl+C\n")

        pass
