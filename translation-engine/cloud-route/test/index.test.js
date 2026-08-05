import assert from "node:assert/strict";
import test from "node:test";

import worker from "../src/index.js";

const ARM_PATH =
  "/v1/translation/1.0.0/assets/macos/arm64/apaper-translation-engine-1.0.0-macos-arm64.tar.gz";
const INTEL_PATH =
  "/v1/translation/1.0.0/assets/macos/x86_64/apaper-translation-engine-1.0.0-macos-x86_64.tar.gz";

for (const [architecture, path] of [
  ["arm64", ARM_PATH],
  ["x86_64", INTEL_PATH],
]) {
  for (const method of ["GET", "HEAD"]) {
    test(`${method} ${architecture} redirects only to the immutable Release asset`, async () => {
      const response = await worker.fetch(
        new Request(`https://cloud.apaper.ai${path}`, { method }),
      );
      assert.equal(response.status, 307);
      assert.equal(
        response.headers.get("location"),
        `https://github.com/YociLam/aPaper-Cloud/releases/download/translation-engine-v1.0.0/apaper-translation-engine-1.0.0-macos-${architecture}.tar.gz`,
      );
    });
  }
}

test("unknown, queried, and mutating requests cannot use the asset route", async () => {
  const unknown = await worker.fetch(
    new Request("https://cloud.apaper.ai/v1/translation/1.0.0/assets/macos/arm64/unknown"),
  );
  const queried = await worker.fetch(
    new Request(`https://cloud.apaper.ai${ARM_PATH}?target=other`),
  );
  const post = await worker.fetch(
    new Request(`https://cloud.apaper.ai${ARM_PATH}`, { method: "POST" }),
  );
  assert.equal(unknown.status, 404);
  assert.equal(queried.status, 404);
  assert.equal(post.status, 405);
  assert.equal(post.headers.get("allow"), "GET, HEAD");
});
