# Hancock 
![John Hancock's Signature](./hancock_signature.png)

A tool for finding and collating all of the function signatures in a git repository, particularly for the linux kernel.


## Usage

```bash
git clone https://github.com/zackmaril/hancock.git
cd hancock
git clone https://github.com/torvalds/linux.git artifacts/linux
poetry install
poetry run python hancock/main.py --repo artifacts/linux --output blobs/linux_functions
gzip blobs/linux_functions.json
# should be about 5.7mb gzip, 80mb unzipped.
```

## Motivation

[bpfquery.com](https://bpfquery.com) takes in sql, compiles it to bpftrace code and then runs and visualizes the results in real time. bpftrace lets you hook into the kprobes, which correspond to various linux kernel routines. While linux will tell you what kprobes are available on a specific instance, it doesn't tell you what the function arguments are nor the return type. This has meant that one has to do a bunch of CAST's when writing bpftrace programs in order to work with the pointers to various types, and it also makes it difficult to do typeahead completion with editors. So, I wrote this tool to crawl the linux kernel source and extract the function signatures from the code. 

# Design 

In flux. Right now it can dump out all the function signatures for a particular tagged release of the linux kernel into json. Next up, I want to be able to produce  a json blob for all tagged releases and produce a unified index. The goal of bpfquery is to let you do adhoc queries on any linux kernel release, so I want to have a single json blob that contains all the function signatures for all releases and see how big that gets.

## License

MIT

