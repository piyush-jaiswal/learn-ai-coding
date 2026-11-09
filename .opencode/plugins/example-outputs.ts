import { execFile } from "node:child_process";
import { readdir } from "node:fs/promises";
import { basename, isAbsolute, join, resolve } from "node:path";

import { Plugin } from "@opencode/plugin";

interface ExampleResult {
  name: string;
  exitCode: number;
  firstLine: string;
}

function runExample(filePath: string, projectRoot: string): Promise<ExampleResult> {
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
      (error, stdout) => {
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

        const [firstLine = ""] = stdout.split(/\r?\n/, 1);

        resolveResult({
          name: basename(absolutePath),
          exitCode,
          firstLine,
        });
      },
    );
  });
}

export default Plugin.define({
  id: "applymaxxing.example-outputs",
  setup: async (ctx) => {
    const projectRoot = ctx.location.directory;

    await ctx.tool.transform((tools) => {
      tools.add({
        name: "example_outputs",
        description:
          "Run every examples/*.slop program and return each example's filename, exit code, and first output line.",
        input: {
          type: "object",
          properties: {},
          additionalProperties: false,
        },
        output: {
          type: "object",
          properties: {
            examples: {
              type: "array",
              items: {
                type: "object",
                properties: {
                  name: { type: "string" },
                  exitCode: { type: "integer" },
                  firstLine: { type: "string" },
                },
                required: ["name", "exitCode", "firstLine"],
                additionalProperties: false,
              },
            },
          },
          required: ["examples"],
          additionalProperties: false,
        },
        options: { codemode: false },
        execute: async () => {
          const examplesDirectory = join(projectRoot, "examples");
          const entries = await readdir(examplesDirectory, { withFileTypes: true });
          const filenames = entries
            .filter((entry) => entry.isFile() && entry.name.endsWith(".slop"))
            .map((entry) => entry.name)
            .sort((a, b) => a.localeCompare(b));

          const examples = await Promise.all(
            filenames.map((filename) =>
              runExample(join(examplesDirectory, filename), projectRoot),
            ),
          );

          return { output: { examples } };
        },
      });
    });
  },
});
