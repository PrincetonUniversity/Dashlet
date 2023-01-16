#!/usr/bin/env node
var fs = require("fs");
var path = require("path");
var recompiler = require("./recompiler.js");


var program = require('commander');
var version = require(path.join(__dirname, "..", "package.json")).version;
program
  .version(version)
  .option('-a, --arch [value]', 'processor architecture')
  .option('-e, --electron [value]', 'electron version')
  .parse(process.argv);



var directory = null;
if (fs.existsSync(process.argv[2])){
	directory = path.normalize(process.argv[2]);
} else {
	if (fs.existsSync(path.join(process.cwd(), process.argv[2]))){
		directory = path.join(process.cwd(), process.argv[2]);
	} else {
		directory = path.normalize(process.cwd());
	}
}

console.log("directory");
console.log(directory);
fs.exists(directory, function(exists){
	var config = {}
	config.arch = (program.arch || process.arch);
	if (exists){
		config.dir = directory;
		config.electronVersion = (program.electron || recompiler.getElectronVersion(directory));
		recompiler.run(config);
	} else {
		directory = path.resolve(process.cwd(), process.argv[2], "node_modules");
		fs.exists(directory, function(exsts){
			if (exsts){
				config.dir = directory;
				config.electronVersion = (program.electron || recompiler.getElectronVersion(directory));
				recompiler.run(directory);
			}
		});
	}
});
