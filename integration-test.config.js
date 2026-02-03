module.exports = {
  testEnvironment: 'node',
  verbose: true,
  testMatch: ['**/?(*.)+(spec|test).[jt]s?(x)'],
  transform: {
    '^.+\\.(t|j)s$': 'ts-jest',
  },
};