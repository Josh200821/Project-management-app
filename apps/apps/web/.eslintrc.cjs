/**
 * ESLint config for the React 18 + TypeScript + Vite frontend.
 *
 * There was no ESLint config file anywhere in apps/web, so `npm run lint`
 * (`eslint src --ext ts,tsx`) failed immediately with "ESLint couldn't find
 * a configuration file" — it never got as far as checking any actual code.
 */
module.exports = {
  root: true,
  env: { browser: true, es2020: true, node: true },
  extends: [
    'eslint:recommended',
    'plugin:@typescript-eslint/recommended',
    'plugin:react/recommended',
    'plugin:react/jsx-runtime', // React 18's new JSX transform — no `import React` needed
    'plugin:react-hooks/recommended',
  ],
  ignorePatterns: ['dist', '.eslintrc.cjs', 'vite.config.ts', 'tailwind.config.ts', 'postcss.config.js'],
  parser: '@typescript-eslint/parser',
  parserOptions: {
    ecmaVersion: 'latest',
    sourceType: 'module',
    ecmaFeatures: { jsx: true },
  },
  plugins: ['react-refresh'],
  settings: {
    react: { version: 'detect' },
  },
  rules: {
    'react-refresh/only-export-components': ['warn', { allowConstantExport: true }],
    '@typescript-eslint/no-unused-vars': ['warn', { argsIgnorePattern: '^_' }],
    '@typescript-eslint/no-explicit-any': 'warn',
    'react/prop-types': 'off', // TypeScript covers this
  },
}
