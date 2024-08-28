#Use gitpython to read the tags of artifact/linux

import os
import sys
import json
import re
import subprocess
import multiprocessing
import argparse
from functools import partial

def get_indexed_tags(repo_path):
    # run tags command
    tags = subprocess.check_output(['git', 'tag'], cwd=repo_path)
    # Split the tags by newline
    tags = tags.decode('utf-8').split('\n')
    # Remove the last newline
    tags = tags[:-1]
    # Return the tags
    #filter out all rcx tags
    tags = [tag for tag in tags if re.match(r'v[0-9]+\.[0-9]+$', tag)]

    indexed_tags = []
    for tag in tags:
        # strip the v and split into major and minor
        major, minor = tag[1:].split('.')
        indexed = int(major) * 100 + int(minor)
        indexed_tags.append((indexed, tag))
        
    indexed_tags.sort()
    return indexed_tags 
    

def extract_functions_from_file(repo_path, file_path):
    fp = os.path.join(repo_path, file_path)
    # Use ctags with the specified options to extract function prototypes
    cmd = [
        'ctags', '--output-format=json', '--fields=+Stn', '--kinds-C=+p', '--c-types=fp', '--extras=+q', '-o', '-',
        fp
    ]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, text=True)
    
    # get the short file_path 
    short_path = os.path.relpath(file_path, repo_path)
    functions = []
    for line in result.stdout.splitlines():
        tag = json.loads(line)
        if tag.get("name").lower() != tag.get("name"):
            continue
        
        if tag.get('_type') == 'tag' and tag.get('kind') in ['function', 'prototype']:
            function_name = tag.get('name')
            line_number = int(tag.get('line'))
            signature = tag.get('signature', '')
            if signature != '':
                #remove parens 
                signature = signature[1:-1]
                signature = signature.split(",")
            typeref = tag.get('typeref', '')
            typeref = typeref.split(':')[1] if typeref else ''
            functions.append((short_path, function_name, line_number, typeref, signature))
    
    return functions


def process_files(files, repo_path):
    with multiprocessing.Pool() as pool:
        functions = pool.map(partial(extract_functions_from_file, repo_path), files)
        functions = [f for sublist in functions for f in sublist]
    return functions

def get_files_for_tag(tag, repo_path):
    files = subprocess.check_output(['git', 'ls-tree', '-r', '--name-only', tag], cwd=repo_path)
    files = files.decode('utf-8').split('\n')
    files = files[:-1]
    # only .c and .h files
    files = [file for file in files if file.endswith('.c') or file.endswith('.h')]
    return files

def get_files_for_diff(tag1, tag2, repo_path):
    files = subprocess.check_output(['git', 'diff', '--name-only', f'{tag1}..{tag2}'], cwd=repo_path)
    files = files.decode('utf-8').split('\n')
    files = files[:-1]
    # only .c and .h files
    files = [file for file in files if file.endswith('.c') or file.endswith('.h')]
    return files

def dump_functions_for_tag(tag, repo_path, output_path):
    print(f"Processing {tag}")
    output_path = os.path.join(output_path, f"{tag}.json")
    if os.path.exists(output_path):
        print(f"Skipping {tag} because {output_path} already exists")
        return
    output = subprocess.run(['git', 'checkout', '-f', tag], cwd=repo_path)
    files = get_files_for_tag(tag, repo_path)
    functions = process_files(files, repo_path)
    with open(output_path, 'w') as f:
        json.dump(functions, f, indent=2)
    print(f"Wrote {len(functions)} functions to {output_path}")

def main():
    # Get command line args
    parser = argparse.ArgumentParser()
    parser.add_argument('--repo', type=str, default='artifacts/linux', help='Path to the repository')
    parser.add_argument('--output', type=str, default='blobs/linux_functions', help='Path to the output file')
    args = parser.parse_args()

    # Make the output directory
    os.makedirs(args.output, exist_ok=True)

    # Get the tags
    tags = get_indexed_tags(args.repo)
    
    print(f"Processing {len(tags)} tags")

    # Get the functions all the files with the first tag 
    for tag in tags:
        dump_functions_for_tag(tag[1], args.repo, args.output)

    # # get list of files that changed for each tag 
    # for i in range(1, len(tags)):
    #     tag1 = tags[i-1][1]
    #     tag2 = tags[i][1]
    #     files = get_files_for_diff(tag1, tag2, args.repo)
    #     print(f"Comparing {tag1} to {tag2}, {len(files)} files changed")
    


if __name__ == '__main__':
    main()
