#!/usr/bin/env node
'use strict';

const fs = require('fs');
const path = require('path');

function patchDistFiles() {
  const filesToPatch = [
    'node_modules/ember-source/dist/ember.debug.js',
    'node_modules/ember-source/dist/ember.prod.js',
    'node_modules/ember-source/dist/ember.min.js',
    'node_modules/ember-source/dist/ember-template-compiler.js',
  ];

  const exportLine = '_exports.arrayLikeToArray = arrayLikeToArray;';
  const markerLine = '_exports.createForOfIteratorHelperLoose = createForOfIteratorHelperLoose;';

  for (const relPath of filesToPatch) {
    const filePath = path.join(__dirname, '..', relPath);
    
    if (!fs.existsSync(filePath)) {
      console.log(`Skipping ${relPath} - file not found`);
      continue;
    }
    
    let content = fs.readFileSync(filePath, 'utf8');
    
    if (content.includes(exportLine)) {
      console.log(`Skipping ${relPath} - already patched`);
      continue;
    }
    
    if (!content.includes(markerLine)) {
      console.log(`Skipping ${relPath} - marker line not found`);
      continue;
    }
    
    content = content.replace(
      markerLine,
      markerLine + '\n  ' + exportLine
    );
    
    fs.writeFileSync(filePath, content);
    console.log(`Patched ${relPath}`);
  }
}

function patchSourceModule() {
  const sourceFile = path.join(__dirname, '..', 'node_modules/ember-source/dist/packages/ember-babel.js');
  
  if (!fs.existsSync(sourceFile)) {
    console.log('Skipping ember-babel.js source - file not found');
    return;
  }
  
  let content = fs.readFileSync(sourceFile, 'utf8');
  
  if (content.includes('export { arrayLikeToArray }') || content.includes('export function arrayLikeToArray')) {
    console.log('Skipping ember-babel.js source - already patched');
    return;
  }
  
  const oldFunctionDef = 'function arrayLikeToArray(arr, len) {';
  const newFunctionDef = 'export function arrayLikeToArray(arr, len) {';
  
  if (!content.includes(oldFunctionDef)) {
    console.log('Skipping ember-babel.js source - function definition not found');
    return;
  }
  
  content = content.replace(oldFunctionDef, newFunctionDef);
  fs.writeFileSync(sourceFile, content);
  console.log('Patched node_modules/ember-source/dist/packages/ember-babel.js');
}

console.log('Patching ember-babel exports...');
patchDistFiles();
patchSourceModule();
console.log('Done patching ember-babel exports');
