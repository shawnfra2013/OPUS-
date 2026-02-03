const path = require('path');

module.exports = {
  entry: './src/agentService.ts',
  output: {
    filename: 'main.js',
    path: path.resolve(__dirname, 'dist')
  },
  mode: 'development',
  resolve: {
    extensions: ['.ts', '.js'],
    fallback: {
      "fs": false,
      "path": require.resolve("path-browserify")
    }
  },
  module: {
    rules: [
      {
        test: /\.ts$/,
        use: 'ts-loader',
        exclude: /node_modules/
      }
    ]
  },
  target: 'node' // Add this line to handle Node.js built-in modules like 'fs' and 'path'
};