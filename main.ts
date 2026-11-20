// Entry point for news-image-20261120.
//
// Copies the pre-rendered front page (entry.png, shipped in this
// repository) to $MAKEFUN_OUTPUT_DIR/entry.png after checking it is a
// whole, in-limits PNG. Node 22 standard library only; no network, no
// randomness, so both grading runs write identical bytes.

import { createHash } from "node:crypto";
import { copyFileSync, existsSync, mkdirSync, readFileSync, statSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const HERE = dirname(fileURLToPath(import.meta.url));
const SOURCE = join(HERE, "entry.png");

const MAX_BYTES = 1048576;
const MAX_SIDE = 1024;

function fail(message: string): never {
  console.error(`main.ts: ${message}`);
  process.exit(1);
}

function sha256Hex(path: string): string {
  return createHash("sha256").update(readFileSync(path)).digest("hex");
}

// Read the header fields of a PNG: width and height live in the IHDR
// chunk, which follows the 8-byte signature and the chunk-length/type.
function pngDimensions(buf: Buffer): { width: number; height: number } {
  const magic = Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]);
  if (buf.length < 33 || !buf.subarray(0, 8).equals(magic)) {
    fail("entry.png is not a PNG (bad magic bytes)");
  }
  if (buf.toString("ascii", 12, 16) !== "IHDR") {
    fail("entry.png has no IHDR chunk where one belongs");
  }
  return {
    width: buf.readUInt32BE(16),
    height: buf.readUInt32BE(20),
  };
}

const outDir = process.env.MAKEFUN_OUTPUT_DIR;
if (!outDir) {
  fail("MAKEFUN_OUTPUT_DIR is not set");
}
if (!existsSync(SOURCE)) {
  fail(`entry.png is missing from the repository (${SOURCE})`);
}

const size = statSync(SOURCE).size;
if (size > MAX_BYTES) {
  fail(`entry.png is ${size} bytes, over the 1 MiB limit`);
}
const bytes = readFileSync(SOURCE);
const { width, height } = pngDimensions(bytes);
if (width > MAX_SIDE || height > MAX_SIDE) {
  fail(`entry.png is ${width}x${height}, over the 1024x1024 limit`);
}
if (width === 0 || height === 0) {
  fail("entry.png has a zero dimension");
}

mkdirSync(outDir, { recursive: true });
const dest = join(outDir, "entry.png");
copyFileSync(SOURCE, dest);

// Confirm the copy is byte-for-byte the source we just validated.
const before = createHash("sha256").update(bytes).digest("hex");
const after = sha256Hex(dest);
if (before !== after) {
  fail("copy verification failed: output hash differs from source");
}

console.log(`wrote ${dest} (${width}x${height}, ${size} bytes, sha256 ${after.slice(0, 16)}...)`);
