var os = require("os");
var fs = require("fs");
var path = require('path');
var packageController = require("package.js");

var NMP = require('nmp');
var nmp = new NMP();

var colors = require('colors');
var child_process = require('child_process');
var fse = require('fs-extra');
var binaries = [];

var getElectronVersion = function(rootDirectory) {
	var result = null;

	if (fs.existsSync(path.join(rootDirectory, "node_modules", "electron-prebuilt", "package.json"))){
		result = require(path.join(rootDirectory, "node_modules", "electron-prebuilt", "package.json")).version;
	}

	if (!result){
		console.log(("could not determine electron version from project path " + path.join(rootDirectory, "electron-prebuilt", "package.json") + ". Try --electron to force a version.").red);
		process.exit(1);
	}
	return result;
}


var Batch = function(module){
	this.module = module;
	this.script = [];
	return this;
}

Batch.prototype.execute = function(script) {
	var done;
		done = false
		var color = script.color || colors.cyan;
		console.log(color(script.cmd), script.args);
		var res = ";";
		try{
			var extend = require('util')._extend;
			var options = extend({}, script.options); // clone
			res = child_process.spawnSync(script.cmd, script.args, options);
			if (typeof(res) === "object"){
				if (res.error){
					console.log(color.red(res.error.message), script.options);
				} else {
					if (res.stderr){
						if (res.status === 0){
							done = true;
							console.log(color.green(res.stderr.toString()));
						} else {
							console.log(color.red(res.stderr.toString()));
						}
					}
				}
			} else {
				console.log(color.blue(res));
			}
			//child_process.execSync(script.cmd, script.options);
		} catch(e){
			console.log(colors.red("Failed to compile : " + this.module.meta.name));
			console.log(colors.red(e), script.options);
			console.log(colors.red(res));
		}
	return done;
};


var processModule = function(module) {
	var fn = path.join(module.dir, "binding.gyp");
	if (fs.existsSync(fn) && module.meta && module.meta.repository && module.meta.repository.url){
		console.log(colors.yellow("found: " + fn));
		console.log("compile".magenta, module.meta.name.green);
		var repoUrl = module.meta.repository.url;
		if (repoUrl.indexOf("+") !== -1){
			repoUrl = repoUrl.split("+")[1];
		}

		var isWindows = (os.platform() === "win32" || os.platform() === "win64");
		var tmp = path.join(__dirname, "..", "tmp", module.meta.name + "@" + module.meta.version);
		var batch = new Batch(module);
		var options = {
			cwd   : tmp
		};
		var options2 = {
			cwd : tmp,
			env : {"HOME": path.join(tmp, "..", "electronGypHome") + "\\"}
		};


		var gypFile = path.join(tmp, "binding.gyp");
		fse.removeSync(tmp);

		batch.execute({cmd:"git", args: ["clone", "--depth=1", repoUrl, tmp]});
		if (fs.existsSync(gypFile)){


			batch.execute({cmd:"npm" + (isWindows ? ".cmd" : ""), args: ["install"], options: options});


			var args = ["rebuild", "--target=" + module.config.electronVersion, "--arch=" + module.config.arch, "--dist-url=https://atom.io/download/atom-shell" ];
			if (module.meta.name === "sqlite3"){
				// FIXME : how to determine module target name?
				args.push("--module_name=node_sqlite3");
				args.push("--module_path=build/release");
			}

			batch.execute({cmd:"node-gyp" + (isWindows ? ".cmd" : ""), args: args, options: options2});

			var targetOut = path.join(module.dir, "bin", nmp.versionString()); //path.join(rootDirectory, "..", "electron-recompiled", "electron-v" + electronVersion + "_" + arch + "_" + this.meta.name + "-v" + this.meta.version);

			//batch.execute({cmd:"mkdir", args: ["-p", targetOut]});
			fse.mkdirsSync(targetOut);
			binaries.push(targetOut);
			var options3 = {cwd : path.join(tmp, "build", "release")};
			batch.execute({cmd:"cp", args: ["-f", "*.node", targetOut], options: options3});
		}

	}
	return false;
};

var run = function(config) {
	if (!config.arch){
		config.arch = process.arch;
	}
	if (!config.electronVersion){
		config.electronVersion = process.versions.electron;
	}

	console.log("recompiling native modules in", config.dir.yellow, "processor:".magenta, config.arch.cyan, "electron:".magenta, config.electronVersion.cyan, "v8:".magenta, process.versions.v8.cyan);

	packageController.autoload({
		debug: true,
		directoryScanLevel: 200,
		identify: function  () {
			this.config = config;
			processModule(this);
			//npm install --ignore-scripts
			return false;
		},
		directories: [config.dir],
		packageContstructorSettings: {}
	});

	console.log(colors.blue("testing..."));
	for (var i = 0; i < binaries.length; i++) {
		var bin = binaries[i];
		var files = fs.readdirSync(bin);
		var found = false;
		for(var f in files) {
			if(path.extname(files[f].toLowerCase()) === ".node") {
				found = true;
				break;
			}
		}
		if (found){
			console.log(colors.green(bin), colors.green("OK") );
		} else {
			console.log(colors.red(bin), colors.red("failed!") );
	  	}
	}
	console.log(colors.blue("done."));
};


module.exports = {
	run:run,
	getElectronVersion:getElectronVersion
}