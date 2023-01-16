# electron-recompile

## Installation
```bash
$ npm install -g electron-recompile;
```

## Usage
```bash
index [folder] [options]

Options:

  -h, --help              output usage information
  -V, --version           output the version number
  -a, --arch [value]      processor architecture
  -e, --electron [value]  electron version

```

## Example
Recompiled native modules to ```your-project-path/electron-recompiled```
```bash
$ cd your-project-path;
$ npm install electron-prebuilt;
$ electron-recompile;
```

## Dependencies
 - [Node.js](https://nodejs.org/)
 - [git commands](https://git-scm.com/downloads)
 - [Linux bash commands](https://git-scm.com/downloads) also available on windows via git bash.
 - [node-gyp](https://github.com/TooTallNate/node-gyp/) ```npm install node-gyp@latest```
 - A c++ compiler on Windows [Microsoft Visual C++ 2015 Express](#) works best ```npm config set msvs_version=2015 --global``` ```set GYP_MSVS_VERSION=2010```
