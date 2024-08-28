#A python script that takes a glob and makes a chart of the file sizes.

import matplotlib.pyplot as plt
import glob
import os
import json

def plot_file_sizes():
    # Get the file sizes
    file_sizes = {}
    for file in glob.glob("./blobs/linux_functions/*.json"):
        #convert the vx.x to a number 
        major, minor, _ = file.split("/")[-1][1:].split(".")

        file_sizes[major + "." + minor] = os.path.getsize(file) / 1024 / 1024
    

    #sort the file sizes by the version number
    file_sizes = dict(sorted(file_sizes.items(), key=lambda x: x[0]))

    # Make a chart of the file sizes
    plt.bar(file_sizes.keys(), file_sizes.values())
    # only show the x tick labels for every 5 minor versions within a major version
    to_show = []
    for major in [3,4,5,6]:
        minor_versions = [version for version in file_sizes.keys() if version.startswith(str(major))]
        to_show.append(minor_versions[0])
    plt.xticks(to_show, to_show, rotation=45)

    # set the y axis to be in mb
    plt.ylabel('File Size (mb)')
    plt.xlabel('Linux Kernel Version ')

    # Get the file sizes
    file_sizes = {}
    for file in glob.glob("./blobs/linux_functions/*.json.gz"):
        #convert the vx.x to a number 
        major, minor, _, _ = file.split("/")[-1][1:].split(".")

        file_sizes[major + "." + minor] = os.path.getsize(file) / 1024 / 1024
    
    # sort the file sizes by the version number
    file_sizes = dict(sorted(file_sizes.items(), key=lambda x: x[0]))
    
    plt.bar(file_sizes.keys(), file_sizes.values())
    plt.legend(['Size of JSON blob', "Compressed"])

    # also plot the number of functions per version
    num_functions = {}
    for file in glob.glob("./blobs/linux_functions/*.json"):
        major, minor, _ = file.split("/")[-1][1:].split(".")
        #load the json file
        with open(file, "r") as f:
            data = json.load(f)
        num_functions[major + "." + minor] = len(data)
    # second y axis
    ax2 = plt.twinx()
    #sort the num_functions by the version number
    num_functions = dict(sorted(num_functions.items(), key=lambda x: x[0]))
    ax2.plot(num_functions.keys(), num_functions.values(), color='red')
    ax2.set_ylabel('Number of Functions')

    ax2.legend(['Number of Functions'], loc=1)


    plt.title('Size of JSON blob of Signatures and Number of Functions per Version')
    plt.tight_layout()
    plt.savefig('chart.png')
    
def get_stats():
    #Get total size of all the json blobs
    total_size_uncompressed = 0
    for file in glob.glob("./blobs/linux_functions/*.json"):
        total_size_uncompressed += os.path.getsize(file) / 1024 / 1024
    print(f"Total size of all the json blobs: {total_size_uncompressed} mb")

    #Get total size of all the json blobs compressed
    total_size = 0
    for file in glob.glob("./blobs/linux_functions/*.json.gz"):
        total_size += os.path.getsize(file) / 1024 / 1024
    print(f"Total size of all the json blobs compressed: {total_size} mb")

    # Get the ratio of the compressed size to the uncompressed size
    print(f"Compression ratio: {total_size / total_size_uncompressed}")





def main():
    plot_file_sizes()
    get_stats()

if __name__ == "__main__":
    main()
