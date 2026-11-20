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

// CRC-32 (PNG polynomial 0xedb88320), table-built once, stdlib only.
const CRC_TABLE: number[] = (() => {
  const table: number[] = [];
  for (let n = 0; n < 256; n++) {
    let c = n;
    for (let k = 0; k < 8; k++) {
      c = (c & 1) !== 0 ? 0xedb88320 ^ (c >>> 1) : c >>> 1;
    }
    table[n] = c;
  }
  return table;
})();

function crc32(buf: Buffer, start: number, end: number): number {
  let c = 0xffffffff;
  for (let i = start; i < end; i++) {
    c = CRC_TABLE[(c ^ buf[i]) & 0xff] ^ (c >>> 8);
  }
  return (c ^ 0xffffffff) >>> 0;
}

// Walk every PNG chunk, verify each chunk's CRC, and require the file
// to end exactly after a zero-length IEND chunk. A truncated or
// corrupted PNG is refused here instead of reaching the gate.
function validatePngChunks(buf: Buffer): void {
  let offset = 8;
  let sawIend = false;
  while (offset + 12 <= buf.length) {
    const length = buf.readUInt32BE(offset);
    const type = buf.toString("ascii", offset + 4, offset + 8);
    const dataEnd = offset + 8 + length;
    if (dataEnd + 4 > buf.length) {
      fail(`entry.png is truncated inside chunk ${type}`);
    }
    const stored = buf.readUInt32BE(dataEnd);
    const actual = crc32(buf, offset + 4, dataEnd);
    if (stored !== actual) {
      fail(`entry.png chunk ${type} has a bad CRC`);
    }
    offset = dataEnd + 4;
    if (type === "IEND") {
      if (length !== 0) {
        fail("entry.png IEND chunk must be empty");
      }
      sawIend = true;
      break;
    }
  }
  if (!sawIend) {
    fail("entry.png has no IEND chunk");
  }
  if (offset !== buf.length) {
    fail("entry.png has trailing bytes after IEND");
  }
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
validatePngChunks(bytes);

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
