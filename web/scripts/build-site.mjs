import { promises as fs } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const scriptDir = path.dirname(fileURLToPath(import.meta.url));
const webDir = path.resolve(scriptDir, "..");
const repoDir = path.resolve(webDir, "..");
const wikiDir = path.join(repoDir, "wiki");
const sourceDir = path.join(webDir, "src");
const outputDir = path.join(webDir, "dist");

const toWebPath = (value) => value.split(path.sep).join("/");

async function walk(directory) {
  const entries = await fs.readdir(directory, { withFileTypes: true });
  const nested = await Promise.all(
    entries.map(async (entry) => {
      const fullPath = path.join(directory, entry.name);
      return entry.isDirectory() ? walk(fullPath) : [fullPath];
    }),
  );
  return nested.flat();
}

function cleanInlineMarkdown(value) {
  return value
    .replace(/\[\[([^\]|]+)(?:\|([^\]]+))?\]\]/g, (_, target, label) => label || target)
    .replace(/!\[[^\]]*\]\([^)]*\)/g, "")
    .replace(/\[([^\]]+)\]\([^)]*\)/g, "$1")
    .replace(/[*_`>#~-]/g, "")
    .replace(/\s+/g, " ")
    .trim();
}

function extractTitle(markdown, fallback) {
  const match = markdown.match(/^#\s+(.+)$/m);
  return match ? cleanInlineMarkdown(match[1]) : fallback;
}

function extractSummary(markdown) {
  const lines = markdown.split(/\r?\n/);
  const paragraphs = [];
  let current = [];

  const flush = () => {
    if (!current.length) return;
    const text = cleanInlineMarkdown(current.join(" "));
    if (text.length >= 24) paragraphs.push(text);
    current = [];
  };

  for (const line of lines) {
    const trimmed = line.trim();
    if (
      !trimmed ||
      /^#{1,6}\s/.test(trimmed) ||
      /^>/.test(trimmed) ||
      /^---+$/.test(trimmed) ||
      /^\|/.test(trimmed) ||
      /^[-*+]\s/.test(trimmed) ||
      /^\d+\.\s/.test(trimmed) ||
      /^```/.test(trimmed)
    ) {
      flush();
      continue;
    }
    current.push(trimmed);
    if (current.join(" ").length > 240) flush();
  }
  flush();
  const summary = paragraphs[0] || "산림경영 실무 판단에 필요한 기준과 근거를 정리한 문서입니다.";
  return summary.length > 190 ? `${summary.slice(0, 187)}…` : summary;
}

function extractHeadings(markdown) {
  return [...markdown.matchAll(/^#{2,4}\s+(.+)$/gm)]
    .map((match) => cleanInlineMarkdown(match[1]))
    .filter(Boolean)
    .slice(0, 24);
}

function categoryFor(relativePath) {
  const segments = relativePath.split("/");
  return segments.length > 1 ? segments[0] : "운영";
}

async function buildIndex() {
  const indexMarkdown = await fs.readFile(path.join(wikiDir, "index.md"), "utf8");
  const indexOrder = new Map();
  for (const match of indexMarkdown.matchAll(/\]\(([^)]+\.md)(?:#[^)]*)?\)/g)) {
    const linkedPath = match[1].replace(/^\.\//, "").replaceAll("\\", "/");
    if (!indexOrder.has(linkedPath)) indexOrder.set(linkedPath, indexOrder.size);
  }

  const files = (await walk(wikiDir))
    .filter((file) => file.toLowerCase().endsWith(".md"))
    .filter((file) => !["index.md", "log.md"].includes(toWebPath(path.relative(wikiDir, file)).toLowerCase()))
    .sort((a, b) => a.localeCompare(b, "ko"));

  const documents = await Promise.all(
    files.map(async (file) => {
      const markdown = await fs.readFile(file, "utf8");
      const relativePath = toWebPath(path.relative(wikiDir, file));
      const fallback = path.basename(file, path.extname(file)).replaceAll("_", " ");
      return {
        id: relativePath.replace(/\.md$/i, ""),
        path: relativePath,
        title: extractTitle(markdown, fallback),
        category: categoryFor(relativePath),
        summary: extractSummary(markdown),
        headings: extractHeadings(markdown),
        rank: indexOrder.get(relativePath) ?? 999999,
        markdown,
      };
    }),
  );

  documents.sort((a, b) => a.rank - b.rank || a.title.localeCompare(b.title, "ko"));

  const categories = documents.reduce((result, document) => {
    result[document.category] = (result[document.category] || 0) + 1;
    return result;
  }, {});

  return {
    generatedAt: new Date().toISOString(),
    source: "https://github.com/chinguli4/FM-WIKI",
    total: documents.length,
    categories,
    documents,
  };
}

async function copySourceFiles() {
  const files = await walk(sourceDir);
  for (const file of files) {
    const relativePath = path.relative(sourceDir, file);
    const destination = path.join(outputDir, relativePath);
    await fs.mkdir(path.dirname(destination), { recursive: true });
    await fs.copyFile(file, destination);
  }
}

await fs.rm(outputDir, { recursive: true, force: true });
await fs.mkdir(path.join(outputDir, "data"), { recursive: true });
await copySourceFiles();

const index = await buildIndex();
await fs.writeFile(
  path.join(outputDir, "data", "wiki.json"),
  JSON.stringify(index),
  "utf8",
);

console.log(`산림경영 Wiki 웹 인덱스 생성 완료: ${index.total}개 문서`);
