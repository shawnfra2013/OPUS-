/*
 * ATTENTION: The "eval" devtool has been used (maybe by default in mode: "development").
 * This devtool is neither made for production nor for readable output files.
 * It uses "eval()" calls to create a separate source file in the browser devtools.
 * If you are trying to read the output file, select a different devtool (https://webpack.js.org/configuration/devtool/)
 * or disable the default devtool with "devtool: false".
 * If you are looking for production-ready output files, see mode: "production" (https://webpack.js.org/configuration/mode/).
 */
/******/ (() => { // webpackBootstrap
/******/ 	"use strict";
/******/ 	var __webpack_modules__ = ({

/***/ "./src/agentService.ts"
/*!*****************************!*\
  !*** ./src/agentService.ts ***!
  \*****************************/
(__unused_webpack_module, exports, __webpack_require__) {

eval("{\nvar __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {\n    if (k2 === undefined) k2 = k;\n    var desc = Object.getOwnPropertyDescriptor(m, k);\n    if (!desc || (\"get\" in desc ? !m.__esModule : desc.writable || desc.configurable)) {\n      desc = { enumerable: true, get: function() { return m[k]; } };\n    }\n    Object.defineProperty(o, k2, desc);\n}) : (function(o, m, k, k2) {\n    if (k2 === undefined) k2 = k;\n    o[k2] = m[k];\n}));\nvar __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {\n    Object.defineProperty(o, \"default\", { enumerable: true, value: v });\n}) : function(o, v) {\n    o[\"default\"] = v;\n});\nvar __importStar = (this && this.__importStar) || (function () {\n    var ownKeys = function(o) {\n        ownKeys = Object.getOwnPropertyNames || function (o) {\n            var ar = [];\n            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;\n            return ar;\n        };\n        return ownKeys(o);\n    };\n    return function (mod) {\n        if (mod && mod.__esModule) return mod;\n        var result = {};\n        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== \"default\") __createBinding(result, mod, k[i]);\n        __setModuleDefault(result, mod);\n        return result;\n    };\n})();\nObject.defineProperty(exports, \"__esModule\", ({ value: true }));\nexports.agentService = exports.AgentService = void 0;\nconst fs = __importStar(__webpack_require__(/*! fs */ \"fs\"));\nconst path = __importStar(__webpack_require__(/*! path */ \"path\"));\nconst OUTBOX_PATH = path.join(__dirname, '../ipc/outbox.jsonl');\nclass AgentService {\n    constructor() {\n        this.listeners = [];\n        this.startListening();\n    }\n    startListening() {\n        fs.watch(OUTBOX_PATH, (eventType, filename) => {\n            if (eventType === 'change') {\n                this.readOutbox();\n            }\n        });\n    }\n    readOutbox() {\n        fs.readFile(OUTBOX_PATH, 'utf-8', (err, data) => {\n            if (err) {\n                console.error('Error reading outbox:', err);\n                return;\n            }\n            const lines = data.trim().split('\\n');\n            const lastLine = lines[lines.length - 1] || '{}'; // Ensure lastLine is always a string\n            try {\n                const parsed = JSON.parse(lastLine);\n                this.notifyListeners(parsed);\n            }\n            catch (error) {\n                if (error instanceof Error) {\n                    console.error('Error parsing outbox line:', error.message);\n                }\n                else {\n                    console.error('Error parsing outbox line: Unknown error');\n                }\n            }\n        });\n    }\n    notifyListeners(data) {\n        this.listeners.forEach(listener => listener(data));\n    }\n    onNewMessage(callback) {\n        this.listeners.push(callback);\n    }\n}\nexports.AgentService = AgentService;\nexports.agentService = new AgentService();\n\n\n//# sourceURL=webpack://local-agent-vscode/./src/agentService.ts?\n}");

/***/ },

/***/ "fs"
/*!*********************!*\
  !*** external "fs" ***!
  \*********************/
(module) {

module.exports = require("fs");

/***/ },

/***/ "path"
/*!***********************!*\
  !*** external "path" ***!
  \***********************/
(module) {

module.exports = require("path");

/***/ }

/******/ 	});
/************************************************************************/
/******/ 	// The module cache
/******/ 	var __webpack_module_cache__ = {};
/******/ 	
/******/ 	// The require function
/******/ 	function __webpack_require__(moduleId) {
/******/ 		// Check if module is in cache
/******/ 		var cachedModule = __webpack_module_cache__[moduleId];
/******/ 		if (cachedModule !== undefined) {
/******/ 			return cachedModule.exports;
/******/ 		}
/******/ 		// Check if module exists (development only)
/******/ 		if (__webpack_modules__[moduleId] === undefined) {
/******/ 			var e = new Error("Cannot find module '" + moduleId + "'");
/******/ 			e.code = 'MODULE_NOT_FOUND';
/******/ 			throw e;
/******/ 		}
/******/ 		// Create a new module (and put it into the cache)
/******/ 		var module = __webpack_module_cache__[moduleId] = {
/******/ 			// no module.id needed
/******/ 			// no module.loaded needed
/******/ 			exports: {}
/******/ 		};
/******/ 	
/******/ 		// Execute the module function
/******/ 		__webpack_modules__[moduleId].call(module.exports, module, module.exports, __webpack_require__);
/******/ 	
/******/ 		// Return the exports of the module
/******/ 		return module.exports;
/******/ 	}
/******/ 	
/************************************************************************/
/******/ 	
/******/ 	// startup
/******/ 	// Load entry module and return exports
/******/ 	// This entry module is referenced by other modules so it can't be inlined
/******/ 	var __webpack_exports__ = __webpack_require__("./src/agentService.ts");
/******/ 	
/******/ })()
;