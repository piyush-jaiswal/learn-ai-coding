import { execFile } from "node:child_process";

import { Plugin } from "@opencode/plugin";

interface LessonInfo {
  uuid: string;
  chapter: number;
  lesson: number;
  title: string;
  chapterTitle?: string;
  course?: string;
}

interface CommandResult {
  stdout: string;
  stderr: string;
  exitCode: number;
}

interface CommitMessage {
  message: string;
  source: "lesson" | "custom";
  chapter?: number;
  lesson?: number;
  title?: string;
  course?: string;
}

export interface CommitResult extends CommitMessage, CommandResult {
  committed: boolean;
}

export interface CommitMessageInput {
  url?: string;
  summary?: string;
  message?: string;
}

const LESSON_URL = "https://www.boot.dev/lessons/";
const UUID_RE = /[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}/i;
const NAMED_ENTITIES: Record<string, string> = {
  amp: "&",
  apos: "'",
  gt: ">",
  lt: "<",
  nbsp: " ",
  quot: '"',
};

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function decodeEntities(text: string): string {
  return text.replace(/&(#x?[0-9a-f]+|[a-z]+);/gi, (entity, code: string) => {
    if (code.startsWith("#")) {
      const hex = code[1]?.toLowerCase() === "x";
      const value = Number.parseInt(code.slice(hex ? 2 : 1), hex ? 16 : 10);
      return Number.isFinite(value) ? String.fromCodePoint(value) : entity;
    }

    return NAMED_ENTITIES[code.toLowerCase()] ?? entity;
  });
}

/**
 * Resolve a value from a Nuxt/devalue payload. Object properties in the payload
 * are references into the top-level array; the value they point at may itself
 * be a literal (number, string) or another object.
 */
function deref(data: unknown[], value: unknown): unknown {
  if (Array.isArray(value) && value.length === 2 && value[0] === "Ref") {
    return deref(data, value[1]);
  }

  if (typeof value === "number" && Number.isInteger(value) && value >= 0 && value < data.length) {
    return data[value];
  }

  return value;
}

function asString(value: unknown): string | undefined {
  if (typeof value !== "string") {
    return undefined;
  }

  const text = decodeEntities(value).replace(/\s+/g, " ").trim();
  return text ? text : undefined;
}

function asPositiveInteger(value: unknown): number | undefined {
  const number = typeof value === "number" ? value : Number(value);
  return Number.isInteger(number) && number > 0 ? number : undefined;
}

export function extractLessonUuid(value: string): string {
  const raw = value.trim();

  if (UUID_RE.test(raw) && !raw.includes("/") && !raw.includes(":")) {
    return raw.match(UUID_RE)![0].toLowerCase();
  }

  let url: URL;
  try {
    url = new URL(raw);
  } catch {
    throw new Error(`Invalid boot.dev lesson URL: ${raw}`);
  }

  if (url.hostname !== "boot.dev" && !url.hostname.endsWith(".boot.dev")) {
    throw new Error(`Expected a boot.dev lesson URL, got host "${url.hostname}"`);
  }

  const match = url.pathname.match(UUID_RE);
  if (!match) {
    throw new Error(`Could not find a lesson UUID in ${url.toString()}`);
  }

  return match[0].toLowerCase();
}

export function parseLessonPage(html: string, expectedUuid?: string): LessonInfo {
  const script = html.match(/<script[^>]*\bid="__NUXT_DATA__"[^>]*>([\s\S]*?)<\/script>/i);
  if (!script) {
    throw new Error("Could not find the lesson metadata payload on the boot.dev page");
  }

  let data: unknown;
  try {
    data = JSON.parse(script[1]);
  } catch {
    throw new Error("Could not parse the lesson metadata payload from boot.dev");
  }

  if (!Array.isArray(data)) {
    throw new Error("Unexpected lesson metadata payload from boot.dev");
  }

  const candidates: LessonInfo[] = [];

  for (const entry of data) {
    if (!isRecord(entry) || !("lesson" in entry) || !("chapterNumber" in entry) || !("lessonNumber" in entry)) {
      continue;
    }

    const lesson = deref(data, entry.lesson);
    if (!isRecord(lesson)) {
      continue;
    }

    const chapter = asPositiveInteger(deref(data, entry.chapterNumber));
    const lessonNumber = asPositiveInteger(deref(data, entry.lessonNumber));
    const title = asString(deref(data, lesson.title));

    if (chapter === undefined || lessonNumber === undefined || !title) {
      continue;
    }

    candidates.push({
      uuid: asString(deref(data, lesson.uuid))?.toLowerCase() ?? "",
      chapter,
      lesson: lessonNumber,
      title,
      chapterTitle: asString(deref(data, lesson.chapterTitle)),
      course: asString(deref(data, lesson.courseTitle)),
    });
  }

  if (candidates.length === 0) {
    throw new Error("Could not determine the chapter, lesson, and title from the boot.dev page");
  }

  const matching = expectedUuid
    ? candidates.find((candidate) => candidate.uuid === expectedUuid.toLowerCase())
    : undefined;

  return matching ?? candidates[0];
}

