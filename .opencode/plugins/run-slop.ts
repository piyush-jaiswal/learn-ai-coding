import { execFile } from "node:child_process";
import { isAbsolute, resolve } from "node:path";

import { Plugin } from "@opencode/plugin";

interface RunSlopResult {
  stdout: string;
  stderr: string;
  exitCode: number;
}

function runSlop(filePath: string, projectRoot: string): Promise<RunSlopResult> {
  const absolutePath = isAbsolute(filePath) ? filePath : resolve(projectRoot, filePath);

  return new Promise((resolveResult) => {
    execFile(
      "uv",
      ["run", "--no-active", "sloperator.py", absolutePath],
      {
        cwd: projectRoot,
        timeout: 30_000,
        maxBuffer: 10 * 1024 * 1024,
      },
      (error, stdout, stderr) => {
        let exitCode = 0;

        if (error) {
          if (error.killed) {
            exitCode = 124;
          } else if (typeof error.code === "number") {
            exitCode = error.code;
          } else if (error.code === "ENOENT") {
            exitCode = 127;
          } else {
            exitCode = 1;
          }
        }

        resolveResult({
          stdout,
          stderr: stderr || (error && !stderr ? `${error.message}\n` : ""),
          exitCode,
        });
      },
    );
  });
}

export default Plugin.define({
  id: "applymaxxing.run-slop",
  setup: async (ctx) => {
    const projectRoot = ctx.location.directory;

    await ctx.tool.transform((tools) => {
      tools.add({
        name: "run_slop",
        description:
          "Run a SlopLang program with sloperator and return its stdout, stderr, and exit code as JSON. Relative paths are resolved from the project root.",
        input: {
          type: "object",
          properties: {
            path: {
              type: "string",
              description: "Path to the .slop file to run.",
            },
          },
          required: ["path"],
          additionalProperties: false,
        },
        output: {
          type: "object",
          properties: {
            stdout: { type: "string" },
            stderr: { type: "string" },
            exitCode: { type: "integer" },
          },
          required: ["stdout", "stderr", "exitCode"],
          additionalProperties: false,
        },
        options: { codemode: false },
        execute: async (input) => {
          const { path } = input as { path: string };
          const result = await runSlop(path, projectRoot);
          return { output: result };
        },
      });
    });

    await ctx.tool.transform((tools) => {
      tools.update("run_slop", (tool) => {
        tool.description +=
          " Use this tool to run individual .slop examples when checking language behavior. Use the test suite for regression testing.";
      });
    });
  },
});
