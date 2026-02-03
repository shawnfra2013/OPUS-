# Issue Log

## Purpose
This document logs all encountered issues, their causes, resolutions, and steps to prevent them in the future. It serves as a reference to avoid repeating mistakes during future rebuilds.

---

## Issue 1: `multer` Type Issue
- **Description**: The `Express.Multer.File` type was not recognized, causing TypeScript errors.
- **Cause**: The `multer` package does not export the `File` type directly. Instead, it is part of the global `Express` namespace.
- **Resolution**: Reverted the explicit import of `File` from `multer` and restored the use of `Express.Multer.File`.
- **Prevention**: Ensure the `@types/multer` and `@types/express` packages are installed and correctly resolve the global namespace.

---

## Issue 2: Decorator Warnings
- **Description**: Warnings about `experimentalDecorators` and `emitDecoratorMetadata` persist.
- **Cause**: These warnings occur when TypeScript is not configured to support experimental decorators.
- **Resolution**: Verified that `tsconfig.json` includes `"experimentalDecorators": true` and `"emitDecoratorMetadata": true`.
- **Prevention**: Always verify TypeScript configurations when using frameworks like NestJS that rely on decorators.

---

## Issue 3: Jest and Mocha Conflicts
- **Description**: Type conflicts between Jest and Mocha.
- **Cause**: Both Jest and Mocha type definitions were installed, leading to conflicts.
- **Resolution**: Exclude one of the libraries and its type definitions.
- **Prevention**: Use only one testing framework and its corresponding type definitions.

---

## Issue 4: Node.js Type Errors
- **Description**: Errors related to `Symbol.dispose`, `asyncDispose`, and missing `Disposable` types.
- **Cause**: Mismatch between the Node.js version and the installed `@types/node` package.
- **Resolution**: Update the `@types/node` package to match the Node.js version.
- **Prevention**: Ensure the `@types/node` package version aligns with the Node.js runtime version.

---

## Next Steps
- Continue logging issues and resolutions.
- Update internal configurations and dependencies to prevent recurring issues.
- Train the model internally to ensure it learns from these mistakes.