/** Collapse arbitrary text into one line, preserving the caller's wording. */
export function normalizeMessage(value: string): string {
  return value.replace(/\s+/g, " ").trim();
}

/** Collapse text into one line and drop the trailing period that repo commits avoid. */
export function normalizeSummary(value: string): string {
  const summary = normalizeMessage(value).replace(/[.!?]+$/, "");
  if (!summary) {
    throw new Error("A non-empty summary is required");
  }

  return summary;
}

export function formatCommitMessage(input: CommitMessageInput & { lesson?: LessonInfo }): CommitMessage {
  const url = input.url?.trim();

  if (!url) {
    const message = normalizeMessage(input.message ?? input.summary ?? "");
    if (!message) {
      throw new Error("Provide a one-line commit message, or a summary plus a boot.dev lesson URL");
    }

    return { message, source: "custom" };
  }

  if (!input.summary?.trim()) {
    throw new Error("A summary is required when a boot.dev lesson URL is provided");
  }

  if (!input.lesson) {
    throw new Error("Lesson metadata is required when a boot.dev lesson URL is provided");
  }

  const summary = normalizeSummary(input.summary);

  return {
    message: `Ch ${input.lesson.chapter}.${input.lesson.lesson} - ${input.lesson.title}: ${summary}`,
    source: "lesson",
    chapter: input.lesson.chapter,
    lesson: input.lesson.lesson,
    title: input.lesson.title,
    course: input.lesson.course,
  };
}

async function fetchLessonHtml(uuid: string): Promise<string> {
  const response = await fetch(`${LESSON_URL}${uuid}`, {
    headers: {
      accept: "text/html",
      "user-agent": "sloperator-commit-changes/1.0",
    },
    redirect: "follow",
    signal: AbortSignal.timeout(15_000),
  });

  if (!response.ok) {
    throw new Error(`boot.dev returned HTTP ${response.status} for lesson ${uuid}`);
  }

  return response.text();
}

export async function buildCommitMessage(input: CommitMessageInput): Promise<CommitMessage> {
  const url = input.url?.trim();

  if (!url) {
    return formatCommitMessage(input);
  }

  const uuid = extractLessonUuid(url);
  const html = await fetchLessonHtml(uuid);
  const lesson = parseLessonPage(html, uuid);

  return formatCommitMessage({ ...input, url, lesson });
}

function runGit(args: string[], cwd: string): Promise<CommandResult> {
  return new Promise((resolveResult) => {
    execFile(
      "git",
      args,
      {
        cwd,
        timeout: 120_000,
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

export async function commitChanges(
  input: CommitMessageInput,
  projectRoot: string,
): Promise<CommitResult> {
  const formatted = await buildCommitMessage(input);
  const result = await runGit(["commit", "-m", formatted.message], projectRoot);

  return { ...formatted, ...result, committed: result.exitCode === 0 };
}

export default Plugin.define({
  id: "applymaxxing.commit-changes",
  setup: async (ctx) => {
    const projectRoot = ctx.location.directory;

    await ctx.tool.transform((tools) => {
      tools.add({
        name: "commit_changes",
        description:
          "Commit already-staged changes with a one-line message in this repository's format. With a boot.dev lesson URL, the message is `Ch <chapter>.<lesson> - <Lesson Title>: <summary>`. Without a URL, the supplied `message` (or `summary`) is used as-is, so it can be a conventional commit or anything else appropriate. Stage changes with `git add` first; this tool never stages or unstages files. Direct `git commit` is blocked, so always use this tool.",
        input: {
          type: "object",
          properties: {
            url: {
              type: "string",
              description:
                "Optional boot.dev lesson URL, for example https://www.boot.dev/lessons/<uuid>. A bare lesson UUID also works.",
            },
            summary: {
              type: "string",
              description:
                "One-line description appended after the lesson title. Required with a lesson URL; used as the full message when no URL and no message are supplied.",
            },
            message: {
              type: "string",
              description:
                "Full one-line commit message for changes without a lesson URL, for example `fix: correct lexer line numbering`. Ignored when url is supplied.",
            },
          },
          additionalProperties: false,
        },
        output: {
          type: "object",
          properties: {
            message: { type: "string" },
            source: { type: "string", enum: ["lesson", "custom"] },
            committed: { type: "boolean" },
            exitCode: { type: "integer" },
            stdout: { type: "string" },
            stderr: { type: "string" },
            chapter: { type: "integer" },
            lesson: { type: "integer" },
            title: { type: "string" },
            course: { type: "string" },
          },
          required: ["message", "source", "committed", "exitCode", "stdout", "stderr"],
          additionalProperties: false,
        },
        options: { codemode: false, permission: "commit_changes" },
        execute: async (input, context) => {
          const { url, summary, message } = input as {
            url?: string;
            summary?: string;
            message?: string;
          };

          await ctx.permission.assert({
            sessionID: context.sessionID,
            agent: context.agent,
            action: "commit_changes",
            resources: ["*"],
            save: ["*"],
            source: { type: "tool", messageID: context.messageID, id: context.id },
          });

          const result = await commitChanges({ url, summary, message }, projectRoot);
          return { output: result };
        },
      });
    });
  },
});
